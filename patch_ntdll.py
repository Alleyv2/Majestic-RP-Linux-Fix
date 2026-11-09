#!/usr/bin/env python3
"""Apply or verify the Wine 11 RCX syscall callback compatibility patch."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

OLD = bytes.fromhex("4c871424415348812424ffbfffff9d48cf")
NEW = bytes.fromhex("4c89d14c871424415380642401bf9d48cf")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    data = args.path.read_bytes()
    old_count = data.count(OLD)
    new_count = data.count(NEW)

    if args.check:
        if new_count == 1 and old_count == 0:
            print("PATCHED")
            return 0
        print(f"NOT_PATCHED old={old_count} new={new_count}")
        return 1

    if new_count == 1 and old_count == 0:
        print("Already patched")
        return 0
    if old_count != 1 or new_count != 0:
        raise SystemExit(f"Unexpected ntdll pattern count: old={old_count}, new={new_count}")

    backup = args.path.with_suffix(args.path.suffix + ".mjlx-original")
    if not backup.exists():
        backup.write_bytes(data)
    patched = data.replace(OLD, NEW, 1)
    args.path.write_bytes(patched)
    print("Patched:", args.path)
    print("SHA256:", hashlib.sha256(patched).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
