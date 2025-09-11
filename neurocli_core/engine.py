import os
from neurocli_core.llm_api import call_gemini_api
from neurocli_core.config import get_gemini_api_key
from typing import Optional

def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.  
    
    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def create_context_from_path(path: str) -> str:
    """
    Creates a context string from a given file or directory path.

    Args:
        path: The path to the file or directory.

    Returns:
        The content of the file or a concatenated string of all files in the directory,
        or an error message if the path is invalid.
    """
    if not os.path.exists(path):
        return f"Error: Path not found at {path}"

    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            return f"--- CONTEXT FROM FILE: {path} ---\n\n{file_content}"
        except Exception as e:
            return f"Error reading file {path}: {e}"

    if os.path.isdir(path):
        all_contents = []
        for root, _, files in os.walk(path):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    all_contents.append(f"--- START OF {filepath} ---\n{content}\n--- END OF {filepath} ---\n\n")
                except Exception:
                    # Silently ignore files that can't be read
                    pass
        return "".join(all_contents)

    return f"Error: Path is not a file or a directory: {path}"

def get_ai_response(prompt: str, context: Optional[str] = None) -> str:
    """
    Processes a user's prompt and returns an AI-generated response,
    optionally with file content as context.
    
    Args:
        prompt: The user's input prompt.
        context: Optional context to include with the prompt.
        
    Returns:
        An AI response or an error message.
    """
    context_prompt = prompt
    if context:
        if context.startswith("Error:"):
            return context
        context_prompt = f"CONTEXT:\n---\n{context}\n---\n\nPROMPT: {prompt}"

    api_key = get_gemini_api_key()
    if not api_key:
        return "Error: Gemini API key not found. Please set it in the .env file."
    
    return call_gemini_api(api_key, context_prompt)
