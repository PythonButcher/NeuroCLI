"""Validate NeuroCLI Agent Council run folders and JSON artifacts.

This validator intentionally uses only the Python standard library. It supports
the subset of JSON Schema used by `council_output_schema.json`, which keeps the
planning workflow lightweight and avoids adding runtime project dependencies for
documentation-only checks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).with_name("council_output_schema.json")
RUNS_DIR = Path(__file__).with_name("runs")


class ValidationError(Exception):
    """Raised when a JSON artifact does not satisfy the council schema."""


def _format_path(path: list[str]) -> str:
    """Return a readable dotted path for an error location."""
    return "$" if not path else "$." + ".".join(path)


def _type_matches(value: Any, expected_type: str) -> bool:
    """Map JSON Schema primitive type names to Python runtime checks."""
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise ValidationError(f"Unsupported schema type: {expected_type}")


def validate(value: Any, schema: dict[str, Any], path: list[str] | None = None) -> None:
    """Validate a value against the schema subset used by this workflow.

    The function is recursive so nested objects and arrays produce precise
    errors. It intentionally rejects unsupported schema features instead of
    silently ignoring them, because this validator is meant to keep the council
    artifact strict.
    """
    location = path or []

    if "type" in schema and not _type_matches(value, schema["type"]):
        raise ValidationError(
            f"{_format_path(location)} expected {schema['type']}, got {type(value).__name__}"
        )

    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{_format_path(location)} expected constant {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        raise ValidationError(f"{_format_path(location)} must be one of: {allowed}")

    if isinstance(value, str) and "minLength" in schema:
        if len(value) < schema["minLength"]:
            raise ValidationError(f"{_format_path(location)} is shorter than minLength")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValidationError(f"{_format_path(location)} has fewer items than minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ValidationError(f"{_format_path(location)} has more items than maxItems")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate(item, item_schema, [*location, str(index)])

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{_format_path(location)} missing required key {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra_keys = sorted(set(value) - set(properties))
            if extra_keys:
                joined = ", ".join(repr(key) for key in extra_keys)
                raise ValidationError(f"{_format_path(location)} has unexpected keys: {joined}")

        for key, child_value in value.items():
            child_schema = properties.get(key)
            if child_schema is not None:
                validate(child_value, child_schema, [*location, key])


def load_json(path: Path) -> Any:
    """Load a JSON file and attach the file path to parse errors."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc


def is_real_run_output(path: Path) -> bool:
    """Return whether a JSON file belongs to a real council run folder."""
    try:
        path.resolve().relative_to(RUNS_DIR.resolve())
    except ValueError:
        return False
    return path.name == "output.json"


def resolve_artifact_path(path: Path) -> tuple[Path, Path | None]:
    """Return the JSON file and required README path for a provided target.

    Passing a real run folder is preferred. Passing its `output.json` still
    requires the sibling README. Passing `sample_output.json` continues to
    validate only the JSON because samples are not real subject runs.
    """
    if path.is_dir():
        artifact_path = path / "output.json"
        readme_path = path / "README.md"
        return artifact_path, readme_path

    if is_real_run_output(path):
        return path, path.with_name("README.md")

    return path, None


def validate_readme(path: Path) -> None:
    """Ensure a real council run has a useful human-readable companion note."""
    if not path.exists():
        raise ValidationError(f"{path} is required for every real council run")
    if not path.is_file():
        raise ValidationError(f"{path} must be a file")

    content = path.read_text(encoding="utf-8").strip()
    if len(content) < 200:
        raise ValidationError(f"{path} must discuss the JSON output, not be a placeholder")
    if "output.json" not in content:
        raise ValidationError(f"{path} must reference the companion output.json")


def main(argv: list[str]) -> int:
    """Validate the run folder or JSON file named on the command line."""
    if len(argv) != 2:
        print(
            "Usage: python handoff/agent_council/validate_council_output.py "
            "<run-folder|output.json>"
        )
        return 2

    artifact_path, readme_path = resolve_artifact_path(Path(argv[1]))
    schema = load_json(SCHEMA_PATH)
    artifact = load_json(artifact_path)

    try:
        if readme_path is not None:
            validate_readme(readme_path)
        validate(artifact, schema)
    except ValidationError as exc:
        print(f"INVALID: {exc}")
        return 1

    if readme_path is not None:
        print(f"VALID: {artifact_path} with {readme_path}")
    else:
        print(f"VALID: {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
