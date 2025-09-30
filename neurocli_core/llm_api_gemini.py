"""
This module provides the interface for interacting with the Gemini Large Language Model API.
"""

import google.generativeai as genai
from typing import Optional

def call_gemini_api(api_key: str, prompt: str) -> str:
    """
    Communicates with the Gemini API to get a response from the model.

    Args:
        api_key: The API key for the Gemini API.
        prompt: The user's prompt to send to the model.

    Returns:
        The text response from the model.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return f"Error: Could not retrieve response from Gemini API. Details: {e}"
