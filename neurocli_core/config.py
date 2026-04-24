"""Configuration helpers shared across the backend surface area."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        """Fallback no-op when python-dotenv is not installed."""

        return False


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def _load_project_env() -> None:
    """Load the project ``.env`` file when it exists.

    The service layer should be able to report clean errors when configuration
    is missing, so this helper intentionally avoids raising when the file is not
    present.
    """

    project_root = Path(__file__).parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)


def get_openai_api_key() -> str | None:
    """Return the configured OpenAI API key, or ``None`` when missing."""

    _load_project_env()
    return os.getenv("OPENAI_API_KEY")


def get_default_openai_model() -> str:
    """Return the configured default model name for NeuroCLI."""

    _load_project_env()
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
