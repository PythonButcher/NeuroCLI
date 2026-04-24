"""API tests for the Phase 2 FastAPI workflow integration."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api import main
from neurocli_core.workflow_service import AIWorkflowResponse, AIWorkflowStreamEvent


class PromptEndpointTests(unittest.TestCase):
    def test_prompt_endpoint_returns_standard_workflow_payload(self) -> None:
        captured_request: dict[str, object] = {}

        def fake_execute(workflow_request):
            captured_request["value"] = workflow_request
            return AIWorkflowResponse(
                ok=True,
                status="completed",
                response_kind="file_update",
                prompt=workflow_request.prompt,
                output_text="updated file",
                target_file=workflow_request.target_file,
                context_paths=list(workflow_request.context_paths),
                original_content="print('before')\n",
                model=workflow_request.model,
            )

        with tempfile.TemporaryDirectory(dir=main.WORKSPACE_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            target_file = temp_root / "sample.py"
            context_file = temp_root / "context.md"
            target_file.write_text("print('before')\n", encoding="utf-8")
            context_file.write_text("use this context", encoding="utf-8")

            payload = {
                "prompt": "Refactor the file",
                "target_file": str(target_file.relative_to(main.WORKSPACE_ROOT)),
                "context_paths": [str(context_file.relative_to(main.WORKSPACE_ROOT))],
                "model": "gpt-test",
                "model_options": {"temperature": 0.1},
            }

            with patch("api.main.execute_ai_workflow", side_effect=fake_execute):
                data = asyncio.run(main.execute_prompt(main.PromptRequest(**payload)))

        self.assertTrue(data["ok"])
        self.assertEqual(data["response_kind"], "file_update")
        self.assertEqual(data["target_file"], str(target_file.resolve()))
        self.assertEqual(data["context_paths"], [str(context_file.resolve())])
        self.assertEqual(data["model"], "gpt-test")

        workflow_request = captured_request["value"]
        self.assertEqual(workflow_request.target_file, str(target_file.resolve()))
        self.assertEqual(workflow_request.context_paths, [str(context_file.resolve())])
        self.assertEqual(workflow_request.model_options, {"temperature": 0.1})

    def test_prompt_endpoint_returns_structured_error_for_unsafe_path(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".py") as outside_file:
            data = asyncio.run(
                main.execute_prompt(
                    main.PromptRequest(prompt="Refactor the file", target_file=outside_file.name)
                )
            )

        self.assertFalse(data["ok"])
        self.assertEqual(data["status"], "error")
        self.assertIn("workspace root", data["error"])

    def test_stream_endpoint_emits_structured_json_sse_events(self) -> None:
        completed_response = AIWorkflowResponse(
            ok=True,
            status="completed",
            response_kind="message",
            prompt="Stream this",
            output_text="hello world",
            model="gpt-test",
        )
        fake_events = iter(
            [
                AIWorkflowStreamEvent(event="start"),
                AIWorkflowStreamEvent(event="delta", delta="hello "),
                AIWorkflowStreamEvent(event="complete", response=completed_response),
            ]
        )

        with patch("api.main.stream_ai_workflow", return_value=fake_events):
            response = asyncio.run(main.stream_prompt(main.PromptRequest(prompt="Stream this")))
            serialized_events = list(main._serialize_stream_events(main.PromptRequest(prompt="Stream this")))

        self.assertEqual(response.__class__.__name__, "EventSourceResponse")
        self.assertEqual([item["event"] for item in serialized_events], ["start", "delta", "complete"])
        payloads = [json.loads(item["data"]) for item in serialized_events]
        self.assertEqual(payloads[0], {"event": "start", "delta": ""})
        self.assertEqual(payloads[1], {"event": "delta", "delta": "hello "})
        self.assertEqual(payloads[2]["event"], "complete")
        self.assertEqual(payloads[2]["response"]["output_text"], "hello world")


class FileSafetyEndpointTests(unittest.TestCase):
    def test_file_endpoint_rejects_paths_outside_workspace(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt") as outside_file:
            response = asyncio.run(main.get_file_content(path=outside_file.name))

        self.assertIn("workspace root", response["error"])

    def test_apply_endpoint_rejects_paths_outside_workspace(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt") as outside_file:
            response = asyncio.run(
                main.apply_changes_endpoint(
                    main.ApplyRequest(file_path=outside_file.name, content="updated")
                )
            )

        self.assertIn("workspace root", response["error"])


if __name__ == "__main__":
    unittest.main()
