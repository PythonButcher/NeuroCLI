"""Tests for the Textual app's shared workflow adapter."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from neurocli_app.workflow_adapter import (
    build_textual_workflow_request,
    parse_model_options,
    run_textual_stream_workflow,
)
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
