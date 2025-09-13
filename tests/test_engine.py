import os
from pathlib import Path

from neurocli_core.engine import create_context_from_path


def test_create_context_from_path_ignores_binary_and_large_files(tmp_path: Path) -> None:
    text_file = tmp_path / "file.txt"
    text_file.write_text("hello world\n")

    binary_file = tmp_path / "bin.bin"
    binary_file.write_bytes(b"\x00\x01\x02")

    large_file = tmp_path / "large.txt"
    large_file.write_text("a" * 200)

    unreadable_file = tmp_path / "secret.txt"
    os.symlink(tmp_path / "does_not_exist.txt", unreadable_file)

    result = create_context_from_path(str(tmp_path), max_file_size=100)

    assert "file.txt" in result
    assert "hello world" in result
    assert "bin.bin" not in result
    assert "large.txt" not in result
    assert "secret.txt" not in result


def test_create_context_from_path_summarize(tmp_path: Path) -> None:
    file1 = tmp_path / "file1.py"
    file1.write_text("print('hi')\n")
    file2 = tmp_path / "file2.py"
    file2.write_text("print('bye')\n")

    summary = create_context_from_path(str(tmp_path), summarize=True)

    assert "file1.py" in summary
    assert "file2.py" in summary
    assert "print('hi')" not in summary
