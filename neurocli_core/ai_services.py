# neurocli_core/ai_services.py

from neurocli_core.llm_api_openai import call_openai_api
from neurocli_core.config import get_openai_api_key
from typing import Optional, Tuple
import os

SYSTEM_PROMPT = """
You are NeuroCLI, an expert-level AI developer and assistant integrated into a command-line tool.
Your primary goal is to help with coding and software development questions.
- Act as an expert Python developer and a helpful assistant.
- Your responses should be clear, concise, and directly address the user's prompt.
"""

def get_ai_response(prompt: str, file_path: Optional[str] = None) -> Tuple[str, str]:
    """
    Processes a user's prompt and returns an AI-generated response,
    optionally with file content as context.
    """
    original_content = ""
    # Start with the base system prompt
    context_prompt = SYSTEM_PROMPT

    if file_path:
        # --- THIS IS THE NEW LOGIC ---
        # If a file is involved, add the strict rules for code generation.
        context_prompt += '''
**IMPORTANT**: You are now in "Code Generation Mode".
When a file's content is provided as context, you MUST return only the complete, modified,
and syntactically correct code for that file.
- DO NOT use Markdown code blocks (e.g., ```python ... ```).
- DO NOT add any commentary, explanations, or introductory sentences.
- Your output MUST be only the raw, valid code for the entire file.
'''
        # --- END OF NEW LOGIC ---

    if file_path:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                # MODIFIED: Append the context and prompt to the system prompt
                context_prompt += f"\n\nCONTEXT:\n---\n{original_content}\n---\n\nUSER PROMPT: {prompt}"
            except Exception as e:
                return "", f"Error reading file {file_path}: {e}"
        else:
            context_content = create_context_from_path(file_path)
            if context_content.startswith("Error:"):
                return "", context_content
            # MODIFIED: Append the context and prompt to the system prompt
            context_prompt += f"\n\nCONTEXT:\n---\n{context_content}\n---\n\nUSER PROMPT: {prompt}"
    else:
        # MODIFIED: Handle prompts without a file path
        context_prompt += f"\n\nUSER PROMPT: {prompt}"


    api_key = get_openai_api_key()
    if not api_key:
        return "", "Error: OpenAI API key not found. Please set it in the .env file."

    response_text = call_openai_api(api_key, context_prompt)
    return original_content, response_text

def create_context_from_path(path: str) -> str:
    '''
    Creates a context string from a given file or directory path.

    Args:
        path: The path to the file or directory.

    Returns:
        The content of the file or a concatenated string of all files in the directory,
        or an error message if the path is invalid.
    '''
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
                    all_contents.append(f"--- START OF {filepath} ---\n{content}\n--- END OF {filepath}---\n\n")
                except Exception:
                    # Silently ignore files that can't be read
                    pass
        return "".join(all_contents)

    return f"Error: Path is not a file or a directory: {path}"