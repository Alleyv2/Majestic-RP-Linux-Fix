#!/usr/bin/env python3
"""Small, side-effect-free system dependency checker."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class MissingDependency:
    key: str
    name: str
    reason_ru: str
    reason_en: str


@dataclass(frozen=True)
class DependencyReport:
    distro: str
    missing: tuple[MissingDependency, ...]
    optional_missing: tuple[MissingDependency, ...]
    install_command: str

    @property
    def ok(self) -> bool:
        return not self.missing


DEPENDENCIES = (
    ("bash", "Bash", "Нужен для установщика", "Required by the installer"),
    ("python3", "Python 3", "Нужен для подготовки Proton", "Required to prepare Proton"),
    ("pgrep", "procps", "Нужен для безопасной проверки процессов", "Required for safe process checks"),
    ("sed", "sed", "Нужен для создания ярлыков", "Required to create launchers"),
    ("cp", "coreutils", "Нужен для резервных копий", "Required for backups"),
    ("cmp", "diffutils", "Нужен для проверки версии Proton", "Required to compare Proton versions"),
    ("steam", "Steam", "Нужен для GTA V Legacy", "Required for GTA V Legacy"),
)

OPTIONAL_DEPENDENCIES = (
    ("mangohud", "MangoHud", "Показывает FPS в игре", "Displays in-game FPS"),
)

PACKAGES = {
    "arch": {
        "bash": "bash", "python3": "python", "pgrep": "procps-ng", "sed": "sed",
        "cp": "coreutils", "cmp": "diffutils", "steam": "steam", "node": "nodejs", "npm": "npm",
    },
    "debian": {
        "bash": "bash", "python3": "python3", "pgrep": "procps", "sed": "sed",
        "cp": "coreutils", "cmp": "diffutils", "steam": "steam-installer", "node": "nodejs", "npm": "npm",
    },
    "fedora": {
        "bash": "bash", "python3": "python3", "pgrep": "procps-ng", "sed": "sed",
        "cp": "coreutils", "cmp": "diffutils", "steam": "steam", "node": "nodejs", "npm": "npm",
    },
}


def detect_distro(os_release: Path = Path("/etc/os-release")) -> str:
    values: dict[str, str] = {}
    try:
        for line in os_release.read_text(errors="replace").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"')
    except OSError:
        return "other"
    names = f"{values.get('ID', '')} {values.get('ID_LIKE', '')}".lower()
    if "arch" in names:
        return "arch"
    if any(name in names for name in ("debian", "ubuntu", "mint")):
        return "debian"
    if any(name in names for name in ("fedora", "rhel", "centos")):
        return "fedora"
    return "other"


def _found(command: str) -> bool:
    return shutil.which(command) is not None


def _missing(item: tuple[str, str, str, str]) -> MissingDependency:
    return MissingDependency(*item)


def build_install_command(distro: str, keys: list[str]) -> str:
    mapping = PACKAGES.get(distro, {})
    packages = list(dict.fromkeys(mapping.get(key, key) for key in keys))
    joined = " ".join(packages)
    if distro == "arch":
        return f"sudo pacman -S --needed {joined}"
    if distro == "debian":
        return f"sudo apt update && sudo apt install {joined}"
    if distro == "fedora":
        return f"sudo dnf install {joined}"
    return "Install these commands with your package manager: " + " ".join(keys)


def check_dependencies() -> DependencyReport:
    missing = [_missing(item) for item in DEPENDENCIES if not _found(item[0])]

    # asar is a Node.js program. Node is always required to execute it; npm is
    # needed only when asar has not been installed yet.
    local_asar = Path.home() / ".local/bin/asar"
    if not _found("node"):
        missing.append(_missing(("node", "Node.js", "Нужен для запуска asar", "Required to run asar")))
    if not _found("asar") and not local_asar.is_file() and not _found("npm"):
        missing.append(_missing(("npm", "npm", "Нужен для установки asar", "Required to install asar")))

    optional = [_missing(item) for item in OPTIONAL_DEPENDENCIES if not _found(item[0])]
    distro = detect_distro()
    command = build_install_command(distro, [item.key for item in missing]) if missing else ""
    return DependencyReport(distro, tuple(missing), tuple(optional), command)


def format_report(report: DependencyReport, language: str = "en") -> str:
    if report.ok:
        return "Все обязательные зависимости найдены." if language == "ru" else "All required dependencies are available."
    lines = ["Не найдены обязательные компоненты:" if language == "ru" else "Missing required components:"]
    for item in report.missing:
        reason = item.reason_ru if language == "ru" else item.reason_en
        lines.append(f"• {item.name} — {reason}")
    lines.extend(("", "Команда установки:" if language == "ru" else "Install command:", report.install_command))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--lang", choices=("ru", "en"), default="ru" if os.getenv("LANG", "").startswith("ru") else "en")
    args = parser.parse_args()
    report = check_dependencies()
    if args.json:
        print(json.dumps({**asdict(report), "ok": report.ok}, ensure_ascii=False, indent=2))
    else:
        print(format_report(report, args.lang))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
