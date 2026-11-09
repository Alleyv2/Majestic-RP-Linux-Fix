#!/usr/bin/env python3
"""Download a pinned, separately licensed majestic-rp-linux dependency."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

COMMIT = "765b2b7e3e459ce1c7921afcd7fa0b1e8e8b3d05"
SHA256 = "cfe816e7eb979f38102aa5a26be09e7fec6ec65b4d30c55f9b4f8ca268c7049a"
URL = f"https://github.com/digitalhorizongroup/majestic-rp-linux/archive/{COMMIT}.tar.gz"


def progress(message: str) -> None:
    print(message, flush=True)


def safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    destination_real = destination.resolve()
    for member in archive.getmembers():
        target = (destination / member.name).resolve()
        if destination_real != target and destination_real not in target.parents:
            raise RuntimeError(f"Unsafe archive member: {member.name}")
    archive.extractall(destination, filter="data")


def install(destination: Path) -> None:
    if (destination / "majestic_linux" / "__main__.py").is_file():
        progress(f"READY {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="majestic-runner-") as raw_tmp:
        tmp = Path(raw_tmp)
        archive_path = tmp / "runner.tar.gz"
        progress("DOWNLOAD 0")

        def report(block: int, block_size: int, total: int) -> None:
            if total > 0:
                percent = min(100, int(block * block_size * 100 / total))
                progress(f"DOWNLOAD {percent}")

        urllib.request.urlretrieve(URL, archive_path, report)
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        if digest != SHA256:
            raise RuntimeError(f"SHA-256 mismatch: expected {SHA256}, got {digest}")
        progress("VERIFY OK")

        extracted = tmp / "extracted"
        extracted.mkdir()
        with tarfile.open(archive_path, "r:gz") as archive:
            safe_extract(archive, extracted)
        source = extracted / f"majestic-rp-linux-{COMMIT}"
        if not (source / "LICENSE").is_file() or not (source / "majestic_linux").is_dir():
            raise RuntimeError("Downloaded runner has an unexpected structure")

        staged = destination.with_name(destination.name + ".new")
        if staged.exists():
            shutil.rmtree(staged)
        shutil.copytree(source, staged)
        if destination.exists():
            backup = destination.with_name(destination.name + ".backup")
            if backup.exists():
                shutil.rmtree(backup)
            destination.replace(backup)
        staged.replace(destination)
        progress(f"READY {destination}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".local/share/majestic-rp-runner",
    )
    args = parser.parse_args()
    install(args.destination.expanduser())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
