"""Regression tests for the Textual workspace reset action."""

from __future__ import annotations

import asyncio
import unittest

from textual.widgets import Input

from neurocli_app.main import NeuroApp
from neurocli_core.validation_result import build_skipped_validation_result
from neurocli_core.workflow_timeline import build_timeline_event


class TextualResetTests(unittest.IsolatedAsyncioTestCase):
    """Verify Reset clears run-scoped UI state without performing file writes."""

    async def test_reset_clears_target_and_transient_workflow_state(self) -> None:
        """Ctrl+L's action must not retain a target from the previous run."""

        app = NeuroApp()
        event_loop = asyncio.get_running_loop()
        previous_slow_callback_duration = event_loop.slow_callback_duration
        # Textual startup can exceed unittest's very low debug threshold on
        # Windows; raising it keeps normal successful test output concise.
        event_loop.slow_callback_duration = 5.0

        try:
            async with app.run_test():
                target_input = app.query_one("#file_path_input", Input)
                target_input.value = "README.md"
                app._proposed_content = "proposed"
                app._proposal_baseline_content = "original"
                app._streamed_output = "response"
                app._validation_result = build_skipped_validation_result()
                app._timeline_events = [
                    build_timeline_event("target_read", "completed")
                ]

                # Invoke the same action bound to Ctrl+L while the Textual widget
                # tree is mounted, then assert every run-scoped field is reset.
                app.action_reset_workspace()

                self.assertEqual(target_input.value, "")
                self.assertEqual(app._proposed_content, "")
                self.assertEqual(app._proposal_baseline_content, "")
                self.assertEqual(app._streamed_output, "")
                self.assertIsNone(app._validation_result)
                self.assertEqual(app._timeline_events, [])
                self.assertEqual(app._workflow_state, "Reset")
        finally:
            event_loop.slow_callback_duration = previous_slow_callback_duration


if __name__ == "__main__":
    unittest.main()
