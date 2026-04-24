"""Shared service contract for NeuroCLI's main AI workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator, Literal, Mapping

from neurocli_core.config import get_default_openai_model, get_openai_api_key
from neurocli_core.llm_api_openai import call_openai_api, stream_openai_api


SYSTEM_PROMPT = """
You are NeuroCLI, an expert-level AI developer and assistant integrated into a command-line tool.
Your primary goal is to help with coding and software development questions.
- Act as an expert Python developer and a helpful assistant.
- Your responses should be clear, concise, and directly address the user's prompt.
"""

CODE_GEN_INSTRUCTIONS = """
**IMPORTANT**: You are now in "Code Generation Mode".
When a file's content is provided as context, you MUST return only the complete, modified,
and syntactically correct code for that file.
- DO NOT use Markdown code blocks (e.g., ```python ... ```).
- DO NOT add any commentary, explanations, or introductory sentences.
- Your output MUST be only the raw, valid code for the entire file.
"""

ResponseKind = Literal["message", "file_update"]
WorkflowStatus = Literal["completed", "error"]
StreamEventType = Literal["start", "delta", "complete", "error"]


@dataclass(slots=True)
class AIWorkflowRequest:
    """Normalized input contract for the shared AI workflow."""

    prompt: str
    target_file: str | None = None
    context_paths: list[str] = field(default_factory=list)
    model: str | None = None
    model_options: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AIWorkflowResponse:
    """Stable return payload for both direct and API-backed callers."""

    ok: bool
    status: WorkflowStatus
    response_kind: ResponseKind
    prompt: str
    output_text: str = ""
    target_file: str | None = None
    context_paths: list[str] = field(default_factory=list)
    original_content: str = ""
    model: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for API callers."""

        return asdict(self)


