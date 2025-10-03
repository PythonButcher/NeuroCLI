"""Adapter functions that communicate with the OpenAI API."""

from __future__ import annotations

from typing import Iterable

from openai import OpenAI


SYSTEM_MESSAGE = "You are NeuroCLI, an expert AI assistant."


def _extract_text_segments(output: Iterable) -> str:
    """Concatenate text segments returned by the OpenAI responses API."""
    text_parts: list[str] = []
    for item in output:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", []):
            if getattr(content, "type", None) == "text":
                text_parts.append(content.text)
    return "".join(text_parts)


def call_openai_api(api_key: str, prompt: str) -> str:
    """Communicate with the OpenAI API and return the model response."""

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": SYSTEM_MESSAGE}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                },
            ],
        )
        return _extract_text_segments(response.output)
    except Exception as exc:  # pragma: no cover - defensive logging path
        print(f"An error occurred while calling the OpenAI API: {exc}")
        return f"Error: Could not retrieve response from OpenAI API. Details: {exc}"
