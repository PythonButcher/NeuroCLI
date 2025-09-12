import difflib

def generate_diff(original_content: str, new_content: str) -> str:
    """
    Generates a diff string between two strings.

    Args:
        original_content: The original string.
        new_content: The new string.

    Returns:
        A Markdown formatted diff string, or a message if no changes are detected.
    """
    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='original',
        tofile='new',
    )
    diff_text = "".join(diff)
    if not diff_text:
        return "No changes proposed."
    return f"```diff\n{diff_text}```"
