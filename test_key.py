# test_key.py

from neurocli_core.config import get_gemini_api_key

try:
    # Create a dummy .env file for the test
    with open(".env", "w") as f:
        f.write('GEMINI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"')

    print("Attempting to load API key...")
    api_key = get_gemini_api_key()

    if api_key:
        print("\nSUCCESS: API Key loaded successfully!")
        # For security, we'll only show the first and last few characters
        print(f"Key snippet: {api_key[:4]}...{api_key[-4:]}")
    else:
        # This part should not be reached if the key is in the .env
        print("\nFAILURE: get_gemini_api_key() returned nothing, but didn't crash.")

except ValueError as e:
    print(f"\nERROR: A ValueError was caught. This is expected if the key is missing.")
    print(f"Error message: {e}")
except Exception as e:
    print(f"\nUNEXPECTED ERROR: An unknown error occurred.")
    print(f"Error details: {e}")