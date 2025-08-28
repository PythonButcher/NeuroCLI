def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.
    
    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

from neurocli_core.llm_api import call_gemini_api
from neurocli_core.config import get_gemini_api_key

def get_ai_response(prompt: str) -> str:
    """Processes a user's prompt and returns an AI-generated response.
    
    Args:
        prompt: The user's input prompt.
        
    Returns:
        An AI response.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return "Error: Gemini API key not found. Please set it in the .env file."
    return call_gemini_api(api_key, prompt)