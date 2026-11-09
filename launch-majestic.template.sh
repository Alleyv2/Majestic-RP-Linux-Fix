#!/usr/bin/env bash
set -uo pipefail
RUNNER="@@RUNNER@@"
LOGDIR="@@HOME@@/.config/majestic-runner"
mkdir -p "$LOGDIR"

if pgrep -f '[M]ajestic Launcher.exe' >/dev/null 2>&1; then
  command -v notify-send >/dev/null 2>&1 && notify-send "Majestic RP" "Launcher is already running / Лаунчер уже запущен"
  exit 0
fi

export PATH="@@HOME@@/.local/bin:$PATH"
export ASAR_BIN="@@HOME@@/.local/bin/asar"
cd "$RUNNER" || exit 1
printf '\n=== %s ===\n' "$(date '+%F %T')" >> "$LOGDIR/launcher-desktop.log"
exec python3 -m majestic_linux run >> "$LOGDIR/launcher-desktop.log" 2>&1
