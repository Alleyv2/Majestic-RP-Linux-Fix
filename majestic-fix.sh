#!/usr/bin/env bash
set -uo pipefail

APP_VERSION="1.2.0"
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_ID="271590"
TOOL_NAME="Proton-Exp-MJLX"
NONINTERACTIVE="${MAJESTIC_FIX_NONINTERACTIVE:-0}"
NO_DIALOGS="${MAJESTIC_FIX_NO_DIALOGS:-0}"

if [[ "${1:-}" == "--lang" && -n "${2:-}" ]]; then
  LANG_CHOICE="$2"
elif [[ "${LANG:-en}" == ru* ]]; then
  LANG_CHOICE="ru"
else
  LANG_CHOICE="en"
fi

trm() {
  local ru="$1" en="$2"
  if [[ "$LANG_CHOICE" == "ru" ]]; then printf '%s' "$ru"; else printf '%s' "$en"; fi
}

have_gui() {
  [[ "$NO_DIALOGS" != "1" && -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]] && command -v zenity >/dev/null 2>&1
}

info() {
  if have_gui; then zenity --info --title="Majestic RP Linux Fix" --width=520 --text="$1"; else printf '\n%s\n' "$1"; fi
}

error() {
  if have_gui; then zenity --error --title="Majestic RP Linux Fix" --width=560 --text="$1"; else printf '\nERROR: %s\n' "$1" >&2; fi
}

confirm() {
  if have_gui; then zenity --question --title="Majestic RP Linux Fix" --width=540 --text="$1"; else
    printf '%s [y/N]: ' "$1"
    read -r answer
    [[ "$answer" =~ ^([yY]|[дД])$ ]]
  fi
}

preflight_check() {
  command -v python3 >/dev/null 2>&1 || {
    error "$(trm 'Не найден Python 3. Установите python и повторите.' 'Python 3 was not found. Install python3 and retry.')"
    return 1
  }
  python3 "$APP_DIR/dependency_check.py" --lang "$LANG_CHOICE" || return 1
}

find_steam_root() {
  local candidate
  for candidate in \
    "${STEAM_ROOT:-}" \
    "$HOME/.local/share/Steam" \
    "$HOME/.steam/steam" \
    "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"; do
    [[ -n "$candidate" && -d "$candidate/steamapps" ]] && { readlink -f "$candidate"; return 0; }
  done
  return 1
}

find_runner() {
  local candidate
  for candidate in \
    "$HOME/.local/share/majestic-rp-runner" \
    "$HOME/.local/share/majestic-rp-runner-6.3.4" \
    "$HOME/.local/share"/majestic-rp-runner-*; do
    [[ -f "$candidate/majestic_linux/__main__.py" ]] && { printf '%s\n' "$candidate"; return 0; }
  done
  return 1
}

detect_paths() {
  STEAM_ROOT_FOUND="$(find_steam_root)" || {
    error "$(trm 'Steam не найден. Установите обычную версию Steam и запустите её хотя бы один раз.' 'Steam was not found. Install the regular Steam package and run it at least once.')"
    return 1
  }
  SOURCE_PROTON="$STEAM_ROOT_FOUND/steamapps/common/Proton - Experimental"
  TARGET_PROTON="$STEAM_ROOT_FOUND/compatibilitytools.d/$TOOL_NAME"
  PREFIX="$STEAM_ROOT_FOUND/steamapps/compatdata/$APP_ID"
  GTA_PATH="$STEAM_ROOT_FOUND/steamapps/common/Grand Theft Auto V"
  STEAM_CONFIG="$STEAM_ROOT_FOUND/config/config.vdf"
  return 0
}

steam_ready() {
  pgrep -f '[s]teamwebhelper.*-steampid=' >/dev/null 2>&1 && \
    pgrep -f '[s]team-runtime-launcher-service' >/dev/null 2>&1
}

steam_or_game_running() {
  steam_ready && return 0
  pgrep -f '[M]ajestic Launcher.exe|[G]TA5.exe|[R]ockstar Games.*Launcher' >/dev/null 2>&1 && return 0
  return 1
}

