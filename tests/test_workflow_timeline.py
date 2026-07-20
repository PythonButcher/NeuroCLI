"""Tests for redacted workflow timeline artifacts."""

from __future__ import annotations

import unittest

from neurocli_core.workflow_timeline import (
    REDACTED_VALUE,
    build_context_metadata,
    build_timeline_event,
)


class WorkflowTimelineTests(unittest.TestCase):
    """Verify timeline events stay concise and do not store sensitive content."""

    def test_timeline_event_redacts_sensitive_metadata_keys(self) -> None:
        event = build_timeline_event(
            "model_request_started",
            "running",
            summary="request started",
            metadata={
                "raw_prompt": "full prompt should not be stored",
                "api_key": "secret",
                "model": "gpt-test",
            },
        )

        self.assertEqual(event.metadata["raw_prompt"], REDACTED_VALUE)
        self.assertEqual(event.metadata["api_key"], REDACTED_VALUE)
        self.assertEqual(event.metadata["model"], "gpt-test")

    def test_context_metadata_uses_labels_and_counts_only(self) -> None:
        metadata = build_context_metadata(
            ("C:/workspace/src/app.py", "C:/workspace/docs/plan.md"),
            collected_count=2,
        )

        self.assertEqual(metadata["requested_count"], 2)
        self.assertEqual(metadata["collected_count"], 2)
        self.assertEqual(metadata["path_labels"], ["app.py", "plan.md"])


if __name__ == "__main__":
    unittest.main()
