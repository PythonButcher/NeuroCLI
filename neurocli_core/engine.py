from neurocli_core.llm_api import call_gemini_api
from neurocli_core.config import get_gemini_api_key
from typing import Optional

def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.
    
    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def read_file_content(file_path: str) -> str:
    """
    Reads the content of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The content of the file or an error message if not found.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"

def get_ai_response(prompt: str, file_path: Optional[str] = None) -> str:
    """
    Processes a user's prompt and returns an AI-generated response,
    optionally with file content as context.
    
    Args:
        prompt: The user's input prompt.
        file_path: Optional path to a file to include as context.
        
    Returns:
        An AI response or an error message.
    """
    context_prompt = prompt
    if file_path:
        file_content = read_file_content(file_path)
        if file_content.startswith("Error:"):
            return file_content
        context_prompt = f"CONTEXT:\n---\n{file_content}\n---\n\nPROMPT: {prompt}"

    api_key = get_gemini_api_key()
    if not api_key:
        return "Error: Gemini API key not found. Please set it in the .env file."
    
    return call_gemini_api(api_key, context_prompt)
