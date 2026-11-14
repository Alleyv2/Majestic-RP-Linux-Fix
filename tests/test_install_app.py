from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import install_app


class StandaloneInstallTests(unittest.TestCase):
    def test_frozen_build_installs_and_wraps_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "download" / "Majestic-RP-Linux-Fix-x86_64"
            source.parent.mkdir()
            source.write_bytes(b"standalone executable")
            app_home = root / "share" / "majestic-rp-linux-fix"
            bin_home = root / "bin"
            applications = root / "share" / "applications"
            with patch.object(install_app, "FROZEN", True), patch.object(install_app, "APP_HOME", app_home), patch.object(
                install_app, "BIN_HOME", bin_home
            ), patch.object(install_app, "APPLICATIONS", applications), patch.object(
                install_app, "DATA_HOME", root / "share"
            ), patch.object(install_app.sys, "executable", str(source)), patch(
                "install_app.shutil.which", return_value=None
            ):
                app_home.mkdir(parents=True)
                install_app.write_launchers(create_desktop=False)

            installed = app_home / "Majestic-RP-Linux-Fix"
            self.assertEqual(installed.read_bytes(), b"standalone executable")
            self.assertTrue(installed.stat().st_mode & 0o100)
            wrapper = (bin_home / "majestic-linux-fix").read_text()
            self.assertIn(str(installed), wrapper)
            self.assertNotIn("python3", wrapper)


if __name__ == "__main__":
    unittest.main()