stop_steam_safely() {
  steam_or_game_running || return 0
  if [[ "$NONINTERACTIVE" != "1" ]]; then
    confirm "$(trm 'Для установки нужно закрыть Steam, Majestic и GTA. Закрыть Steam штатно сейчас?' 'Steam, Majestic and GTA must be closed before installation. Shut Steam down cleanly now?')" || return 1
  fi
  command -v steam >/dev/null 2>&1 && steam -shutdown >/dev/null 2>&1 || true
  for _ in {1..30}; do
    steam_or_game_running || return 0
    sleep 1
  done
  error "$(trm 'Некоторые процессы ещё работают. Закройте Steam, Majestic, Rockstar Launcher и GTA, затем повторите.' 'Some processes are still running. Close Steam, Majestic, Rockstar Launcher and GTA, then retry.')"
  return 1
}

runner_check() {
  if RUNNER_PATH="$(find_runner)"; then return 0; fi
  error "$(trm 'Внешний раннер majestic-rp-linux не найден. Установите его отдельно в ~/.local/share/majestic-rp-runner. Эта программа намеренно не загружает и не распространяет сторонний код.' 'The external majestic-rp-linux runner was not found. Install it separately in ~/.local/share/majestic-rp-runner. This program intentionally does not download or redistribute third-party code.')"
  return 1
}

asar_install() {
  command -v asar >/dev/null 2>&1 && return 0
  [[ -x "$HOME/.local/bin/asar" ]] && return 0
  command -v npm >/dev/null 2>&1 || {
    error "$(trm 'Не найден asar. Установите nodejs и npm, затем повторите установку.' 'asar was not found. Install nodejs and npm, then retry.')"
    return 1
  }
  npm install --global --prefix "$HOME/.local" asar || return 1
}

proton_is_patched() {
  [[ -f "$TARGET_PROTON/files/lib/wine/x86_64-unix/ntdll.so" ]] || return 1
  python3 "$APP_DIR/patch_ntdll.py" --check "$TARGET_PROTON/files/lib/wine/x86_64-unix/ntdll.so" >/dev/null 2>&1
}

proton_needs_rebuild() {
  proton_is_patched || return 0
  [[ -f "$SOURCE_PROTON/version" && -f "$TARGET_PROTON/version" ]] || return 1
  cmp -s "$SOURCE_PROTON/version" "$TARGET_PROTON/version" || return 0
  return 1
}

build_patched_proton() {
  [[ -x "$SOURCE_PROTON/proton" ]] || {
    error "$(trm 'Proton Experimental не установлен. Установите его через библиотеку Steam → Инструменты.' 'Proton Experimental is not installed. Install it from Steam Library → Tools.')"
    return 1
  }
  mkdir -p "$STEAM_ROOT_FOUND/compatibilitytools.d"
  if ! proton_needs_rebuild; then return 0; fi

  local stamp temp backup
  stamp="$(date +%Y%m%d-%H%M%S)"
  temp="$STEAM_ROOT_FOUND/compatibilitytools.d/.${TOOL_NAME}.new-$stamp"
  backup="$STEAM_ROOT_FOUND/compatibilitytools.d/${TOOL_NAME}.backup-$stamp"
  cp -a "$SOURCE_PROTON" "$temp" || return 1
  python3 "$APP_DIR/patch_ntdll.py" "$temp/files/lib/wine/x86_64-unix/ntdll.so" || { rm -rf -- "$temp"; return 1; }
  cp "$APP_DIR/compatibilitytool.vdf" "$temp/compatibilitytool.vdf" || { rm -rf -- "$temp"; return 1; }
  if [[ -e "$TARGET_PROTON" ]]; then mv "$TARGET_PROTON" "$backup" || return 1; fi
  mv "$temp" "$TARGET_PROTON" || return 1
}

