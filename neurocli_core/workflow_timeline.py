"""Redacted workflow timeline artifacts shared by NeuroCLI surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping


WorkflowTimelineEventType = Literal[
    "context_collected",
    "target_read",
    "model_request_started",
    "stream_complete",
    "proposal_created",
    "diff_generated",
    "validation_run",
    "apply_ready",
    "backup_created",
    "commit_prepared",
]
WorkflowTimelineStatus = Literal["completed", "running", "skipped", "error"]
TIMELINE_TEXT_LIMIT = 160
TIMELINE_LIST_LIMIT = 8
REDACTED_VALUE = "[redacted]"

_SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "content",
    "diff",
    "key",
    "output",
    "password",
    "prompt",
    "secret",
    "source",
    "token",
)


@dataclass(slots=True)
class WorkflowTimelineEvent:
    """A concise, redacted state marker for the safe AI workflow loop."""

    event_type: WorkflowTimelineEventType
    status: WorkflowTimelineStatus
    label: str
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event payload."""

        return asdict(self)


def build_timeline_event(
    event_type: WorkflowTimelineEventType,
    status: WorkflowTimelineStatus,
    *,
    label: str | None = None,
    summary: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> WorkflowTimelineEvent:
    """Create one timeline event with default redaction applied."""

    return WorkflowTimelineEvent(
        event_type=event_type,
        status=status,
        label=label or _default_label(event_type),
        summary=_redact_text(summary),
        metadata=redact_timeline_metadata(metadata or {}),
    )


def build_target_metadata(path: str | Path | None, *, bytes_read: int | None = None) -> dict[str, Any]:
    """Return safe target-file metadata without embedding file contents."""

    if not path:
        return {}

    target_path = Path(str(path))
    metadata: dict[str, Any] = {
        "path_label": target_path.name,
        "extension": target_path.suffix.lower(),
    }
    if bytes_read is not None:
        metadata["bytes_read"] = max(0, bytes_read)
    return metadata


def build_context_metadata(paths: list[str] | tuple[str, ...], *, collected_count: int) -> dict[str, Any]:
    """Return safe context metadata that exposes counts and labels only."""

    labels = [Path(path).name for path in paths[:TIMELINE_LIST_LIMIT]]
    metadata: dict[str, Any] = {
        "requested_count": len(paths),
        "collected_count": max(0, collected_count),
        "path_labels": labels,
    }
    if len(paths) > TIMELINE_LIST_LIMIT:
        metadata["omitted_count"] = len(paths) - TIMELINE_LIST_LIMIT
    return metadata


def build_validation_metadata(
    *,
    command_label: str,
    status: str,
    duration_seconds: float,
    exit_code: int | None,
    skipped: bool,
) -> dict[str, Any]:
    """Return safe validation metadata without subprocess output."""

    return {
        "command_label": command_label,
        "result_status": status,
        "duration_seconds": round(max(0.0, duration_seconds), 3),
        "exit_code": exit_code,
        "skipped": skipped,
    }


def redact_timeline_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Redact metadata values that could contain source, prompts, secrets, or long text."""

    redacted: dict[str, Any] = {}
    for key, value in metadata.items():
        normalized_key = str(key)
        if _is_sensitive_key(normalized_key):
            redacted[normalized_key] = REDACTED_VALUE
            continue
        redacted[normalized_key] = _redact_value(value)
    return redacted


def _default_label(event_type: WorkflowTimelineEventType) -> str:
    return event_type.replace("_", " ").title()


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in _SENSITIVE_KEY_PARTS)


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return [_redact_value(item) for item in value[:TIMELINE_LIST_LIMIT]]
    if isinstance(value, Mapping):
        return redact_timeline_metadata(value)
    return _redact_text(str(value))


def _redact_text(value: str) -> str:
    stripped = value.strip()
    if len(stripped) <= TIMELINE_TEXT_LIMIT:
        return stripped
    omitted = len(stripped) - TIMELINE_TEXT_LIMIT
    return f"{stripped[:TIMELINE_TEXT_LIMIT]}...[truncated {omitted} chars]"
