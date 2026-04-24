"""Compatibility helpers for older callers that still expect tuple responses."""

from __future__ import annotations

from typing import Optional, Tuple

from neurocli_core.workflow_service import (
    build_ai_workflow_request,
    create_context_from_path,
    execute_ai_workflow,
)


def get_ai_response(
    prompt: str,
    file_path: Optional[str] = None,
    context_paths: Optional[list[str]] = None,
) -> Tuple[str, str]:
    """Return the legacy ``(original_content, response_text)`` tuple shape."""

    response = execute_ai_workflow(
        build_ai_workflow_request(
            prompt,
            target_file=file_path,
            context_paths=context_paths,
        )
    )
    if response.ok:
        return response.original_content, response.output_text
    return response.original_content, response.error or "Unknown AI workflow error."


__all__ = ["create_context_from_path", "get_ai_response"]