configure_all() {
  RUNNER_PATH="$(find_runner)" || return 1
  mkdir -p "$HOME/.config/majestic-runner" "$HOME/.local/bin"
  local fps_config="$HOME/.config/MangoHud/majestic-gta.conf"
  local launch_options=""
  if command -v mangohud >/dev/null 2>&1; then
    mkdir -p "$(dirname -- "$fps_config")"
    if [[ -f "$fps_config" ]]; then
      cp -a "$fps_config" "$fps_config.mjlx-backup-$(date +%Y%m%d-%H%M%S)"
    fi
    cp "$APP_DIR/mangohud-gta.conf" "$fps_config"
    launch_options="MANGOHUD=1 MANGOHUD_CONFIGFILE=$fps_config %command%"
  fi
  python3 "$APP_DIR/configure.py" \
    --config "$HOME/.config/majestic-runner/majestic-runner.conf" \
    --proton "$TARGET_PROTON/proton" \
    --prefix "$PREFIX" \
    --gta "$GTA_PATH" \
    --launch-options "$launch_options"
  python3 "$APP_DIR/configure.py" --steam-config "$STEAM_CONFIG" --tool "$TOOL_NAME"

  local launcher="$HOME/.local/bin/majestic-rp.sh"
  sed \
    -e "s|@@RUNNER@@|$RUNNER_PATH|g" \
    -e "s|@@HOME@@|$HOME|g" \
    "$APP_DIR/launch-majestic.template.sh" > "$launcher"
  chmod +x "$launcher"

  mkdir -p "$HOME/.local/share/applications"
  sed \
    -e "s|@@HOME@@|$HOME|g" \
    "$APP_DIR/majestic-rp.desktop.template" > "$HOME/.local/share/applications/majestic-rp.desktop"
  chmod +x "$HOME/.local/share/applications/majestic-rp.desktop"
}

