from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dependency_check


class DependencyCheckTests(unittest.TestCase):
    def test_detects_arch_family(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            os_release = Path(temporary) / "os-release"
            os_release.write_text('ID=endeavouros\nID_LIKE="arch"\n')
            self.assertEqual(dependency_check.detect_distro(os_release), "arch")

    def test_arch_command_deduplicates_packages(self) -> None:
        command = dependency_check.build_install_command("arch", ["cp", "python3", "cp"])
        self.assertEqual(command, "sudo pacman -S --needed coreutils python")

    def test_complete_system_is_ready(self) -> None:
        with patch("dependency_check.shutil.which", return_value="/usr/bin/tool"):
            report = dependency_check.check_dependencies()
        self.assertTrue(report.ok)
        self.assertEqual(report.install_command, "")

    def test_missing_tools_have_install_hint(self) -> None:
        available = {"bash", "python3", "pgrep", "sed", "cp", "cmp", "node", "npm", "mangohud"}
        with patch("dependency_check.shutil.which", side_effect=lambda name: f"/usr/bin/{name}" if name in available else None), patch(
            "dependency_check.detect_distro", return_value="arch"
        ):
            report = dependency_check.check_dependencies()
        self.assertFalse(report.ok)
        self.assertEqual([item.key for item in report.missing], ["steam"])
        self.assertEqual(report.install_command, "sudo pacman -S --needed steam")


if __name__ == "__main__":
    unittest.main()
