"""Tests for the shared generated-file proposal artifact."""

from __future__ import annotations

import unittest

from neurocli_core.generated_file_proposal import build_generated_file_proposal
from neurocli_core.workflow_service import AIWorkflowResponse


class GeneratedFileProposalTests(unittest.TestCase):
    def test_proposal_creation_formats_and_diffs_generated_content(self) -> None:
        proposal = build_generated_file_proposal(
            target_path="sample.py",
            original_content="print('before')\n",
            output_text="```python\nprint('after')\n```",
            formatter=lambda code, _path: code + "\n",
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.status, "ready")
        self.assertEqual(proposal.target_path, "sample.py")
        self.assertEqual(proposal.proposed_content, "print('after')")
        self.assertEqual(proposal.normalized_content, "print('after')\n")
        self.assertIn("-print('before')", proposal.diff_text)
        self.assertIn("+print('after')", proposal.diff_text)
        self.assertEqual(proposal.errors, [])

    def test_malformed_model_output_returns_error_proposal(self) -> None:
        proposal = build_generated_file_proposal(
            target_path="sample.py",
            original_content="print('before')\n",
            output_text="   ",
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.status, "error")
        self.assertEqual(proposal.proposed_content, "")
        self.assertIn("empty", proposal.errors[0])

    def test_format_failure_is_captured_without_diff(self) -> None:
        def failing_formatter(_code: str, _path: str) -> str:
            raise RuntimeError("formatter unavailable")

        proposal = build_generated_file_proposal(
            target_path="sample.py",
            original_content="print('before')\n",
            output_text="print('after')\n",
            formatter=failing_formatter,
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.status, "error")
        self.assertEqual(proposal.normalized_content, "")
        self.assertEqual(proposal.diff_text, "")
        self.assertIn("Formatting failed", proposal.errors[0])

    def test_diff_failure_is_captured_after_formatting(self) -> None:
        def failing_differ(_original: str, _new: str) -> str:
            raise RuntimeError("diff unavailable")

        proposal = build_generated_file_proposal(
            target_path="sample.py",
            original_content="print('before')\n",
            output_text="print('after')\n",
            formatter=lambda code, _path: code,
            differ=failing_differ,
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.status, "error")
        self.assertEqual(proposal.normalized_content, "print('after')\n")
        self.assertEqual(proposal.diff_text, "")
        self.assertIn("Diff generation failed", proposal.errors[0])

    def test_non_file_chat_response_has_no_proposal(self) -> None:
        response = AIWorkflowResponse(
            ok=True,
            status="completed",
            response_kind="message",
            prompt="Explain this",
            output_text="This is a chat response.",
        )

        self.assertIsNone(response.proposal)
        self.assertIsNone(response.to_dict()["proposal"])


if __name__ == "__main__":
    unittest.main()
