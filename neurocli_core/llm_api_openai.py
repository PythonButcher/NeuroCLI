"""
This module provides the interface for interacting with the OpenAI Large Language Model API.
"""

from openai import OpenAI


def call_openai_api(api_key: str, prompt: str) -> str:
    """
    Communicates with the OpenAI API to get a response from the model.

    Args:
        api_key: The API key for the OpenAI API.
        prompt: The user's prompt to send to the model.

    Returns:
        The text response from the model.
    """
    try:
        # Create a client instance with the provided API key
        client = OpenAI(api_key=api_key)

        # Call the chat completions endpoint
        response = client.chat.completions.create(
            model="gpt-4.1 mini",   # ✅ lightweight, low-latency model
            messages=[
                {"role": "system", "content": "You are NeuroCLI, an expert AI assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return f"Error: Could not retrieve response from OpenAI API. Details: {e}"
