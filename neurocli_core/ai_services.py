"""Service helpers that build prompts and call the OpenAI backend."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from neurocli_core.config import get_openai_api_key
from neurocli_core.llm_api_openai import call_openai_api


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


def get_ai_response(prompt: str, file_path: Optional[str] = None) -> Tuple[str, str]:
    """Return the original content and OpenAI response for ``prompt``.

    Parameters
    ----------
    prompt:
        The user's prompt.
    file_path:
        Optional path to a file or directory whose content should be provided as context.
    """

    original_content = ""
    context_prompt = SYSTEM_PROMPT

    if file_path:
        context_prompt += f"\n\n{CODE_GEN_INSTRUCTIONS.strip()}"
        path = Path(file_path)
        if path.is_file():
            try:
                original_content = path.read_text(encoding="utf-8")
            except Exception as exc:  # pragma: no cover - filesystem error path
                return "", f"Error reading file {file_path}: {exc}"
            context_prompt += f"\n\nCONTEXT:\n---\n{original_content}\n---"
        else:
            context_content = create_context_from_path(path)
            if context_content.startswith("Error:"):
                return "", context_content
            context_prompt += f"\n\nCONTEXT:\n---\n{context_content}\n---"

    context_prompt += f"\n\nUSER PROMPT: {prompt}"

    api_key = get_openai_api_key()
    if not api_key:
        return "", "Error: OpenAI API key not found. Please set it in the .env file."

    response_text = call_openai_api(api_key, context_prompt)
    return original_content, response_text


def create_context_from_path(path: Path) -> str:
    """Build a concatenated context string from ``path``.

    ``path`` may be a directory or a file. Directories are traversed recursively and
    the content of readable files is concatenated together. Unreadable files are ignored.
    """

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
            if child.is_file():
                try:
                    content = child.read_text(encoding="utf-8")
                except Exception:
                    continue
                all_contents.append(
                    f"--- START OF {child} ---\n{content}\n--- END OF {child} ---\n\n"
                )
        return "".join(all_contents)

    return f"Error: Path is not a file or a directory: {path}"
