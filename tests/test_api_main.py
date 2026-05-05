"""API tests for the Phase 2 FastAPI workflow integration."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api import main
from neurocli_core.generated_file_proposal import GeneratedFileProposal
from neurocli_core.validation_result import ValidationResult
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
                proposal=GeneratedFileProposal(
                    target_path=workflow_request.target_file or "",
                    original_content="print('before')\n",
                    original_content_reference=workflow_request.target_file or "",
                    proposed_content="print('after')",
                    normalized_content="print('after')\n",
                    diff_text="```diff\n-before\n+after\n```",
                    status="ready",
                ),
                validation_result=ValidationResult(
                    status="skipped",
                    command_label="not_run",
                    duration_seconds=0.0,
                    skipped=True,
                    error_details="Validation was not requested.",
                ),
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
        self.assertEqual(data["proposal"]["status"], "ready")
        self.assertEqual(data["proposal"]["target_path"], str(target_file.resolve()))
        self.assertEqual(data["proposal"]["normalized_content"], "print('after')\n")
        self.assertEqual(data["validation_result"]["status"], "skipped")
        self.assertEqual(data["validation_result"]["command_label"], "not_run")

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
        self.assertIsNone(data["proposal"])
        self.assertEqual(data["validation_result"]["status"], "skipped")

    def test_prompt_endpoint_rejects_unsafe_context_path_before_workflow(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".md") as outside_file:
            with patch("api.main.execute_ai_workflow") as mocked_execute:
                data = asyncio.run(
                    main.execute_prompt(
                        main.PromptRequest(
                            prompt="Use unsafe context",
                            context_paths=[outside_file.name],
                        )
                    )
                )

        mocked_execute.assert_not_called()
        self.assertFalse(data["ok"])
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

    def test_validate_endpoint_exposes_policy_gated_artifact(self) -> None:
        result = ValidationResult(
            status="passed",
            command_label="python_unittest",
            duration_seconds=0.1,
            exit_code=0,
            output_excerpt="ok",
        )

        with patch("api.main.build_default_validation_policy") as mocked_policy, patch(
            "api.main.run_validation_command", return_value=result
        ) as mocked_run:
            data = asyncio.run(
                main.validate_workspace_endpoint(
                    main.ValidationRequest(command_label="python_unittest")
                )
            )

        mocked_policy.assert_called_once_with(main.WORKSPACE_ROOT)
        mocked_run.assert_called_once()
        self.assertEqual(data["status"], "passed")
        self.assertEqual(data["command_label"], "python_unittest")
        self.assertEqual(data["output_excerpt"], "ok")

    def test_validate_endpoint_targets_selected_python_file(self) -> None:
        result = ValidationResult(
            status="failed",
            command_label="python_unittest_target",
            duration_seconds=0.1,
            exit_code=1,
            output_excerpt="failed",
        )

        with tempfile.TemporaryDirectory(dir=main.WORKSPACE_ROOT) as temp_dir:
            target_file = Path(temp_dir) / "test_selected.py"
            target_file.write_text(
                "import unittest\n\n"
                "class SelectedTest(unittest.TestCase):\n"
                "    def test_failure(self):\n"
                "        self.fail('expected')\n",
                encoding="utf-8",
            )

            with patch("api.main.run_validation_command", return_value=result) as mocked_run:
                data = asyncio.run(
                    main.validate_workspace_endpoint(
                        main.ValidationRequest(
                            command_label="python_unittest",
                            target_file=str(target_file.relative_to(main.WORKSPACE_ROOT)),
                        )
                    )
                )

        command_label, kwargs = mocked_run.call_args.args[0], mocked_run.call_args.kwargs
        policy = kwargs["policy"]
        self.assertEqual(command_label, "python_unittest_target")
        self.assertIn("python_unittest_target", policy.commands)
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["command_label"], "python_unittest_target")


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
