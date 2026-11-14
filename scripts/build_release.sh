#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf -- build dist
python scripts/collect_licenses.py build-licenses

data_files=(
  majestic-fix.sh patch_ntdll.py configure.py download_dependency.py dependency_check.py install_app.py
  compatibilitytool.vdf launch-majestic.template.sh mangohud-gta.conf majestic-rp.desktop.template
  README.md README_RU.md README_EN.md THIRD_PARTY.md CHANGELOG.md LICENSE ARCHITECTURE.md SECURITY.md requirements.txt
)

pyinstaller_args=(
  --clean --noconfirm --onefile --windowed
  --name Majestic-RP-Linux-Fix-x86_64
)
pyinstaller_args+=(--add-data "build-licenses:LICENSES")
for file in "${data_files[@]}"; do
  pyinstaller_args+=(--add-data "$file:.")
done
python -m PyInstaller "${pyinstaller_args[@]}" gui.py

chmod 755 dist/Majestic-RP-Linux-Fix-x86_64
cp LICENSE THIRD_PARTY.md README_RU.md README_EN.md dist/
cp -a build-licenses dist/LICENSES
tar -C dist -czf dist/Majestic-RP-Linux-Fix-v1.2.0-linux-x86_64.tar.gz \
  Majestic-RP-Linux-Fix-x86_64 LICENSE LICENSES THIRD_PARTY.md README_RU.md README_EN.md
(
  cd dist
  sha256sum Majestic-RP-Linux-Fix-x86_64 Majestic-RP-Linux-Fix-v1.2.0-linux-x86_64.tar.gz > SHA256SUMS
)