install_fix() {
  preflight_check || return 1
  detect_paths || return 1
  [[ -d "$GTA_PATH" ]] || {
    error "$(trm 'GTA V Legacy не найдена. Сначала установите в Steam именно Grand Theft Auto V Legacy.' 'GTA V Legacy was not found. Install Grand Theft Auto V Legacy in Steam first.')"
    return 1
  }
  stop_steam_safely || return 1
  runner_check || return 1
  asar_install || return 1
  build_patched_proton || return 1
  configure_all || return 1
  if [[ "${MAJESTIC_FIX_FULL_INSTALL:-0}" == "1" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
    export ASAR_BIN="$HOME/.local/bin/asar"
    (cd "$RUNNER_PATH" && python3 -m majestic_linux install) || return 1
  fi
  info "$(trm 'Фикс установлен и проверен. Перезапустите Steam, затем запускайте Majestic через ярлык.' 'The fix was installed and verified. Restart Steam, then launch Majestic from the shortcut.')"
}

launch_game() {
  detect_paths || return 1
  if ! proton_is_patched; then
    error "$(trm 'Исправленный Proton не найден или повреждён. Сначала выберите «Установить / обновить фикс».' 'Patched Proton is missing or invalid. Choose “Install / update fix” first.')"
    return 1
  fi
  if pgrep -f '[M]ajestic Launcher.exe' >/dev/null 2>&1; then
    info "$(trm 'Majestic уже запущен.' 'Majestic is already running.')"
    return 0
  fi
  if ! steam_ready; then
    if command -v steam >/dev/null 2>&1; then
      nohup steam >/dev/null 2>&1 </dev/null &
    else
      error "$(trm 'Команда Steam не найдена.' 'The Steam command was not found.')"
      return 1
    fi
    local ready=0
    for _ in {1..60}; do
      if steam_ready; then ready=1; break; fi
      sleep 1
    done
    if [[ "$ready" != "1" ]]; then
      error "$(trm 'Steam не успел запуститься за 60 секунд. Откройте Steam вручную, дождитесь библиотеки и повторите.' 'Steam did not become ready within 60 seconds. Open Steam manually, wait for the Library, and retry.')"
      return 1
    fi
    sleep 3
  fi
  nohup "$HOME/.local/bin/majestic-rp.sh" >/dev/null 2>&1 </dev/null &
  disown 2>/dev/null || true
}

diagnose() {
  detect_paths || return 1
  local patched="NO" runner="NO" gta="NO" active="NO" injection="UNKNOWN" report
  proton_is_patched && patched="YES"
  find_runner >/dev/null 2>&1 && runner="YES"
  [[ -f "$GTA_PATH/GTA5.exe" ]] && gta="YES"
  pgrep -f '[G]TA5.exe' >/dev/null 2>&1 && active="YES"
  local patchlog="$PREFIX/pfx/drive_c/users/steamuser/AppData/Roaming/majestic-launcher/Multiplayer/logs/majestic-patcher.log"
  [[ -f "$patchlog" ]] && grep -q 'Injected DLL successfully' "$patchlog" && injection="SUCCESS"
  report="Majestic RP Linux Fix $APP_VERSION
Steam: $STEAM_ROOT_FOUND
GTA Legacy: $gta
Runner: $runner
Patched Proton: $patched
GTA active: $active
Last injection: $injection"
  if have_gui; then zenity --info --title="Majestic RP Linux Fix — Diagnostics" --width=620 --text="$report"; else printf '%s\n' "$report"; fi
}

show_logs() {
  detect_paths || return 1
  local patchlog="$PREFIX/pfx/drive_c/users/steamuser/AppData/Roaming/majestic-launcher/Multiplayer/logs/majestic-patcher.log"
  local content
  content="$(tail -n 120 "$patchlog" 2>/dev/null || trm 'Лог пока отсутствует.' 'No log is available yet.')"
  if have_gui; then
    printf '%s\n' "$content" | zenity --text-info --title="Majestic injection log" --width=900 --height=620
  else
    printf '%s\n' "$content"
  fi
}

disable_fix() {
  detect_paths || return 1
  stop_steam_safely || return 1
  confirm "$(trm 'Отключить фикс? Файлы исправленного Proton сохранятся, но GTA вернётся на обычный Proton Experimental.' 'Disable the fix? Patched Proton files will be preserved, but GTA will return to regular Proton Experimental.')" || return 0
  python3 "$APP_DIR/configure.py" --steam-config "$STEAM_CONFIG" --tool "proton_experimental"
  if [[ -f "$HOME/.config/majestic-runner/majestic-runner.conf" ]]; then
    python3 "$APP_DIR/configure.py" \
      --config "$HOME/.config/majestic-runner/majestic-runner.conf" \
      --proton "$SOURCE_PROTON/proton" --prefix "$PREFIX" --gta "$GTA_PATH"
  fi
  info "$(trm 'Фикс отключён без удаления файлов. Для повторного включения выберите установку/обновление.' 'The fix was disabled without deleting files. Use install/update to enable it again.')"
}

choose_language() {
  if have_gui; then
    local value
    value="$(zenity --list --title="Language / Язык" --width=420 --height=260 --column="Code" --column="Language" ru 'Русский' en 'English' --hide-column=1 2>/dev/null)" || return 1
    LANG_CHOICE="$value"
  else
    printf '1) Русский\n2) English\n> '
    read -r value
    [[ "$value" == "2" ]] && LANG_CHOICE="en" || LANG_CHOICE="ru"
  fi
}

menu_gui() {
  local choice
  while true; do
    choice="$(zenity --list --title="Majestic RP Linux Fix $APP_VERSION" --width=650 --height=450 \
      --column="Action" --column="$(trm 'Действие' 'Action')" \
      launch "$(trm 'Запустить Majestic RP' 'Launch Majestic RP')" \
      install "$(trm 'Установить / обновить фикс' 'Install / update fix')" \
      diagnose "$(trm 'Проверить конфигурацию' 'Check configuration')" \
      logs "$(trm 'Показать лог инъекции' 'Show injection log')" \
      language "Language / Язык" \
      disable "$(trm 'Отключить фикс без удаления' 'Disable fix without deleting files')" \
      --hide-column=1 2>/dev/null)" || break
    case "$choice" in
      launch) launch_game ;;
      install) install_fix ;;
      diagnose) diagnose ;;
      logs) show_logs ;;
      language) choose_language || true ;;
      disable) disable_fix ;;
    esac
  done
}

menu_cli() {
  while true; do
    printf '\nMajestic RP Linux Fix %s\n' "$APP_VERSION"
    printf '1) %s\n2) %s\n3) %s\n4) %s\n5) Language / Язык\n6) %s\n0) %s\n> ' \
      "$(trm 'Запустить Majestic RP' 'Launch Majestic RP')" \
      "$(trm 'Установить / обновить фикс' 'Install / update fix')" \
      "$(trm 'Проверить конфигурацию' 'Check configuration')" \
      "$(trm 'Показать лог инъекции' 'Show injection log')" \
      "$(trm 'Отключить фикс' 'Disable fix')" \
      "$(trm 'Выход' 'Exit')"
    read -r choice
    case "$choice" in
      1) launch_game ;;
      2) install_fix ;;
      3) diagnose ;;
      4) show_logs ;;
      5) choose_language || true ;;
      6) disable_fix ;;
      0) break ;;
    esac
  done
}

case "${1:-}" in
  --install) install_fix ;;
  --launch) launch_game ;;
  --diagnose) diagnose ;;
  --logs) show_logs ;;
  --disable) disable_fix ;;
  *) if have_gui; then menu_gui; else menu_cli; fi ;;
esac
