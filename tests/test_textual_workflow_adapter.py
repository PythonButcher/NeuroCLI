"""Tests for the Textual app's shared workflow adapter."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from neurocli_app.workflow_adapter import (
    build_textual_workflow_request,
    format_validation_result_markdown,
    parse_model_options,
    run_textual_validation,
    run_textual_stream_workflow,
)
from neurocli_core.validation_result import ValidationCommandPolicy
from neurocli_core.validation_result import ValidationResult
from neurocli_core.workflow_service import (
    AIWorkflowResponse,
    AIWorkflowStreamEvent,
    build_ai_workflow_request,
)


class ParseModelOptionsTests(unittest.TestCase):
    def test_empty_model_options_are_treated_as_unset(self) -> None:
        self.assertIsNone(parse_model_options("   "))

    def test_model_options_must_be_a_json_object(self) -> None:
        with self.assertRaisesRegex(ValueError, "valid JSON object"):
            parse_model_options('["temperature", 0.2]')


class BuildTextualWorkflowRequestTests(unittest.TestCase):
    def test_request_uses_shared_phase_four_fields(self) -> None:
        request = build_textual_workflow_request(
            "Refactor this file",
            target_file=" sample.py ",
            context_paths={"docs/guide.md", "src/app.py"},
            model=" gpt-test ",
            model_options_text='{"temperature": 0.2, "max_tokens": 300}',
        )

        self.assertEqual(request.prompt, "Refactor this file")
        self.assertEqual(request.target_file, "sample.py")
        self.assertEqual(request.context_paths, ["docs/guide.md", "src/app.py"])
        self.assertEqual(request.model, "gpt-test")
        self.assertEqual(request.model_options, {"temperature": 0.2, "max_tokens": 300})


class RunTextualStreamWorkflowTests(unittest.TestCase):
    def test_stream_helper_returns_the_final_normalized_response(self) -> None:
        request = build_ai_workflow_request("Stream this")
        completed_response = AIWorkflowResponse(
            ok=True,
            status="completed",
            response_kind="message",
            prompt="Stream this",
            output_text="hello world",
            model="gpt-test",
        )
        seen_events: list[AIWorkflowStreamEvent] = []

        with patch(
            "neurocli_app.workflow_adapter.stream_ai_workflow",
            return_value=iter(
                [
                    AIWorkflowStreamEvent(event="start"),
                    AIWorkflowStreamEvent(event="delta", delta="hello "),
                    AIWorkflowStreamEvent(event="complete", response=completed_response),
                ]
            ),
        ):
            final_response = run_textual_stream_workflow(request, seen_events.append)

        self.assertEqual([event.event for event in seen_events], ["start", "delta", "complete"])
        self.assertEqual(final_response.output_text, "hello world")

    def test_stream_helper_requires_a_final_response_event(self) -> None:
        request = build_ai_workflow_request("Incomplete stream")

        with patch(
            "neurocli_app.workflow_adapter.stream_ai_workflow",
            return_value=iter(
                [
                    AIWorkflowStreamEvent(event="start"),
                    AIWorkflowStreamEvent(event="delta", delta="partial"),
                ]
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "final response event"):
                run_textual_stream_workflow(request, lambda _event: None)


class TextualValidationTests(unittest.TestCase):
    def test_textual_validation_runs_policy_label(self) -> None:
        expected = ValidationResult(
            status="passed",
            command_label="python_unittest",
            duration_seconds=0.1,
            exit_code=0,
            output_excerpt="OK",
        )

        with patch(
            "neurocli_app.workflow_adapter.run_validation_command",
            return_value=expected,
        ) as mocked_run:
            result = run_textual_validation()

        mocked_run.assert_called_once_with("python_unittest", cwd=".")
        self.assertEqual(result.status, "passed")

    def test_textual_validation_targets_selected_python_file(self) -> None:
        expected = ValidationResult(
            status="failed",
            command_label="python_unittest_target",
            duration_seconds=0.1,
            exit_code=1,
            output_excerpt="failed",
        )

        with patch(
            "neurocli_app.workflow_adapter.run_validation_command",
            return_value=expected,
        ) as mocked_run:
            result = run_textual_validation(target_file="tests/fixtures/validation_failure.py")

        command_label, kwargs = mocked_run.call_args.args[0], mocked_run.call_args.kwargs
        policy = kwargs["policy"]
        self.assertEqual(command_label, "python_unittest_target")
        self.assertIsInstance(policy, ValidationCommandPolicy)
        self.assertIn("python_unittest_target", policy.commands)
        command_target = Path(policy.commands["python_unittest_target"].argv[-1])
        self.assertEqual(command_target.as_posix(), "tests/fixtures/validation_failure.py")
        self.assertEqual(result.status, "failed")

    def test_validation_result_markdown_includes_core_fields(self) -> None:
        result = ValidationResult(
            status="failed",
            command_label="python_unittest",
            duration_seconds=1.25,
            exit_code=1,
            output_excerpt="failure details",
            error_details="Validation command exited with a non-zero status.",
        )

        rendered = format_validation_result_markdown(result)

        self.assertIn("Validation: Failed", rendered)
        self.assertIn("Command label: `python_unittest`", rendered)
        self.assertIn("Exit code: 1", rendered)
        self.assertIn("failure details", rendered)
