import subprocess
import sys
import os

def format_code(code_string: str, file_path: str) -> str:
    """
    Formats code based on file extension using standard tools.

    Args:
        code_string: The code to format.
        file_path: The path to the file (used to determine extension).

    Returns:
        The formatted code string, or the original string if the extension is unsupported or if formatting fails.
    """
    _, ext = os.path.splitext(file_path.lower())
    
    python_exts = ['.py']
    web_exts = ['.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.html', '.md']
    
    if ext in python_exts:
        cmd = [sys.executable, "-m", "ruff", "format", "-"]
        tool_name = "ruff"
        install_msg = "Please run 'pip install ruff'."
    elif ext in web_exts:
        # We use npx to run prettier. npx is generally available with Node.js installations.
        cmd = ["npx", "prettier", "--stdin-filepath", file_path]
        tool_name = "prettier"
        install_msg = "Please ensure Node.js and 'npx' are installed."
    else:
        # Unsupported extension, return original code
        return code_string

    try:
        result = subprocess.run(
            cmd,
            input=code_string,
            capture_output=True,
            text=True,
            check=True,
            shell=(os.name == "nt"),
        )
        return result.stdout
    except FileNotFoundError:
        raise RuntimeError(
            f"The '{tool_name}' formatter is not installed or not in PATH. "
            f"{install_msg}"
        )
    except subprocess.CalledProcessError:
        # If the tool fails for other reasons, return the original code
        return code_string
