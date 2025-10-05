"""Git integration utilities for NeuroCLI.

This module centralizes subprocess-based Git operations so they can be
reused safely by the Textual front-end.  Each helper automatically resolves
the repository root for the provided path and raises descriptive errors when
Git is unavailable.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional

__all__ = [
    "GitError",
    "GitRepositoryNotFound",
    "detect_git_root",
    "get_status_for_path",
    "apply_patch",
    "stage_paths",
    "open_in_editor",
]


class GitError(RuntimeError):
    """Base exception for Git-related failures."""


class GitRepositoryNotFound(GitError):
    """Raised when attempting to operate outside of a Git repository."""

    def __init__(self, start_path: Path) -> None:
        super().__init__(f"No Git repository found for {start_path}.")
        self.start_path = start_path


def _run_git_command(args: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess[str]:
    """Execute a Git command, returning the completed process."""

    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        check=True,
        capture_output=True,
        **kwargs,
    )


def detect_git_root(start_path: Optional[os.PathLike[str] | str] = None) -> Path:
    """Locate the Git repository root starting from ``start_path``.

    Args:
        start_path: A file or directory path used as the starting point.
            Defaults to the NeuroCLI project directory.

    Raises:
        GitRepositoryNotFound: If no repository can be found.

    Returns:
        The resolved path to the repository root.
    """

    if start_path is None:
        start_path = Path(__file__).resolve().parent.parent
    start_path = Path(start_path).resolve()

    search_path = start_path if start_path.is_dir() else start_path.parent

    try:
        result = _run_git_command(["rev-parse", "--show-toplevel"], cwd=search_path)
    except subprocess.CalledProcessError as exc:
        raise GitRepositoryNotFound(search_path) from exc

    return Path(result.stdout.strip())


def get_status_for_path(target_path: Optional[os.PathLike[str] | str] = None) -> str:
    """Return the Git status summary for ``target_path``.

    Args:
        target_path: Optional path whose status should be inspected. When
            provided, the output mirrors ``git status --short -- <path>``.

    Returns:
        A formatted status string suitable for display.
    """

    repo_root = detect_git_root(target_path)

    status_args = ["status", "--short"]
    branch_result = _run_git_command(["branch", "--show-current"], cwd=repo_root)
    branch_name = branch_result.stdout.strip() or "(detached HEAD)"

    if target_path:
        relative_path = Path(target_path).resolve().relative_to(repo_root)
        status_args.extend(["--", str(relative_path)])

    status_result = _run_git_command(status_args, cwd=repo_root)
    status_output = status_result.stdout.strip() or "Clean"

    header = f"### Git Status — {branch_name}\n"
    if target_path:
        header += f"`{relative_path}`\n\n"

    return f"{header}```\n{status_output}\n```"


def apply_patch(patch: str, *, start_path: Optional[os.PathLike[str] | str] = None) -> str:
    """Apply a unified diff to the working tree via ``git apply``.

    Args:
        patch: Unified diff text.
        start_path: Path used to resolve the repository root.

    Returns:
        A confirmation message describing the outcome.
    """

    if not patch.strip():
        raise GitError("No patch content provided.")

    repo_root = detect_git_root(start_path)

    try:
        _run_git_command(["apply", "--whitespace=nowarn"], cwd=repo_root, input=patch)
    except subprocess.CalledProcessError as exc:
        raise GitError(exc.stderr.strip() or "Failed to apply patch.") from exc

    return "Patch applied to working tree."


def stage_paths(paths: Iterable[os.PathLike[str] | str]) -> str:
    """Stage the provided paths via ``git add``.

    Args:
        paths: Iterable of file paths to stage.

    Returns:
        A confirmation message describing the staged files.
    """

    paths = list(paths)
    if not paths:
        raise GitError("No paths provided to stage.")

    repo_root = detect_git_root(paths[0])
    relative_paths = [str(Path(path).resolve().relative_to(repo_root)) for path in paths]

    try:
        _run_git_command(["add", "--", *relative_paths], cwd=repo_root)
    except subprocess.CalledProcessError as exc:
        raise GitError(exc.stderr.strip() or "Failed to stage paths.") from exc

    return "Staged: " + ", ".join(relative_paths)


def open_in_editor(target_path: os.PathLike[str] | str) -> str:
    """Open ``target_path`` in the user's ``$EDITOR``.

    Returns a status message so callers can surface the action inside the UI.
    """

    editor = os.environ.get("EDITOR")
    if not editor:
        raise GitError("$EDITOR environment variable is not set.")

    target = Path(target_path).resolve()
    subprocess.run([editor, str(target)], check=True)
    return f"Opened {target} in {editor}."
