# Changelog

## 1.1.1 — 2026-11-09

- fixed the About page layout at wide and short window sizes;
- replaced the native language dropdown with a themed RU/EN switch;
- added recoverable injection-log clearing;
- made component states explicit: installed, running, or missing;
- added creator attribution for Alley and a GitHub profile link.

## 1.1.0 — 2026-11-09

- added a native bilingual PySide6/Qt 6 interface;
- added a guided one-click install and repair workflow;
- added integrated status cards, progress output and sanitized logs;
- added a pinned SHA-256-verified downloader for the separately licensed MIT runner;
- added XDG/KDE application-menu and desktop-shortcut installation;
- kept CLI mode available as a fallback.

## 1.0.1 — 2026-11-09

- fixed false-positive Majestic process detection;
- detached Steam and Majestic from the maintenance menu process;
- added a real Steam readiness check (`steamwebhelper` and runtime launcher service);
- Steam now has up to 60 seconds to become ready before Majestic starts;
- verified end-to-end with a successful GTA V Legacy DLL injection and active Majestic web engine.

## 1.0.0 — 2026-11-09

- initial bilingual installer, launcher, diagnostics and rollback utility;
- separate patched Proton Experimental tool;
- Steam AppID 271590 and shared-prefix configuration;
- Wine 11 RCX compatibility patch verification and backup.
