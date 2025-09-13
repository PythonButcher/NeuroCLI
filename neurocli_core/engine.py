import os
from typing import Optional, Tuple

def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.  
    
    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def _is_binary_file(filepath: str) -> bool:
    """Check if a file is binary by looking for null bytes in a chunk."""
    try:
        with open(filepath, "rb") as file:
            chunk = file.read(1024)
            if b"\0" in chunk:
                return True
            # Attempt to decode to ensure it's valid text
            chunk.decode("utf-8")
    except Exception:
        return True
    return False


def create_context_from_path(
    path: str,
    *,
    max_depth: int = 5,
    max_file_size: int = 1_000_000,
    summarize: bool = False,
    _current_depth: int = 0,
) -> str:
    """Create a context string from a file or directory path.

    Args:
        path: The path to inspect.
        max_depth: Maximum directory depth to recurse into.
        max_file_size: Maximum size in bytes for files to include.
        summarize: If ``True``, only a summary of folder contents is returned.
        _current_depth: Internal counter used for recursion.

    Returns:
        A context string or an error message if the path is invalid.
    """
    if not os.path.exists(path):
        return f"Error: Path not found at {path}"

    if os.path.isfile(path):
        if os.path.getsize(path) > max_file_size or _is_binary_file(path):
            return ""
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            if summarize:
                line_count = len(content.splitlines())
                return f"{path} - {line_count} lines"
            return f"--- CONTEXT FROM FILE: {path} ---\n\n{content}"
        except Exception:
            return ""

    if os.path.isdir(path):
        if _current_depth >= max_depth:
            return ""
        entries = []
        try:
            for name in sorted(os.listdir(path)):
                file_path = os.path.join(path, name)
                entry = create_context_from_path(
                    file_path,
                    max_depth=max_depth,
                    max_file_size=max_file_size,
                    summarize=summarize,
                    _current_depth=_current_depth + 1,
                )
                if entry and not entry.startswith("Error:"):
                    if summarize and os.path.isfile(file_path):
                        entries.append(entry + "\n")
                    else:
                        entries.append(entry)
        except Exception:
            return ""
        if summarize:
            return "".join(entries)
        return "".join(entries)

    return f"Error: Path is not a file or a directory: {path}"

def get_ai_response(prompt: str, file_path: Optional[str] = None) -> Tuple[str, str]:
    """Process a user's prompt and return an AI-generated response."""
    from neurocli_core.llm_api import call_gemini_api
    from neurocli_core.config import get_gemini_api_key

    original_content = ""
    context_prompt = prompt

    if file_path:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                context_prompt = f"CONTEXT:\n---\n{original_content}\n---\n\nPROMPT: {prompt}"
            except Exception as e:
                return "", f"Error reading file {file_path}: {e}"
        else:
            # For directories, we don't have a single original content
            context_content = create_context_from_path(file_path)
            if context_content.startswith("Error:"):
                return "", context_content
            context_prompt = f"CONTEXT:\n---\n{context_content}\n---\n\nPROMPT: {prompt}"

    system_prompt = (
        "You are an AI coding assistant. Improve the provided Python code without "
        "breaking imports, dependencies, or style. Follow PEP8 and use type hints. "
        "If no improvements are needed, say 'No changes proposed'."
    )
    final_prompt = f"{system_prompt}\n\n{context_prompt}"

    api_key = get_gemini_api_key()
    if not api_key:
        return "", "Error: Gemini API key not found. Please set it in the .env file."

    response_text = call_gemini_api(api_key, final_prompt)
    return original_content, response_text
