"""Shared service contract for NeuroCLI's main AI workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator, Literal, Mapping

from neurocli_core.config import get_default_openai_model, get_openai_api_key
from neurocli_core.generated_file_proposal import (
    GeneratedFileProposal,
    build_generated_file_proposal,
)
from neurocli_core.llm_api_openai import call_openai_api, stream_openai_api
from neurocli_core.validation_result import (
    ValidationResult,
    build_skipped_validation_result,
)
from neurocli_core.workflow_timeline import (
    WorkflowTimelineEvent,
    build_context_metadata,
    build_target_metadata,
    build_timeline_event,
)


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
    proposal: GeneratedFileProposal | None = None
    validation_result: ValidationResult | None = None
    timeline: list[WorkflowTimelineEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for API callers."""

        return asdict(self)


@dataclass(slots=True)
class AIWorkflowStreamEvent:
    """Structured event payload for stream consumers such as FastAPI SSE."""

    event: StreamEventType
    delta: str = ""
    response: AIWorkflowResponse | None = None
    timeline_event: WorkflowTimelineEvent | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event payload."""

        payload: dict[str, Any] = {"event": self.event, "delta": self.delta}
        if self.timeline_event is not None:
            payload["timeline_event"] = self.timeline_event.to_dict()
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
    timeline: list[WorkflowTimelineEvent] = field(default_factory=list)


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
            timeline=prepared.timeline,
        )

    timeline = list(prepared.timeline)
    model_request_event = build_timeline_event(
        "model_request_started",
        "running",
        summary="Model request started with redacted prompt content.",
        metadata={"model": prepared.model, "response_kind": prepared.response_kind},
    )
    timeline.append(model_request_event)

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
            timeline=timeline,
        )

    return _build_success_response(prepared, output_text, timeline=timeline)


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
                timeline=prepared.timeline,
            ),
        )
        return

    timeline = list(prepared.timeline)
    model_request_event = build_timeline_event(
        "model_request_started",
        "running",
        summary="Streaming model request started with redacted prompt content.",
        metadata={"model": prepared.model, "response_kind": prepared.response_kind},
    )
    timeline.append(model_request_event)

    yield AIWorkflowStreamEvent(event="start", timeline_event=model_request_event)

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
                timeline=timeline,
            ),
        )
        return

    stream_complete_event = build_timeline_event(
        "stream_complete",
        "completed",
        summary="Model stream completed; generated text is stored only on the workflow response.",
        metadata={"chunk_count": len(collected_chunks), "character_count": len("".join(collected_chunks))},
    )
    timeline.append(stream_complete_event)
    yield AIWorkflowStreamEvent(
        event="complete",
        response=_build_success_response(prepared, "".join(collected_chunks), timeline=timeline),
        timeline_event=stream_complete_event,
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
    timeline: list[WorkflowTimelineEvent] = []

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
                    timeline=timeline,
                )
            timeline.append(
                build_timeline_event(
                    "target_read",
                    "completed",
                    summary="Target file was read for model context; source text is not stored in the timeline.",
                    metadata=build_target_metadata(
                        normalized_request.target_file,
                        bytes_read=len(original_content.encode("utf-8")),
                    ),
                )
            )
            compiled_prompt += f"\n\n{CODE_GEN_INSTRUCTIONS.strip()}"
            compiled_prompt += f"\n\nTARGET FILE CONTEXT:\n---\n{original_content}\n---"
        else:
            context_content = create_context_from_path(target_path)
            if context_content.startswith("Error:"):
                return None, _build_error_response(
                    normalized_request,
                    context_content,
                    timeline=timeline,
                )
            timeline.append(
                build_timeline_event(
                    "target_read",
                    "completed",
                    summary="Target path context was collected; source text is not stored in the timeline.",
                    metadata=build_target_metadata(normalized_request.target_file),
                )
            )
            compiled_prompt += f"\n\nTARGET CONTEXT:\n---\n{context_content}\n---"
    else:
        timeline.append(
            build_timeline_event(
                "target_read",
                "skipped",
                summary="No target file was selected for this workflow run.",
            )
        )

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
                    timeline=timeline,
                )
            context_sections.append(context_content)
        compiled_prompt += "\n\nADDITIONAL CONTEXT FILES:\n" + "\n".join(context_sections)
        timeline.append(
            build_timeline_event(
                "context_collected",
                "completed",
                summary="Additional context was collected; file contents are excluded from the timeline.",
                metadata=build_context_metadata(
                    tuple(normalized_request.context_paths),
                    collected_count=len(context_sections),
                ),
            )
        )
    else:
        timeline.append(
            build_timeline_event(
                "context_collected",
                "completed",
                summary="No additional context paths were selected.",
                metadata=build_context_metadata((), collected_count=0),
            )
        )

    compiled_prompt += f"\n\nUSER PROMPT: {normalized_request.prompt}"
    selected_model = normalized_request.model or get_default_openai_model()

    return (
        _PreparedWorkflow(
            request=normalized_request,
            compiled_prompt=compiled_prompt,
            response_kind=response_kind,
            original_content=original_content,
            model=selected_model,
            timeline=timeline,
        ),
        None,
    )


def _build_success_response(
    prepared: _PreparedWorkflow,
    output_text: str,
    *,
    timeline: list[WorkflowTimelineEvent] | None = None,
) -> AIWorkflowResponse:
    """Create a stable success payload for sync and streaming callers."""

    proposal = None
    response_timeline = list(timeline or prepared.timeline)
    if prepared.response_kind == "file_update":
        proposal = build_generated_file_proposal(
            target_path=prepared.request.target_file,
            original_content=prepared.original_content,
            output_text=output_text,
        )
        proposal_status = proposal.status if proposal is not None else "error"
        response_timeline.append(
            build_timeline_event(
                "proposal_created",
                "completed" if proposal_status != "error" else "error",
                summary="Generated-file proposal artifact was created without storing generated content in the timeline.",
                metadata={
                    "proposal_status": proposal_status,
                    "target": build_target_metadata(prepared.request.target_file),
                },
            )
        )
        response_timeline.append(
            build_timeline_event(
                "diff_generated",
                "completed" if proposal is not None and proposal.diff_text else "skipped",
                summary="Diff availability was recorded without embedding diff text in the timeline.",
                metadata={
                    "has_diff": bool(proposal is not None and proposal.diff_text),
                    "proposal_status": proposal_status,
                },
            )
        )
        response_timeline.append(
            build_timeline_event(
                "apply_ready",
                "completed" if proposal is not None and proposal.status == "ready" else "skipped",
                summary="Apply readiness was derived from the shared proposal status.",
                metadata={"proposal_status": proposal_status},
            )
        )

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
        proposal=proposal,
        validation_result=build_skipped_validation_result(),
        timeline=response_timeline,
    )


def _build_error_response(
    request: AIWorkflowRequest,
    error: str,
    *,
    response_kind: ResponseKind = "message",
    original_content: str = "",
    model: str | None = None,
    timeline: list[WorkflowTimelineEvent] | None = None,
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
        validation_result=build_skipped_validation_result(
            error_details="Validation was skipped because the workflow did not complete."
        ),
        timeline=list(timeline or []),
    )
