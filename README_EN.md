# Majestic RP Linux Fix

A bilingual GUI utility for running Majestic RP with GTA V Legacy through Steam/Proton.

This repository contains only the utility's own code. The third-party runner is not bundled; its separate download occurs only after explicit user consent.

With explicit user consent, the GUI wizard can automatically download the separately licensed MIT runner from a pinned commit. The archive is SHA-256 verified and its original license is preserved in the dependency directory.

## Graphical installation

For a regular installation, download `Majestic-RP-Linux-Fix-v1.2.0-linux-x86_64.tar.gz` from Releases, extract it, and run `Majestic-RP-Linux-Fix-x86_64`. Python and PySide6 are not required to start the interface. Before setup, the application checks Steam, Python, Node.js/npm and other system components and provides a ready-to-copy install command when something is missing.

Source installation remains available:

```bash
python3 install_app.py
```

This installs the application under `~/.local/share/majestic-rp-linux-fix`, registers it in the KDE application menu, and creates a desktop shortcut. Open **Majestic RP Linux Fix** and select **Install or repair**.

## Features

- creates a separate Proton Experimental copy and leaves the original untouched;
- applies the Wine 11 compatibility fix for `ERR_FAILED_TO_INJECT` / `0xc0000409`;
- assigns the patched Proton to Steam AppID `271590`;
- keeps Majestic, Rockstar Launcher and GTA in one Proton prefix;
- launches Majestic and displays configuration and injection logs;
- backs up configuration and can disable the fix without deleting its files.
- automatically enables a compact top-right FPS counter when MangoHud is installed; `Right Shift + F12` toggles it.

## Usage

Open the **Majestic RP Linux Fix** shortcut and choose an action. Close the game before the initial installation; the utility can request a clean Steam shutdown.

You need **Grand Theft Auto V Legacy**, not Enhanced. Proton Experimental must be installed in Steam.

The external `majestic-rp-linux` runner is installed separately. The GUI can download it automatically after displaying its source and license. By default, the utility looks under `~/.local/share/majestic-rp-runner` and `~/.local/share/majestic-rp-runner-*`.

## Notice

This is an unofficial community utility. The patch is based on the public investigation at:
https://github.com/digitalhorizongroup/majestic-rp-linux/issues/18

See `THIRD_PARTY.md`: no third-party source code or binaries are bundled in this project.

The patched copy is stored under `Steam/compatibilitytools.d/Proton-Exp-MJLX`. The original Proton Experimental is not modified.
