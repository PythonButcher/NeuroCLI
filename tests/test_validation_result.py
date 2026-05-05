"""Tests for the shared validation-result artifact and command policy."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from neurocli_core.validation_result import (
    ValidationCommand,
    ValidationCommandPolicy,
    run_validation_command,
)


class ValidationResultTests(unittest.TestCase):
    """Verify validation states are deterministic and policy-gated."""

    def test_validation_command_passes(self) -> None:
        policy = _policy_for(
            "unit_pass",
            sys.executable,
            "-c",
            "print('validation passed')",
        )

        result = run_validation_command("unit_pass", policy=policy)

        self.assertEqual(result.status, "passed")
        self.assertEqual(result.command_label, "unit_pass")
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(result.skipped)
        self.assertIn("validation passed", result.output_excerpt)
        self.assertIsNone(result.error_details)

    def test_validation_command_fails(self) -> None:
        policy = _policy_for(
            "unit_fail",
            sys.executable,
            "-c",
            "import sys; print('validation failed'); sys.exit(7)",
        )

        result = run_validation_command("unit_fail", policy=policy)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.exit_code, 7)
        self.assertFalse(result.skipped)
        self.assertIn("validation failed", result.output_excerpt)
        self.assertIn("non-zero", result.error_details or "")

    def test_validation_command_timeout(self) -> None:
        policy = _policy_for(
            "unit_timeout",
            sys.executable,
            "-c",
            "import time; print('before sleep'); time.sleep(1)",
            timeout_seconds=0.01,
        )

        result = run_validation_command("unit_timeout", policy=policy)

        self.assertEqual(result.status, "timeout")
        self.assertIsNone(result.exit_code)
        self.assertFalse(result.skipped)
        self.assertIn("timed out", result.error_details or "")

    def test_validation_command_skipped_without_label(self) -> None:
        result = run_validation_command("", policy=ValidationCommandPolicy())

        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.command_label, "not_run")
        self.assertTrue(result.skipped)
        self.assertEqual(result.duration_seconds, 0.0)

    def test_validation_output_is_truncated(self) -> None:
        policy = _policy_for(
            "unit_long_output",
            sys.executable,
            "-c",
            "print('x' * 80)",
        )

        result = run_validation_command("unit_long_output", policy=policy, output_excerpt_limit=12)

        self.assertEqual(result.status, "passed")
        self.assertTrue(result.output_excerpt.startswith("xxxxxxxxxxxx"))
        self.assertIn("truncated", result.output_excerpt)

    def test_validation_policy_rejects_unknown_label_without_execution(self) -> None:
        with patch("neurocli_core.validation_result.subprocess.run") as mocked_run:
            result = run_validation_command("rm_everything", policy=ValidationCommandPolicy())

        mocked_run.assert_not_called()
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.command_label, "rm_everything")
        self.assertTrue(result.skipped)
        self.assertIn("not allowed", result.error_details or "")


def _policy_for(
    label: str,
    *argv: str,
    timeout_seconds: float = 5.0,
) -> ValidationCommandPolicy:
    """Build a one-command test policy with comments kept out of test bodies."""

    return ValidationCommandPolicy(
        commands={
            label: ValidationCommand(
                label=label,
                argv=tuple(argv),
                timeout_seconds=timeout_seconds,
            )
        }
    )


if __name__ == "__main__":
    unittest.main()
