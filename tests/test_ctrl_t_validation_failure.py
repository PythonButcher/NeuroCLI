"""Simple intentional failure for the app validation action."""

import unittest


class CtrlTValidationFailureTest(unittest.TestCase):
    def test_validation_failure_example(self) -> None:
        self.assertEqual("expected", "actual")


if __name__ == "__main__":
    unittest.main()
