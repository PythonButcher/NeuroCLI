import subprocess

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
            ["ruff", "format", "-"],
            input=code_string,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If ruff is not installed or fails, return the original code
        return code_string