@dataclass(slots=True)
class AIWorkflowStreamEvent:
    """Structured event payload for stream consumers such as FastAPI SSE."""

    event: StreamEventType
    delta: str = ""
    response: AIWorkflowResponse | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event payload."""

        payload: dict[str, Any] = {"event": self.event, "delta": self.delta}
        if self.response is not None:
            payload["response"] = self.response.to_dict()
        return payload


@dataclass(slots=True)
class _PreparedWorkflow:
    """Internal representation shared by sync and streaming execution paths."""

    request: AIWorkflowRequest
    compiled_prompt: str
    response_kind: ResponseKind
    original_content: str
    model: str


def build_ai_workflow_request(
    prompt: str,
    *,
    target_file: str | None = None,
    context_paths: list[str] | None = None,
    model: str | None = None,
    model_options: Mapping[str, Any] | None = None,
) -> AIWorkflowRequest:
    """Construct a normalized workflow request from loose caller inputs."""

    normalized_context_paths: list[str] = []
    if context_paths:
        # Preserve order while dropping empty or duplicate entries.
        seen_paths: set[str] = set()
        for raw_path in context_paths:
            normalized_path = str(raw_path).strip()
            if not normalized_path or normalized_path in seen_paths:
                continue
            seen_paths.add(normalized_path)
            normalized_context_paths.append(normalized_path)

    return AIWorkflowRequest(
        prompt=prompt.strip(),
        target_file=target_file.strip() if target_file and target_file.strip() else None,
        context_paths=normalized_context_paths,
        model=model.strip() if model and model.strip() else None,
        model_options=dict(model_options or {}),
    )


def execute_ai_workflow(request: AIWorkflowRequest) -> AIWorkflowResponse:
    """Run the AI workflow synchronously and return a standardized payload."""

    prepared, error_response = _prepare_workflow(request)
    if error_response is not None:
        return error_response

    api_key = get_openai_api_key()
    if not api_key:
        return _build_error_response(
            prepared.request,
            "OpenAI API key not found. Please set OPENAI_API_KEY in the project .env file.",
            response_kind=prepared.response_kind,
            original_content=prepared.original_content,
            model=prepared.model,
        )

    try:
        output_text = call_openai_api(
            api_key,
            prepared.compiled_prompt,
            model=prepared.model,
            options=prepared.request.model_options,
        )
    except RuntimeError as exc:
        return _build_error_response(
            prepared.request,
            str(exc),
            response_kind=prepared.response_kind,
            original_content=prepared.original_content,
            model=prepared.model,
        )

    return _build_success_response(prepared, output_text)


def stream_ai_workflow(request: AIWorkflowRequest) -> Iterator[AIWorkflowStreamEvent]:
    """Yield structured workflow events backed by the shared prompt preparation logic."""

    prepared, error_response = _prepare_workflow(request)
    if error_response is not None:
        yield AIWorkflowStreamEvent(event="error", response=error_response)
        return

    api_key = get_openai_api_key()
    if not api_key:
        yield AIWorkflowStreamEvent(
            event="error",
            response=_build_error_response(
                prepared.request,
                "OpenAI API key not found. Please set OPENAI_API_KEY in the project .env file.",
                response_kind=prepared.response_kind,
                original_content=prepared.original_content,
                model=prepared.model,
            ),
        )
        return

    yield AIWorkflowStreamEvent(event="start")

    collected_chunks: list[str] = []
    try:
        for chunk in stream_openai_api(
            api_key,
            prepared.compiled_prompt,
            model=prepared.model,
            options=prepared.request.model_options,
        ):
            collected_chunks.append(chunk)
            yield AIWorkflowStreamEvent(event="delta", delta=chunk)
    except RuntimeError as exc:
        yield AIWorkflowStreamEvent(
            event="error",
            response=_build_error_response(
                prepared.request,
                str(exc),
                response_kind=prepared.response_kind,
                original_content=prepared.original_content,
                model=prepared.model,
            ),
        )
        return

    yield AIWorkflowStreamEvent(
        event="complete",
        response=_build_success_response(prepared, "".join(collected_chunks)),
    )


def create_context_from_path(path: Path) -> str:
    """Build a readable context string from a file or directory path."""

    if not path.exists():
        return f"Error: Path not found at {path}"

    if path.is_file():
        try:
            file_content = path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - filesystem error path
            return f"Error reading file {path}: {exc}"
        return f"--- CONTEXT FROM FILE: {path} ---\n\n{file_content}"

    if path.is_dir():
        all_contents: list[str] = []
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            try:
                content = child.read_text(encoding="utf-8")
            except Exception:
                continue
            all_contents.append(
                f"--- START OF {child} ---\n{content}\n--- END OF {child} ---\n\n"
            )
        return "".join(all_contents)

    return f"Error: Path is not a file or a directory: {path}"


def _prepare_workflow(
    request: AIWorkflowRequest,
) -> tuple[_PreparedWorkflow | None, AIWorkflowResponse | None]:
    """Resolve files, context, and model selection before execution begins."""

    normalized_request = build_ai_workflow_request(
        request.prompt,
        target_file=request.target_file,
        context_paths=request.context_paths,
        model=request.model,
        model_options=request.model_options,
    )

    if not normalized_request.prompt:
        return None, _build_error_response(
            normalized_request,
            "Prompt is required.",
        )

    compiled_prompt = SYSTEM_PROMPT
    response_kind: ResponseKind = "message"
    original_content = ""

    if normalized_request.target_file:
        target_path = Path(normalized_request.target_file)
        if target_path.is_file():
            response_kind = "file_update"
            try:
                original_content = target_path.read_text(encoding="utf-8")
            except Exception as exc:  # pragma: no cover - filesystem error path
                return None, _build_error_response(
                    normalized_request,
                    f"Error reading file {normalized_request.target_file}: {exc}",
                    response_kind=response_kind,
                )
            compiled_prompt += f"\n\n{CODE_GEN_INSTRUCTIONS.strip()}"
            compiled_prompt += f"\n\nTARGET FILE CONTEXT:\n---\n{original_content}\n---"
        else:
            context_content = create_context_from_path(target_path)
            if context_content.startswith("Error:"):
                return None, _build_error_response(
                    normalized_request,
                    context_content,
                )
            compiled_prompt += f"\n\nTARGET CONTEXT:\n---\n{context_content}\n---"

    if normalized_request.context_paths:
        context_sections: list[str] = []
        for raw_context_path in normalized_request.context_paths:
            context_content = create_context_from_path(Path(raw_context_path))
            if context_content.startswith("Error:"):
                return None, _build_error_response(
                    normalized_request,
                    context_content,
                    response_kind=response_kind,
                    original_content=original_content,
                )
            context_sections.append(context_content)
        compiled_prompt += "\n\nADDITIONAL CONTEXT FILES:\n" + "\n".join(context_sections)

    compiled_prompt += f"\n\nUSER PROMPT: {normalized_request.prompt}"
    selected_model = normalized_request.model or get_default_openai_model()

    return (
        _PreparedWorkflow(
            request=normalized_request,
            compiled_prompt=compiled_prompt,
            response_kind=response_kind,
            original_content=original_content,
            model=selected_model,
        ),
        None,
    )


def _build_success_response(
    prepared: _PreparedWorkflow,
    output_text: str,
) -> AIWorkflowResponse:
    """Create a stable success payload for sync and streaming callers."""

    return AIWorkflowResponse(
        ok=True,
        status="completed",
        response_kind=prepared.response_kind,
        prompt=prepared.request.prompt,
        output_text=output_text,
        target_file=prepared.request.target_file,
        context_paths=list(prepared.request.context_paths),
        original_content=prepared.original_content,
        model=prepared.model,
    )


def _build_error_response(
    request: AIWorkflowRequest,
    error: str,
    *,
    response_kind: ResponseKind = "message",
    original_content: str = "",
    model: str | None = None,
) -> AIWorkflowResponse:
    """Create a stable error payload without raising across UI boundaries."""

    return AIWorkflowResponse(
        ok=False,
        status="error",
        response_kind=response_kind,
        prompt=request.prompt,
        target_file=request.target_file,
        context_paths=list(request.context_paths),
        original_content=original_content,
        model=model or request.model,
        error=error,
    )
