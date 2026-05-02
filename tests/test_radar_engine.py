"""Tests for workspace Radar source filtering."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from neurocli_core.radar_engine import scan_technical_debt, scan_workspace_health


class RadarEngineExclusionTests(unittest.TestCase):
    def test_codex_temp_dependencies_are_excluded_from_radar_scans(self) -> None:
        """Radar should ignore local dependency/runtime folders created by tooling."""

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            source_file = workspace / "app.py"
            temp_dependency = workspace / ".codex_tmp_py" / "site-packages" / "vendor.py"

            source_file.write_text("# TODO first-party issue\nprint('hello')\n", encoding="utf-8")
            temp_dependency.parent.mkdir(parents=True)
            temp_dependency.write_text("# TODO dependency noise\nprint('ignore me')\n", encoding="utf-8")

            debt = scan_technical_debt(str(workspace))
            health = scan_workspace_health(str(workspace))

        self.assertEqual(len(debt), 1)
        self.assertEqual(debt[0]["file_name"], "app.py")
        self.assertEqual(health["composition"]["Python"]["loc"], 2)


if __name__ == "__main__":
    unittest.main()
