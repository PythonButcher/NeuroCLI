"""Adapter functions that communicate with the OpenAI chat completions API."""

from __future__ import annotations

from typing import Any, Iterator, Mapping

from neurocli_core.config import DEFAULT_OPENAI_MODEL


SYSTEM_MESSAGE = "You are NeuroCLI, an expert AI assistant."


def _normalize_message_content(content: Any) -> str:
    """Collapse OpenAI message payloads into a plain string."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return "".join(text_parts)

    return ""


def _build_completion_kwargs(
    prompt: str,
    model: str | None,
    options: Mapping[str, Any] | None,
    *,
    stream: bool,
) -> dict[str, Any]:
    """Build a single Chat Completions request payload."""

    request_kwargs: dict[str, Any] = {
        "model": model or DEFAULT_OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    }
    if options:
        request_kwargs.update(dict(options))
    if stream:
        request_kwargs["stream"] = True
    return request_kwargs


def call_openai_api(
    api_key: str,
    prompt: str,
    *,
    model: str | None = None,
    options: Mapping[str, Any] | None = None,
) -> str:
    """Return the full response body for a single prompt."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            **_build_completion_kwargs(prompt, model, options, stream=False)
        )
        return _normalize_message_content(response.choices[0].message.content)
    except Exception as exc:  # pragma: no cover - depends on external API failures
        raise RuntimeError(
            f"Could not retrieve response from OpenAI API. Details: {exc}"
        ) from exc


def stream_openai_api(
    api_key: str,
    prompt: str,
    *,
    model: str | None = None,
    options: Mapping[str, Any] | None = None,
) -> Iterator[str]:
    """Yield response chunks from the OpenAI streaming API."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        stream = client.chat.completions.create(
            **_build_completion_kwargs(prompt, model, options, stream=True)
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content
    except Exception as exc:  # pragma: no cover - depends on external API failures
        raise RuntimeError(
            f"Could not stream response from OpenAI API. Details: {exc}"
        ) from exc
