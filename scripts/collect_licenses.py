#!/usr/bin/env python3
"""Collect license files from the exact Python packages used by a build."""

from __future__ import annotations

import importlib.metadata
import shutil
import sys
from pathlib import Path


PACKAGES = ("PyInstaller",)
MARKERS = ("license", "copying", "notice")
BUNDLED_LICENSES = Path(__file__).resolve().parent.parent / "LICENSES"


def collect_package(name: str, destination: Path) -> int:
    distribution = importlib.metadata.distribution(name)
    copied = 0
    for entry in distribution.files or ():
        if not any(marker in str(entry).lower() for marker in MARKERS):
            continue
        source = Path(distribution.locate_file(entry))
        if not source.is_file():
            continue
        target = destination / name / Path(entry).name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    return copied


def collect_python(destination: Path) -> bool:
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    candidates = (
        Path(sys.base_prefix) / "LICENSE.txt",
        Path(sys.base_prefix) / "LICENSE",
        Path(sys.base_prefix) / "lib" / version / "LICENSE.txt",
        Path(f"/usr/share/doc/{version}/copyright"),
    )
    for source in candidates:
        if source.is_file():
            target = destination / "Python" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            return True
    return False


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: collect_licenses.py DESTINATION")
    destination = Path(sys.argv[1])
    if destination.exists():
        shutil.rmtree(destination)
    if not BUNDLED_LICENSES.is_dir():
        raise SystemExit(f"Bundled Qt license directory is missing: {BUNDLED_LICENSES}")
    shutil.copytree(BUNDLED_LICENSES, destination)
    missing = [name for name in PACKAGES if collect_package(name, destination) == 0]
    if not collect_python(destination):
        missing.append("Python")
    if missing:
        raise SystemExit("No license files found for: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
