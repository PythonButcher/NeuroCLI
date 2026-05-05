"""Shared generated-file proposal artifacts for NeuroCLI review flows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Literal

from neurocli_core.code_formatter import format_code, strip_markdown_blocks
from neurocli_core.diff_generator import generate_diff


ProposalStatus = Literal["ready", "no_change", "error"]


@dataclass(slots=True)
class GeneratedFileProposal:
    """Reviewable full-file proposal created from a model file-update response."""

    target_path: str
    original_content: str
    original_content_reference: str
    proposed_content: str
    normalized_content: str
    diff_text: str
    status: ProposalStatus
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable artifact for API and frontend callers."""

        return asdict(self)


def build_generated_file_proposal(
    *,
    target_path: str | None,
    original_content: str,
    output_text: str,
    formatter: Callable[[str, str], str] = format_code,
    differ: Callable[[str, str], str] = generate_diff,
) -> GeneratedFileProposal | None:
    """Build a shared review artifact for a full-file model update.

    The model is instructed to return raw file content, but this function still
    strips accidental Markdown fences and refuses blank generated content so a
    frontend cannot apply an obviously malformed model response as a file.
    """

    normalized_target_path = (target_path or "").strip()
    if not normalized_target_path:
        return None

    proposed_content = strip_markdown_blocks(output_text)
    if not proposed_content.strip():
        return GeneratedFileProposal(
            target_path=normalized_target_path,
            original_content=original_content,
            original_content_reference=normalized_target_path,
            proposed_content="",
            normalized_content="",
            diff_text="",
            status="error",
            errors=["Model output was empty after normalization."],
        )

    errors: list[str] = []
    try:
        normalized_content = formatter(proposed_content, normalized_target_path)
    except Exception as exc:
        normalized_content = ""
        errors.append(f"Formatting failed: {exc}")

    diff_text = ""
    if normalized_content:
        try:
            diff_text = differ(original_content, normalized_content)
        except Exception as exc:
            errors.append(f"Diff generation failed: {exc}")

    if errors:
        status: ProposalStatus = "error"
    elif normalized_content == original_content:
        status = "no_change"
    else:
        status = "ready"

    return GeneratedFileProposal(
        target_path=normalized_target_path,
        original_content=original_content,
        original_content_reference=normalized_target_path,
        proposed_content=proposed_content,
        normalized_content=normalized_content,
        diff_text=diff_text,
        status=status,
        errors=errors,
    )
