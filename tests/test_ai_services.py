"""Unit tests for the shared NeuroCLI AI workflow contract."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from neurocli_core import ai_services
from neurocli_core.workflow_service import (
    AIWorkflowResponse,
    build_ai_workflow_request,
    execute_ai_workflow,
    stream_ai_workflow,
)


class ExecuteAIWorkflowTests(unittest.TestCase):
    """Verify the normalized sync contract used by both app surfaces."""

    def test_execute_returns_standard_message_response(self) -> None:
        call_args: dict[str, object] = {}

        def fake_call(
            api_key: str,
            prompt: str,
            *,
            model: str | None = None,
            options: dict[str, object] | None = None,
        ) -> str:
            call_args["api_key"] = api_key
            call_args["prompt"] = prompt
            call_args["model"] = model
            call_args["options"] = options
            return "synthetic response"

        request = build_ai_workflow_request("Write hello world", model_options={"temperature": 0.2})

        with patch("neurocli_core.workflow_service.get_openai_api_key", return_value="test-key"), patch(
            "neurocli_core.workflow_service.get_default_openai_model", return_value="test-model"
        ), patch("neurocli_core.workflow_service.call_openai_api", side_effect=fake_call):
            response = execute_ai_workflow(request)

        self.assertTrue(response.ok)
        self.assertEqual(response.status, "completed")
        self.assertEqual(response.response_kind, "message")
        self.assertEqual(response.output_text, "synthetic response")
        self.assertEqual(response.model, "test-model")
        self.assertEqual(call_args["api_key"], "test-key")
        self.assertIn("USER PROMPT: Write hello world", call_args["prompt"])
        self.assertEqual(call_args["options"], {"temperature": 0.2})

    def test_execute_marks_file_requests_as_file_updates_even_when_empty(self) -> None:
        captured_prompt: dict[str, str] = {}

        def fake_call(
            api_key: str,
            prompt: str,
            *,
            model: str | None = None,
            options: dict[str, object] | None = None,
        ) -> str:
            captured_prompt["value"] = prompt
            return "print('generated')\n"

        with tempfile.TemporaryDirectory() as tmp_dir:
            target_path = Path(tmp_dir) / "empty.py"
            target_path.write_text("", encoding="utf-8")

            with patch("neurocli_core.workflow_service.get_openai_api_key", return_value="test-key"), patch(
                "neurocli_core.workflow_service.call_openai_api", side_effect=fake_call
            ):
                response = execute_ai_workflow(
                    build_ai_workflow_request("Fill the file", target_file=str(target_path))
                )

        self.assertTrue(response.ok)
        self.assertEqual(response.response_kind, "file_update")
        self.assertEqual(response.original_content, "")
        self.assertEqual(response.target_file, str(target_path))
        self.assertIn("TARGET FILE CONTEXT:", captured_prompt["value"])

    def test_execute_returns_structured_error_when_key_is_missing(self) -> None:
        with patch("neurocli_core.workflow_service.get_openai_api_key", return_value=None):
            response = execute_ai_workflow(build_ai_workflow_request("Explain this code"))

        self.assertFalse(response.ok)
        self.assertEqual(response.status, "error")
        self.assertIn("OPENAI_API_KEY", response.error or "")


class StreamAIWorkflowTests(unittest.TestCase):
    """Verify that streaming uses the same prepared request contract."""

    def test_stream_emits_start_delta_and_complete_events(self) -> None:
        with patch("neurocli_core.workflow_service.get_openai_api_key", return_value="test-key"), patch(
            "neurocli_core.workflow_service.stream_openai_api",
            return_value=iter(["hello", " ", "world"]),
        ):
            events = list(stream_ai_workflow(build_ai_workflow_request("Stream a response")))

        self.assertEqual([event.event for event in events], ["start", "delta", "delta", "delta", "complete"])
        self.assertEqual(events[1].delta, "hello")
        self.assertIsNotNone(events[-1].response)
        self.assertEqual(events[-1].response.output_text, "hello world")
        self.assertEqual(events[-1].response.response_kind, "message")


class LegacyCompatibilityTests(unittest.TestCase):
    """Keep the older tuple-based helper working during the transition."""

    def test_legacy_wrapper_returns_tuple_from_standard_response(self) -> None:
        mocked_response = AIWorkflowResponse(
            ok=False,
            status="error",
            response_kind="message",
            prompt="hello",
            error="synthetic failure",
        )

        with patch("neurocli_core.ai_services.execute_ai_workflow", return_value=mocked_response):
            original_content, response_text = ai_services.get_ai_response("hello")

        self.assertEqual(original_content, "")
        self.assertEqual(response_text, "synthetic failure")


if __name__ == "__main__":
    unittest.main()
