# Architecture

## User flow

1. The user opens the Qt 6 application from KDE or the desktop shortcut.
2. The dashboard performs read-only checks for Steam, GTA V Legacy, the patched Proton tool and Majestic Launcher.
3. **Install or repair** explains any external download and requests consent.
4. GTA V Legacy and Proton Experimental are installed through Steam when missing.
5. The separately licensed MIT runner is downloaded from a pinned commit and verified by SHA-256.
6. The application creates `Proton-Exp-MJLX` as a separate copy, patches only that copy and keeps backups.
7. The runner downloads Majestic Launcher from the configured official Majestic CDN and prepares the shared GTA prefix.
8. XDG desktop entries are installed for KDE and other compliant Linux desktops.
9. **Launch** starts Steam, waits for its UI and runtime service, and only then starts Majestic.

## Trust boundaries

- This repository: MIT-licensed GUI, orchestration, verification and configuration code.
- `majestic-rp-linux`: external MIT dependency, stored separately with its license.
- Steam and Proton: external Valve software.
- Majestic Launcher: external software downloaded from Majestic infrastructure.
- GTA V Legacy and Rockstar Games Launcher: licensed external software.

No authentication tokens, cookies or account data are copied into reports. The integrated log viewer masks authorization headers.

## Distribution

Development builds can use the system PySide6 package. Tagged public releases are built on Ubuntu 22.04 with PyInstaller and published as a standalone x86_64 executable, a permission-preserving tar archive and `SHA256SUMS`. The executable bundles the GUI runtime but not Steam, Proton, GTA, Majestic or the external runner. It never silently self-updates executable code.
