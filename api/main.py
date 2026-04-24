import json
import subprocess
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from neurocli_core.code_formatter import format_code
from neurocli_core.diff_generator import generate_diff
from neurocli_core.file_handler import create_backup
from neurocli_core.git_engine import execute_commit_and_push, get_staged_diff
from neurocli_core.radar_engine import (
    scan_recent_edits,
    scan_technical_debt,
    scan_workspace_health,
)
from neurocli_core.workflow_service import (
    AIWorkflowRequest,
    AIWorkflowResponse,
    build_ai_workflow_request,
    execute_ai_workflow,
    stream_ai_workflow,
)


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}

app = FastAPI(title="NeuroCLI API")

# The React client still runs on Vite defaults during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str
    target_file: str | None = None
    context_paths: list[str] | None = None
    model: str | None = None
    model_options: dict[str, Any] | None = None


class FormatRequest(BaseModel):
    file_path: str


class ApplyRequest(BaseModel):
    file_path: str
    content: str


class CommitRequest(BaseModel):
    message: str


def _is_within_workspace(path: Path) -> bool:
    try:
        path.relative_to(WORKSPACE_ROOT)
        return True
    except ValueError:
        return False


def _resolve_workspace_path(raw_path: str, *, must_exist: bool = True) -> Path:
    normalized = (raw_path or "").strip()
    if not normalized:
        raise ValueError("Path is required.")

    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate

    resolved = candidate.resolve(strict=False)
    if not _is_within_workspace(resolved):
        raise ValueError("Path must stay within the workspace root.")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path not found: {normalized}")

    return resolved


def _resolve_workspace_file(raw_path: str) -> Path:
    resolved = _resolve_workspace_path(raw_path)
    if not resolved.is_file():
        raise FileNotFoundError(f"File not found: {raw_path}")
    return resolved


def _build_workflow_error_response(payload: PromptRequest, error: str) -> AIWorkflowResponse:
    normalized_request = build_ai_workflow_request(
        payload.prompt,
        target_file=payload.target_file,
        context_paths=payload.context_paths,
        model=payload.model,
        model_options=payload.model_options,
    )
    return AIWorkflowResponse(
        ok=False,
        status="error",
        response_kind="message",
        prompt=normalized_request.prompt,
        target_file=normalized_request.target_file,
        context_paths=list(normalized_request.context_paths),
        model=normalized_request.model,
        error=error,
    )


def _build_safe_workflow_request(
    payload: PromptRequest,
) -> tuple[AIWorkflowRequest | None, AIWorkflowResponse | None]:
    try:
        target_file = None
        if payload.target_file:
            target_file = str(_resolve_workspace_path(payload.target_file))

        context_paths: list[str] = []
        if payload.context_paths:
            for raw_path in payload.context_paths:
                context_paths.append(str(_resolve_workspace_path(raw_path)))
    except (FileNotFoundError, ValueError) as exc:
        return None, _build_workflow_error_response(payload, str(exc))

    return (
        build_ai_workflow_request(
            payload.prompt,
            target_file=target_file,
            context_paths=context_paths,
            model=payload.model,
            model_options=payload.model_options,
        ),
        None,
    )


def get_directory_tree(path: Path) -> dict[str, Any]:
    """Recursively build a workspace-scoped directory tree structure."""

    result: dict[str, Any] = {
        "name": path.name,
        "path": str(path),
        "type": "directory",
        "children": [],
    }

    try:
        entries = sorted(path.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
        for entry in entries:
            if entry.name in EXCLUDED_DIRECTORIES:
                continue

            resolved_entry = entry.resolve(strict=False)
            if not _is_within_workspace(resolved_entry):
                continue

            if entry.is_dir():
                result["children"].append(get_directory_tree(entry))
            else:
                result["children"].append(
                    {"name": entry.name, "path": str(resolved_entry), "type": "file"}
                )
    except PermissionError:
        pass

    return result


def _get_git_status() -> tuple[str, list[str]]:
    try:
        status_result = subprocess.run(
            ["git", "status", "-s"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            cwd=WORKSPACE_ROOT,
        )
        lines = status_result.stdout.strip().splitlines()
        unsaved = [line[3:] for line in lines if len(line) > 3]

        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            encoding="utf-8",
            check=True,
            cwd=WORKSPACE_ROOT,
        )
        branch = branch_result.stdout.strip()
        return f"On branch {branch}", unsaved
    except subprocess.CalledProcessError:
        return "Not a git repository or git error.", []


def _serialize_stream_events(payload: PromptRequest) -> Iterator[dict[str, str]]:
    workflow_request, error_response = _build_safe_workflow_request(payload)
    if error_response is not None:
        error_event = {"event": "error", "delta": "", "response": error_response.to_dict()}
        yield {"event": "error", "data": json.dumps(error_event)}
        return

    # Every SSE message carries the canonical workflow event JSON as its data payload.
    for event in stream_ai_workflow(workflow_request):
        yield {"event": event.event, "data": json.dumps(event.to_dict())}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "NeuroCLI API is running. Ready to bridge to neurocli_core."}


