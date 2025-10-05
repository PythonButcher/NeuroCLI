"""Tests that the OpenAI integration is used by the AI service layer."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from types import SimpleNamespace

from neurocli_core import ai_services
from neurocli_core import llm_api_openai


class GetAIResponseTests(unittest.TestCase):
    """Verify that ``get_ai_response`` wires prompts to the OpenAI client."""

    def test_calls_openai_api_with_system_prompt(self) -> None:
        call_args: dict[str, str] = {}

        def fake_call(api_key: str, prompt: str) -> str:
            call_args["api_key"] = api_key
            call_args["prompt"] = prompt
            return "synthetic response"

        with patch.object(ai_services, "get_openai_api_key", return_value="test-key"), patch.object(
            ai_services, "call_openai_api", side_effect=fake_call
        ):
            original, response = ai_services.get_ai_response("Write hello world", file_path=None)

        self.assertEqual(original, "")
        self.assertEqual(response, "synthetic response")
        self.assertEqual(call_args["api_key"], "test-key")
        self.assertIn("USER PROMPT: Write hello world", call_args["prompt"])
        self.assertIn("NeuroCLI", call_args["prompt"])
        self.assertNotIn("Gemini", call_args["prompt"])


class ExtractTextSegmentsTests(unittest.TestCase):
    """Validate the OpenAI response parsing helper."""

    def test_concatenates_message_text_parts(self) -> None:
        output = [
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(type="text", text="Hello"),
                    SimpleNamespace(type="text", text=", world!"),
                ],
            ),
            SimpleNamespace(type="not-handled", content=[]),
            SimpleNamespace(
                type="message",
                content=[SimpleNamespace(type="text", text=" More text.")],
            ),
        ]

        text = llm_api_openai._extract_text_segments(output)  # type: ignore[attr-defined]

        self.assertEqual(text, "Hello, world! More text.")


if __name__ == "__main__":
    unittest.main()
