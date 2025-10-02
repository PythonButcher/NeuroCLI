import os
from pathlib import Path
from dotenv import load_dotenv

# def get_gemini_api_key() -> str:
#     """Loads the Gemini API key from a .env file in the project root.

#     Raises:
#         ValueError: If the GEMINI_API_KEY is not found in the .env file.

#     Returns:
#         The Gemini API key.
#     """
#     # Correctly determine the project root by going up from the current file's directory
#     # __file__ -> config.py
#     # Path(__file__).parent -> neurocli_core
#     # Path(__file__).parent.parent -> project root (NeuroCLI)
#     project_root = Path(__file__).parent.parent
#     dotenv_path = project_root / ".env"

#     if not dotenv_path.exists():
#         raise FileNotFoundError(f".env file not found at {dotenv_path}")

#     load_dotenv(dotenv_path=dotenv_path)
    
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY not found in .env file.")
        
#     return api_key


def get_openai_api_key() -> str:
    """Loads the OpenAI API key from a .env file in the project root.

    Raises:
        ValueError: If the OPENAI_API_KEY is not found in the .env file.

    Returns:
        The OpenAI API key.
    """
    # Correctly determine the project root by going up from the current file's directory
    # __file__ -> config.py
    # Path(__file__).parent -> neurocli_core
    # Path(__file__).parent.parent -> project root (NeuroCLI)
    project_root = Path(__file__).parent.parent
    dotenv_path = project_root / ".env"

    if not dotenv_path.exists():
        raise FileNotFoundError(f".env file not found at {dotenv_path}")

    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
        
    return api_key
