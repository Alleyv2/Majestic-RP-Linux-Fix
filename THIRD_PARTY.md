# Third-party dependencies and attribution

The source repository does not vendor the external Majestic runner or other game software. Standalone release assets do bundle the Python, PySide6/Qt and PyInstaller runtime components needed to start the GUI; those components remain under their own licenses.

## Runtime dependencies

The utility can operate with a separately installed `majestic-rp-linux` runner:

https://github.com/digitalhorizongroup/majestic-rp-linux

The runner is not bundled in this repository. With explicit user consent, `download_dependency.py` downloads a pinned upstream commit, verifies the archive against a hard-coded SHA-256 digest, extracts it to a separate XDG user-data directory, and preserves its original MIT license.

Steam, Proton Experimental, Wine, Rockstar Games Launcher, Grand Theft Auto V and Majestic Launcher are also external software and are not part of this repository.

The GUI uses Qt for Python / PySide6, provided under the LGPLv3/GPLv3 or a commercial Qt license. Standalone releases use the LGPLv3 option and keep Qt as separate shared libraries inside the temporary application bundle. Python is distributed under the Python Software Foundation License. PyInstaller and its bootloader are distributed under GPL terms with the PyInstaller bootloader exception. The release archive includes the exact upstream license files collected from the build environment under `LICENSES/`; the same files are embedded in the one-file executable.

## Compatibility technique

The Wine 11 RCX compatibility problem and the relevant machine-code sequence were publicly documented here:

https://github.com/digitalhorizongroup/majestic-rp-linux/issues/18

`patch_ntdll.py` is an original implementation written for this project. It only locates, verifies, backs up and replaces the documented 17-byte compatibility sequence. It does not contain a copy of Wine, Proton, the runner or Majestic software.
