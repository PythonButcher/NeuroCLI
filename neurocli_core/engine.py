# neurocli_core/engine.py
"""Public entry points for shared NeuroCLI backend behavior."""

from __future__ import annotations

from typing import Optional, Tuple

from neurocli_core.ai_services import get_ai_response as get_ai_response_from_service
from neurocli_core.workflow_service import (
    AIWorkflowRequest,
    AIWorkflowResponse,
    AIWorkflowStreamEvent,
    build_ai_workflow_request,
    execute_ai_workflow,
    stream_ai_workflow,
)

def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.

    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def get_ai_response(
    prompt: str,
    file_path: Optional[str] = None,
    context_paths: Optional[list[str]] = None,
) -> Tuple[str, str]:
    """
    Processes a user's prompt and returns an AI-generated response,
    optionally with file content and additional context paths.
    """
    return get_ai_response_from_service(prompt, file_path, context_paths)


__all__ = [
    "AIWorkflowRequest",
    "AIWorkflowResponse",
    "AIWorkflowStreamEvent",
    "build_ai_workflow_request",
    "execute_ai_workflow",
    "get_ai_response",
    "get_greeting",
    "stream_ai_workflow",
]
