from neurocli_core.diff_generator import generate_diff

def test_generate_diff_no_changes() -> None:
    original = "print('hi')\n"
    diff = generate_diff(original, original)
    assert diff == "No changes proposed."


def test_generate_diff_with_changes() -> None:
    original = "print('hi')\n"
    new = "print('hello')\n"
    diff = generate_diff(original, new)
    assert diff.startswith("```diff")
    assert "-print('hi')" in diff
    assert "+print('hello')" in diff
