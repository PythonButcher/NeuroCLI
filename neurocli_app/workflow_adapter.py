"""Helpers that map the Textual UI onto the shared workflow contract."""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from neurocli_core.workflow_service import (
    AIWorkflowRequest,
    AIWorkflowResponse,
    AIWorkflowStreamEvent,
    build_ai_workflow_request,
    stream_ai_workflow,
)


def parse_model_options(raw_text: str) -> dict[str, Any] | None:
    """Parse raw JSON from the Textual model modal into ``model_options``."""

    normalized_text = raw_text.strip()
    if not normalized_text:
        return None

    try:
        parsed = json.loads(normalized_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Model options must be a valid JSON object before sending the request."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "Model options must be a valid JSON object before sending the request."
        )

    return parsed


def build_textual_workflow_request(
    prompt: str,
    *,
    target_file: str = "",
    context_paths: Iterable[str] | None = None,
    model: str = "",
    model_options_text: str = "",
) -> AIWorkflowRequest:
    """Build the same normalized request shape used by the API-backed web flow."""

    # The Textual app stores context in a set, so we sort before building the
    # request to keep repeated runs deterministic across both app surfaces.
    normalized_context_paths = sorted(context_paths or [])

    return build_ai_workflow_request(
        prompt,
        target_file=target_file,
        context_paths=normalized_context_paths,
        model=model,
        model_options=parse_model_options(model_options_text),
    )


def run_textual_stream_workflow(
    request: AIWorkflowRequest,
    on_event: Callable[[AIWorkflowStreamEvent], None],
) -> AIWorkflowResponse:
    """Run the shared stream workflow and return the final normalized response."""

    final_response: AIWorkflowResponse | None = None

    for event in stream_ai_workflow(request):
        on_event(event)
        if event.event in {"complete", "error"} and event.response is not None:
            final_response = event.response

    if final_response is None:
        raise RuntimeError("The workflow stream ended without a final response event.")

    return final_response
