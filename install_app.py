#!/usr/bin/env python3
"""Install the GUI in XDG user locations and create KDE-compatible shortcuts."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
HOME = Path.home()
DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share"))
BIN_HOME = HOME / ".local/bin"
APP_HOME = DATA_HOME / "majestic-rp-linux-fix"
APPLICATIONS = DATA_HOME / "applications"


def desktop_directory() -> Path:
    try:
        result = subprocess.run(["xdg-user-dir", "DESKTOP"], text=True, capture_output=True, check=True)
        path = Path(result.stdout.strip())
        if path.is_dir():
            return path
    except (OSError, subprocess.SubprocessError):
        pass
    return HOME / "Desktop"


def copy_project() -> None:
    APP_HOME.mkdir(parents=True, exist_ok=True)
    allowed = {
        "gui.py",
        "majestic-fix.sh",
        "patch_ntdll.py",
        "configure.py",
        "download_dependency.py",
        "install_app.py",
        "compatibilitytool.vdf",
        "launch-majestic.template.sh",
        "mangohud-gta.conf",
        "majestic-rp.desktop.template",
        "README.md",
        "README_RU.md",
        "README_EN.md",
        "THIRD_PARTY.md",
        "CHANGELOG.md",
        "LICENSE",
        "ARCHITECTURE.md",
        "SECURITY.md",
    }
    for name in allowed:
        source = SOURCE / name
        if source.is_file():
            shutil.copy2(source, APP_HOME / name)
    for executable in ("gui.py", "majestic-fix.sh", "patch_ntdll.py", "configure.py", "download_dependency.py"):
        target = APP_HOME / executable
        if target.exists():
            target.chmod(0o755)


def write_launchers(create_desktop: bool) -> None:
    BIN_HOME.mkdir(parents=True, exist_ok=True)
    APPLICATIONS.mkdir(parents=True, exist_ok=True)
    wrapper = BIN_HOME / "majestic-linux-fix"
    wrapper.write_text(f'#!/bin/sh\nexec python3 "{APP_HOME / "gui.py"}" "$@"\n')
    wrapper.chmod(0o755)

    icon = DATA_HOME / "icons/majestic-rp.png"
    icon_value = str(icon) if icon.is_file() else "applications-games"
    entry = f"""[Desktop Entry]
Type=Application
Version=1.0
Name=Majestic RP Linux Fix
Name[ru]=Majestic RP Linux Fix
GenericName=Linux game installer
GenericName[ru]=Установщик и запуск игры
Comment=Install, repair and launch Majestic RP on Linux
Comment[ru]=Установка, восстановление и запуск Majestic RP в Linux
Exec={wrapper}
TryExec={wrapper}
Icon={icon_value}
Terminal=false
Categories=Game;
Keywords=GTA;Majestic;RP;Proton;Wine;
StartupNotify=true
SingleMainWindow=true
Actions=Play;Repair;

[Desktop Action Play]
Name=Launch Majestic RP
Name[ru]=Запустить Majestic RP
Exec={APP_HOME / "majestic-fix.sh"} --launch

[Desktop Action Repair]
Name=Install or repair
Name[ru]=Установить или исправить
Exec={wrapper}
"""
    installed_entry = APPLICATIONS / "majestic-linux-fix.desktop"
    installed_entry.write_text(entry)
    installed_entry.chmod(0o755)

    if create_desktop:
        desktop = desktop_directory()
        desktop.mkdir(parents=True, exist_ok=True)
        shortcut = desktop / "Majestic RP Linux Fix.desktop"
        shortcut.write_text(entry)
        shortcut.chmod(0o755)

    if shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(APPLICATIONS)], check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-desktop", action="store_true")
    args = parser.parse_args()
    copy_project()
    write_launchers(not args.no_desktop)
    print(f"Installed: {APP_HOME}")
    print(f"Launcher: {BIN_HOME / 'majestic-linux-fix'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