@app.post("/execute")
async def execute_command(command: str) -> dict[str, str]:
    return {"status": "success", "command": command}


@app.post("/api/ai/prompt")
async def execute_prompt(payload: PromptRequest) -> dict[str, Any]:
    workflow_request, error_response = _build_safe_workflow_request(payload)
    if error_response is not None:
        return error_response.to_dict()
    return execute_ai_workflow(workflow_request).to_dict()


@app.post("/api/ai/stream")
async def stream_prompt(payload: PromptRequest) -> EventSourceResponse:
    return EventSourceResponse(_serialize_stream_events(payload))


@app.get("/api/radar")
async def get_radar_stats() -> dict[str, Any]:
    """Return aggregated stats from the radar engine for the current workspace."""

    health = scan_workspace_health(str(WORKSPACE_ROOT))
    debt = scan_technical_debt(str(WORKSPACE_ROOT))
    edits = scan_recent_edits(str(WORKSPACE_ROOT), max_items=20, max_days=7)

    return {"health": health, "debt": debt, "edits": edits}


@app.get("/api/files")
async def get_files() -> dict[str, Any]:
    """Return the directory structure of the current workspace root."""

    return get_directory_tree(WORKSPACE_ROOT)


@app.get("/api/git/status")
async def get_status_endpoint() -> dict[str, Any]:
    status_msg, unsaved_files = _get_git_status()
    return {"status_message": status_msg, "unsaved_files": unsaved_files}


@app.get("/api/git/diff")
async def get_diff_endpoint(path: str | None = None) -> dict[str, str]:
    _ = path
    try:
        diff_text, _is_fallback = get_staged_diff()
        return {"diffs": diff_text}
    except Exception as exc:
        return {"diffs": str(exc)}


@app.post("/api/git/commit")
async def execute_commit_endpoint(req: CommitRequest) -> dict[str, Any]:
    try:
        status_msg, unsaved_files = _get_git_status()
        _ = status_msg
        add_all = len(unsaved_files) > 0
        execute_commit_and_push(req.message, add_all=add_all)
        return {"success": True, "message": "Successfully committed and pushed"}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@app.get("/api/file")
async def get_file_content(path: str) -> dict[str, str]:
    """Read a file's content and return it."""

    try:
        resolved_path = _resolve_workspace_file(path)
        return {"content": resolved_path.read_text(encoding="utf-8")}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/api/format")
async def format_file_endpoint(req: FormatRequest) -> dict[str, Any]:
    """Format a file and return the proposed diff, mirroring the Textual flow."""

    try:
        resolved_path = _resolve_workspace_file(req.file_path)
        original_content = resolved_path.read_text(encoding="utf-8")
        formatted_content = format_code(original_content, str(resolved_path))

        if formatted_content == original_content:
            return {"status": "no_change", "message": "No formatting needed.", "diff": ""}

        return {
            "status": "changes_proposed",
            "diff": generate_diff(original_content, formatted_content),
            "proposed_content": formatted_content,
        }
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/api/apply")
async def apply_changes_endpoint(req: ApplyRequest) -> dict[str, str]:
    """Write proposed changes back to disk after creating a local backup."""

    try:
        resolved_path = _resolve_workspace_file(req.file_path)
        backup_dir = resolved_path.parent / "backups"
        create_backup(str(resolved_path), str(backup_dir))
        resolved_path.write_text(req.content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Changes applied to {resolved_path.name} successfully.",
        }
    except Exception as exc:
        return {"error": str(exc)}
