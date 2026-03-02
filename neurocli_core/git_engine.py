"""Core logic for Git operations and AI commit generation."""

import subprocess
from typing import Tuple

from neurocli_core.config import get_openai_api_key
from neurocli_core.llm_api_openai import call_openai_api


def get_staged_diff() -> Tuple[str, bool]:
    """Get the diff of staged changes.
    
    If nothing is staged, falls back to the diff of all tracked changes.
    
    Returns:
        Tuple[str, bool]: A tuple containing the diff text and a boolean
                          indicating whether it's a fallback (True if fallback,
                          False if there were staged changes).
    """
    try:
        # Check for staged changes
        staged_result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        staged_diff = staged_result.stdout.strip()
        
        if staged_diff:
            return staged_diff, False
            
        # Fallback to unstaged changes for tracked files
        unstaged_result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        # Handle the case where the fallback reading thread somehow still fails
        unstaged_diff = unstaged_result.stdout.strip() if unstaged_result.stdout else ""
        
        return unstaged_diff, True

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git diff failed: {e.stderr}") from e


def generate_commit_message(diff_text: str) -> str:
    """Generate a Conventional Commit message using AI based on a diff.
    
    Args:
        diff_text: The output from `git diff`.
        
    Returns:
        str: The generated commit message.
    """
    if not diff_text:
        return "No changes detected to commit."

    prompt = (
        "You are an expert developer. Generate a concise Conventional Commit message "
        "for the following diff. Only return the commit message text. Do not use Markdown "
        "code blocks around it. Do not include introductory text.\n\n"
        f"DIFF:\n{diff_text}"
    )

    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set it in the .env file.")

    return call_openai_api(api_key, prompt).strip()


def execute_commit_and_push(commit_message: str, add_all: bool = False) -> None:
    """Commit changes with the given message and push to the remote repository.
    
    Args:
        commit_message: The commit message to use.
        add_all: If True, uses `git commit -am` to automatically stage tracked changes.
                 Otherwise, uses `git commit -m`.
    """
    try:
        commit_cmd = ["git", "commit"]
        if add_all:
            commit_cmd.append("-a")
        commit_cmd.extend(["-m", commit_message])

        # Execute commit
        commit_result = subprocess.run(
            commit_cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        
        # Execute push
        push_result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git operation failed: {e.stderr or e.stdout}") from e
