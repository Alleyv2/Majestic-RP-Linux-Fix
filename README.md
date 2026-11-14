# Majestic RP Linux Fix

[![License: MIT](https://img.shields.io/badge/License-MIT-ff2e72.svg)](LICENSE)
![Linux](https://img.shields.io/badge/Linux-Arch%20%7C%20KDE-1793d1)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab)

A bilingual graphical installer, repair tool, and launcher for running Majestic RP with GTA V Legacy through Steam and Proton on Linux.

[Русская документация](README_RU.md) · [English documentation](README_EN.md)

![Majestic RP Linux Fix interface](assets/gui-ru.png)

## Highlights

- guided installation and repair from a native Qt 6 interface;
- separate patched Proton tool without modifying Proton Experimental;
- automatic checks for Steam, GTA V Legacy, Majestic, and the compatibility fix;
- shared Proton prefix for Majestic, Rockstar Launcher, and GTA V;
- bilingual Russian/English interface and KDE-friendly desktop integration;
- recoverable log clearing and sanitized log display.
- optional compact MangoHud FPS counter in the top-right corner of GTA V.

## Quick start

For most users, download `Majestic-RP-Linux-Fix-v1.2.0-linux-x86_64.tar.gz` from Releases, extract it and run:

```bash
./Majestic-RP-Linux-Fix-x86_64
```

The standalone build includes the GUI runtime and checks the remaining system dependencies before installation. Source users can still install Python 3 and PySide6, download this repository, then run:

```bash
python3 install_app.py
```

Open **Majestic RP Linux Fix** from the application menu and choose **Install or repair**. GTA V **Legacy** and Proton Experimental must already be installed through Steam.

## Project information

- [Third-party dependencies and attribution](THIRD_PARTY.md)
- [Changelog](CHANGELOG.md)
- [Architecture and distribution](ARCHITECTURE.md)
- [Security policy](SECURITY.md)

The source tree contains no vendored runner code. Standalone release binaries bundle the Python/PySide6/Qt runtime under their respective licenses; the separately licensed runner is still downloaded only after explicit consent, from a pinned commit, and verified by SHA-256.

Created by [Alley](https://github.com/Alleyv2). This is an unofficial community utility and is not affiliated with Majestic RP, Rockstar Games, Valve, or CodeWeavers.
