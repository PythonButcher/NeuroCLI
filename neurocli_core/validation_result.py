"""Shared validation result artifacts and safe command policy helpers."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Mapping


ValidationStatus = Literal["passed", "failed", "timeout", "skipped", "rejected"]
DEFAULT_OUTPUT_EXCERPT_LIMIT = 2000
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True, slots=True)
class ValidationCommand:
    """A project-approved validation command selected by stable label."""

    label: str
    argv: tuple[str, ...]
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True, slots=True)
class ValidationCommandPolicy:
    """Allowlist of validation commands that may be executed."""

    commands: Mapping[str, ValidationCommand] = field(default_factory=dict)

    def resolve(self, command_label: str) -> ValidationCommand | None:
        """Return an approved command for the label, or ``None`` when rejected."""

        return self.commands.get(command_label)


@dataclass(slots=True)
class ValidationResult:
    """Deterministic validation artifact shared by all NeuroCLI surfaces."""

    status: ValidationStatus
    command_label: str
    duration_seconds: float
    exit_code: int | None = None
    skipped: bool = False
    output_excerpt: str = ""
    error_details: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for API callers."""

        return asdict(self)


def build_default_validation_policy(project_root: str | Path | None = None) -> ValidationCommandPolicy:
    """Build the explicit project validation policy.

    The built-in labels are intentionally narrow and can be extended by a
    workspace-local ``neurocli_validation.json`` file. The config file still
    maps labels to argv arrays; callers never provide raw shell text.
    """

    root = Path(project_root).resolve() if project_root is not None else Path.cwd()
    commands: dict[str, ValidationCommand] = {
        "python_unittest": ValidationCommand(
            label="python_unittest",
            argv=("python", "-m", "unittest"),
            timeout_seconds=60.0,
        ),
        "react_build": ValidationCommand(
            label="react_build",
            argv=("npm", "--prefix", "web_client", "run", "build"),
            timeout_seconds=120.0,
        ),
    }

    config_path = root / "neurocli_validation.json"
    if config_path.exists():
        commands.update(_load_configured_commands(config_path))

    return ValidationCommandPolicy(commands=commands)


def build_skipped_validation_result(
    command_label: str = "not_run",
    error_details: str | None = "Validation was not requested for this workflow response.",
) -> ValidationResult:
    """Create a skipped artifact for workflows where validation has not run."""

    return ValidationResult(
        status="skipped",
        command_label=command_label,
        duration_seconds=0.0,
        skipped=True,
        error_details=error_details,
    )


def run_validation_command(
    command_label: str | None,
    *,
    policy: ValidationCommandPolicy | None = None,
    cwd: str | Path | None = None,
    output_excerpt_limit: int = DEFAULT_OUTPUT_EXCERPT_LIMIT,
) -> ValidationResult:
    """Run an approved validation command and return a shared result artifact."""

    normalized_label = (command_label or "").strip()
    if not normalized_label:
        return build_skipped_validation_result()

    active_policy = policy or build_default_validation_policy(cwd)
    command = active_policy.resolve(normalized_label)
    if command is None:
        return ValidationResult(
            status="rejected",
            command_label=normalized_label,
            duration_seconds=0.0,
            skipped=True,
            error_details=f"Validation command '{normalized_label}' is not allowed by policy.",
        )

    if not command.argv:
        return ValidationResult(
            status="rejected",
            command_label=normalized_label,
            duration_seconds=0.0,
            skipped=True,
            error_details=f"Validation command '{normalized_label}' has no executable argv.",
        )

    start_time = time.perf_counter()
    try:
        completed = subprocess.run(
            list(command.argv),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd) if cwd is not None else None,
            shell=False,
            timeout=command.timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - start_time
        combined_output = _combine_output(exc.stdout, exc.stderr)
        return ValidationResult(
            status="timeout",
            command_label=normalized_label,
            duration_seconds=duration,
            exit_code=None,
            skipped=False,
            output_excerpt=_excerpt(combined_output, output_excerpt_limit),
            error_details=f"Validation timed out after {command.timeout_seconds:g} seconds.",
        )
    except OSError as exc:
        duration = time.perf_counter() - start_time
        return ValidationResult(
            status="failed",
            command_label=normalized_label,
            duration_seconds=duration,
            exit_code=None,
            skipped=False,
            error_details=str(exc),
        )

    duration = time.perf_counter() - start_time
    combined_output = _combine_output(completed.stdout, completed.stderr)
    return ValidationResult(
        status="passed" if completed.returncode == 0 else "failed",
        command_label=normalized_label,
        duration_seconds=duration,
        exit_code=completed.returncode,
        skipped=False,
        output_excerpt=_excerpt(combined_output, output_excerpt_limit),
        error_details=None if completed.returncode == 0 else "Validation command exited with a non-zero status.",
    )


def _load_configured_commands(config_path: Path) -> dict[str, ValidationCommand]:
    """Load project-configured validation labels from JSON."""

    raw_config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_commands = raw_config.get("commands", {})
    if not isinstance(raw_commands, dict):
        raise ValueError("neurocli_validation.json commands must be an object.")

    commands: dict[str, ValidationCommand] = {}
    for label, definition in raw_commands.items():
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Validation command labels must be non-empty strings.")
        if not isinstance(definition, dict):
            raise ValueError(f"Validation command '{label}' must be an object.")

        raw_argv = definition.get("argv")
        if not _is_safe_argv(raw_argv):
            raise ValueError(f"Validation command '{label}' must define a non-empty argv string array.")

        raw_timeout = definition.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
        timeout_seconds = float(raw_timeout)
        if timeout_seconds <= 0:
            raise ValueError(f"Validation command '{label}' timeout_seconds must be positive.")

        commands[label] = ValidationCommand(
            label=label,
            argv=tuple(raw_argv),
            timeout_seconds=timeout_seconds,
        )

    return commands


def _is_safe_argv(raw_argv: object) -> bool:
    """Return whether config argv is structured enough for shell-free execution."""

    return (
        isinstance(raw_argv, list)
        and len(raw_argv) > 0
        and all(isinstance(part, str) and part.strip() for part in raw_argv)
    )


def _combine_output(stdout: object, stderr: object) -> str:
    """Combine process streams while tolerating timeout bytes or missing values."""

    return "\n".join(part for part in (_normalize_output(stdout), _normalize_output(stderr)) if part)


def _normalize_output(value: object) -> str:
    """Normalize subprocess output values into text."""

    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _excerpt(output: str, limit: int) -> str:
    """Return a bounded output excerpt for UI display and artifact storage."""

    normalized_limit = max(0, limit)
    if len(output) <= normalized_limit:
        return output
    omitted = len(output) - normalized_limit
    return f"{output[:normalized_limit]}\n...[truncated {omitted} characters]"
