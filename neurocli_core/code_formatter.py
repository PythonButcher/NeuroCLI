import subprocess
import sys

def format_python_code(code_string: str) -> str:
    """
    Formats a Python code string using ruff.

    Args:
        code_string: The Python code to format.

    Returns:
        The formatted code string, or the original string if ruff is not installed or fails.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "-"],
            input=code_string,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except FileNotFoundError:
        # Explicitly report when ruff is missing
        raise RuntimeError(
            "The 'ruff' formatter is not installed or not in PATH. "
            "Please run 'pip install ruff'."
        )
    except subprocess.CalledProcessError:
        # If ruff fails for other reasons, return the original code
        return code_string
