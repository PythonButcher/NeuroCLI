"""Helpers that map the Textual UI onto the shared workflow contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable

from neurocli_core.validation_result import (
    ValidationCommand,
    ValidationCommandPolicy,
    ValidationResult,
    run_validation_command,
)
from neurocli_core.workflow_service import (
    AIWorkflowRequest,
    AIWorkflowResponse,
    AIWorkflowStreamEvent,
    build_ai_workflow_request,
    stream_ai_workflow,
)


def parse_model_options(raw_text: str) -> dict[str, Any] | None:
    """Parse raw JSON from the Textual model modal into ``model_options``."""

    normalized_text = raw_text.strip()
    if not normalized_text:
        return None

    try:
        parsed = json.loads(normalized_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Model options must be a valid JSON object before sending the request."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "Model options must be a valid JSON object before sending the request."
        )

    return parsed


def build_textual_workflow_request(
    prompt: str,
    *,
    target_file: str = "",
    context_paths: Iterable[str] | None = None,
    model: str = "",
    model_options_text: str = "",
) -> AIWorkflowRequest:
    """Build the same normalized request shape used by the API-backed web flow."""

    # The Textual app stores context in a set, so we sort before building the
    # request to keep repeated runs deterministic across both app surfaces.
    normalized_context_paths = sorted(context_paths or [])

    return build_ai_workflow_request(
        prompt,
        target_file=target_file,
        context_paths=normalized_context_paths,
        model=model,
        model_options=parse_model_options(model_options_text),
    )


def run_textual_stream_workflow(
    request: AIWorkflowRequest,
    on_event: Callable[[AIWorkflowStreamEvent], None],
) -> AIWorkflowResponse:
    """Run the shared stream workflow and return the final normalized response."""

    final_response: AIWorkflowResponse | None = None

    for event in stream_ai_workflow(request):
        on_event(event)
        if event.event in {"complete", "error"} and event.response is not None:
            final_response = event.response

    if final_response is None:
        raise RuntimeError("The workflow stream ended without a final response event.")

    return final_response


def run_textual_validation(
    command_label: str = "python_unittest",
    *,
    cwd: str | Path = ".",
    target_file: str = "",
) -> ValidationResult:
    """Run a policy-approved validation label for the Textual app."""

    target_path = Path(target_file.strip()) if target_file.strip() else None
    if target_path is None:
        return run_validation_command(command_label, cwd=cwd)

    workspace_root = Path(cwd).resolve()
    resolved_target = target_path.resolve(strict=False)
    try:
        relative_target = resolved_target.relative_to(workspace_root)
    except ValueError:
        return run_validation_command("outside_workspace", policy=ValidationCommandPolicy(), cwd=cwd)

    if resolved_target.suffix != ".py":
        return run_validation_command("not_python_test", policy=ValidationCommandPolicy(), cwd=cwd)

    policy = ValidationCommandPolicy(
        commands={
            "python_unittest_target": ValidationCommand(
                label="python_unittest_target",
                argv=("python", "-m", "unittest", str(relative_target)),
                timeout_seconds=60.0,
            )
        }
    )
    return run_validation_command("python_unittest_target", policy=policy, cwd=cwd)


def format_validation_result_markdown(result: ValidationResult) -> str:
    """Render a validation result artifact for terminal display."""

    status_title = result.status.replace("_", " ").title()
    exit_code = "none" if result.exit_code is None else str(result.exit_code)
    details = result.error_details or "None"
    output = result.output_excerpt or "No output captured."

    return (
        f"### Validation: {status_title}\n\n"
        f"- Command label: `{result.command_label}`\n"
        f"- Duration: {result.duration_seconds:.2f}s\n"
        f"- Exit code: {exit_code}\n"
        f"- Skipped: {'yes' if result.skipped else 'no'}\n"
        f"- Details: {details}\n\n"
        f"#### Output excerpt\n\n"
        f"```text\n{output}\n```"
    )
