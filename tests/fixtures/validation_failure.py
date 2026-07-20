"""Intentional failing sample used to verify target-scoped validation output."""

import unittest


class ValidationFailureFixture(unittest.TestCase):
    """Provide one deterministic failure without joining normal test discovery."""

    def test_validation_failure_example(self) -> None:
        """Fail intentionally when NeuroCLI explicitly validates this fixture."""

        self.assertEqual("expected", "actual")


if __name__ == "__main__":
    unittest.main()
