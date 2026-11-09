# Majestic RP Linux Fix

A standalone bilingual maintenance utility for Majestic RP on Linux.

- [English documentation](README_EN.md)
- [Русская документация](README_RU.md)
- [Third-party dependencies and attribution](THIRD_PARTY.md)
- [Changelog](CHANGELOG.md)
- [Architecture and distribution](ARCHITECTURE.md)
- [Security policy](SECURITY.md)

This repository contains no vendored third-party source code or binaries.

The desktop interface uses the official Qt for Python binding, PySide6. For end-user releases, bundle the application with `pyside6-deploy`; source checkouts can use the system PySide6 package on Arch Linux.
