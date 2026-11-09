#!/usr/bin/env python3
"""Preserve user config while setting Majestic/Steam compatibility values."""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path


def backup(path: Path) -> None:
    if path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, path.with_name(path.name + f".mjlx-backup-{stamp}"))


def set_lines(path: Path, values: dict[str, str]) -> None:
    text = path.read_text(errors="replace") if path.exists() else ""
    lines = text.splitlines()
    found: set[str] = set()
    result: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in values:
            result.append(f'{key}="{values[key]}"')
            found.add(key)
        else:
            result.append(line)
    for key, value in values.items():
        if key not in found:
            result.append(f'{key}="{value}"')
    path.parent.mkdir(parents=True, exist_ok=True)
    backup(path)
    path.write_text("\n".join(result).rstrip() + "\n")


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    for pos in range(opening, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return pos
    raise ValueError("Unbalanced VDF braces")


def set_steam_tool(path: Path, tool: str) -> None:
    text = path.read_text(errors="replace")
    marker = '"CompatToolMapping"'
    marker_pos = text.find(marker)
    if marker_pos < 0:
        raise SystemExit("CompatToolMapping was not found in config.vdf")
    opening = text.find("{", marker_pos + len(marker))
    closing = matching_brace(text, opening)
    section = text[opening + 1 : closing]
    app_re = re.compile(r'(?ms)(^[ \t]*"271590"[ \t]*\n[ \t]*\{)(.*?)(^[ \t]*\})')
    match = app_re.search(section)
    entry = (
        '\n\t\t\t\t\t"271590"\n'
        '\t\t\t\t\t{\n'
        f'\t\t\t\t\t\t"name"\t\t"{tool}"\n'
        '\t\t\t\t\t\t"config"\t\t""\n'
        '\t\t\t\t\t\t"priority"\t\t"250"\n'
        '\t\t\t\t\t}\n\t\t\t\t'
    )
    if match:
        body = match.group(2)
        name_re = re.compile(r'("name"\s+")[^"]*(")')
        if name_re.search(body):
            body = name_re.sub(rf'\g<1>{tool}\g<2>', body, count=1)
        else:
            body = f'\n\t\t\t\t\t\t"name"\t\t"{tool}"' + body
        section = section[: match.start(2)] + body + section[match.end(2) :]
    else:
        section = section + entry
    backup(path)
    path.write_text(text[: opening + 1] + section + text[closing:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--proton")
    parser.add_argument("--prefix")
    parser.add_argument("--gta")
    parser.add_argument("--steam-config", type=Path)
    parser.add_argument("--tool")
    args = parser.parse_args()

    if args.config:
        set_lines(
            args.config,
            {
                "MAJESTIC_GPU_MODE": "nvidia",
                "MAJESTIC_STEAM_RUNTIME": "auto",
                "MAJESTIC_AUTO_DETECT": "1",
                "MAJESTIC_PERMISSIONS": "1",
                "MAJESTIC_STEAM_OVERLAY": "0",
                "GTA_WINE_DRIVE": "g",
                "STEAM_COMPAT_DATA_PATH": args.prefix,
                "GTA_PATH": args.gta,
                "PROTON_PATH": args.proton,
                "MAJESTIC_LAUNCHER_FLAGS": "--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox --disable-gpu --disable-gpu-compositing --disable-direct-composition --disable-features=DirectComposition,CalculateNativeWinOcclusion --remote-debugging-port=9222",
            },
        )
    if args.steam_config:
        set_steam_tool(args.steam_config, args.tool)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
