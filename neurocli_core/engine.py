# neurocli_core/engine.py

from neurocli_core.ai_services import get_ai_response as get_ai_response_from_service
from typing import Optional, Tuple

def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.

    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def get_ai_response(prompt: str, file_path: Optional[str] = None) -> Tuple[str, str]:
    """
    Processes a user's prompt and returns an AI-generated response,
    optionally with file content as context.
    """
    return get_ai_response_from_service(prompt, file_path)
