#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

APP_DIR = Path(__file__).resolve().parent
HOME = Path.home()
STEAM = HOME / ".local/share/Steam"
PREFIX = STEAM / "steamapps/compatdata/271590"
GTA = STEAM / "steamapps/common/Grand Theft Auto V"
PROTON = STEAM / "compatibilitytools.d/Proton-Exp-MJLX"
PATCH_LOG = PREFIX / "pfx/drive_c/users/steamuser/AppData/Roaming/majestic-launcher/Multiplayer/logs/majestic-patcher.log"
MAIN_LOG = PREFIX / "pfx/drive_c/users/steamuser/AppData/Roaming/majestic-launcher/logs/main.log"

TEXT = {
    "ru": {
        "overview": "Главная",
        "install": "Установка",
        "logs": "Журналы",
        "about": "О программе",
        "eyebrow": "MAJESTIC RP · LINUX",
        "title": "Играй без ручной настройки",
        "subtitle": "Steam, GTA V Legacy, Proton и Majestic — в правильном порядке и в одном окне.",
        "ready": "Всё готово к игре",
        "needs": "Требуется установка",
        "ready_detail": "Исправленный Proton установлен, последняя инъекция успешна.",
        "needs_detail": "Мастер проверит систему и установит недостающие компоненты.",
        "play": "Запустить Majestic RP",
        "repair": "Установить или исправить",
        "diagnostics": "Обновить проверку",
        "steam": "Steam",
        "gta": "GTA V Legacy",
        "fix": "Proton Fix",
        "launcher": "Majestic",
        "online": "готов",
        "missing": "не найден",
        "steam_ready": "запущен",
        "steam_missing": "не запущен",
        "gta_ready": "установлена",
        "gta_missing": "не установлена",
        "fix_ready": "установлен",
        "fix_missing": "не установлен",
        "launcher_ready": "установлен",
        "launcher_missing": "не установлен",
        "quick": "Быстрые действия",
        "repair_desc": "Одна кнопка проверит зависимости, скачает закреплённые компоненты и настроит общий префикс.",
        "logs_desc": "Посмотреть последнюю инъекцию и сообщения запуска без поиска файлов вручную.",
        "open_logs": "Открыть журнал",
        "wizard_title": "Установка и восстановление",
        "wizard_sub": "Программа выполняет шаги последовательно и сохраняет резервные копии конфигурации.",
        "step1": "Проверка Steam и GTA V Legacy",
        "step2": "Загрузка проверяемой MIT-зависимости",
        "step3": "Создание отдельного Proton-Exp-MJLX",
        "step4": "Установка Majestic Launcher и ярлыков",
        "start_install": "Начать установку",
        "working": "Выполняется…",
        "activity": "Ход выполнения",
        "log_title": "Журнал инъекции",
        "refresh": "Обновить",
        "copy": "Копировать",
        "clear_log": "Очистить журнал инъекции",
        "clear_confirm": "Очистить текущий журнал инъекции? Перед очисткой будет создана резервная копия.",
        "clear_running": "Нельзя очищать журнал, пока GTA или Majestic запущены.",
        "clear_done": "Журнал очищен. Резервная копия сохранена рядом с исходным файлом.",
        "no_log": "Журнал инъекции пока не создан.",
        "about_title": "Majestic RP Linux Fix",
        "about_text": "Независимый графический установщик для GTA V Legacy и Majestic RP в Linux. Он проверяет систему, создаёт отдельный исправленный Proton, устанавливает Majestic и запускает компоненты в правильном порядке.",
        "privacy_text": "Сторонние бинарники не включены в исходный код. MIT-зависимость загружается отдельно только после согласия и проверяется по SHA-256.",
        "creator": "Создатель программы",
        "version": "Версия 1.1.2 · Qt 6 · KDE friendly",
        "confirm_install": "Steam, Rockstar Launcher, Majestic и GTA будут штатно закрыты на время установки. Продолжить?",
        "dependency_title": "Внешняя MIT-зависимость",
        "dependency_text": "Для подготовки Majestic требуется majestic-rp-linux. Он будет скачан отдельно с GitHub из закреплённого коммита, проверен по SHA-256 и сохранён вместе с оригинальной MIT-лицензией. Продолжить?",
        "success": "Установка завершена. Можно запускать игру.",
        "failed": "Операция завершилась с ошибкой. Подробности показаны в журнале выполнения.",
        "game_running": "Игра уже запущена",
        "launched": "Steam и Majestic запускаются в правильном порядке.",
        "gta_required": "GTA V Legacy ещё не установлена. Открыть её установку в Steam? Загрузка игры большая и начнётся только после подтверждения в Steam.",
        "proton_required": "Proton Experimental ещё не установлен. Открыть его установку в Steam? После завершения снова нажмите «Начать установку».",
    },
    "en": {
        "overview": "Overview",
        "install": "Install",
        "logs": "Logs",
        "about": "About",
        "eyebrow": "MAJESTIC RP · LINUX",
        "title": "Play without manual setup",
        "subtitle": "Steam, GTA V Legacy, Proton and Majestic — in the right order, from one window.",
        "ready": "Ready to play",
        "needs": "Installation required",
        "ready_detail": "Patched Proton is installed and the latest injection succeeded.",
        "needs_detail": "The wizard will inspect the system and install missing components.",
        "play": "Launch Majestic RP",
        "repair": "Install or repair",
        "diagnostics": "Refresh checks",
        "steam": "Steam",
        "gta": "GTA V Legacy",
        "fix": "Proton Fix",
        "launcher": "Majestic",
        "online": "ready",
        "missing": "missing",
        "steam_ready": "running",
        "steam_missing": "not running",
        "gta_ready": "installed",
        "gta_missing": "not installed",
        "fix_ready": "installed",
        "fix_missing": "not installed",
        "launcher_ready": "installed",
        "launcher_missing": "not installed",
        "quick": "Quick actions",
        "repair_desc": "One button checks dependencies, downloads pinned components and configures the shared prefix.",
        "logs_desc": "Read the latest injection and launch messages without hunting for files.",
        "open_logs": "Open log",
        "wizard_title": "Install and repair",
        "wizard_sub": "Steps run in order and configuration backups are kept automatically.",
        "step1": "Check Steam and GTA V Legacy",
        "step2": "Download the verified MIT dependency",
        "step3": "Create the separate Proton-Exp-MJLX tool",
        "step4": "Install Majestic Launcher and shortcuts",
        "start_install": "Start installation",
        "working": "Working…",
        "activity": "Activity",
        "log_title": "Injection log",
        "refresh": "Refresh",
        "copy": "Copy",
        "clear_log": "Clear injection log",
        "clear_confirm": "Clear the current injection log? A backup will be created first.",
        "clear_running": "The log cannot be cleared while GTA or Majestic is running.",
        "clear_done": "The log was cleared. A backup was saved next to the original file.",
        "no_log": "No injection log has been created yet.",
        "about_title": "Majestic RP Linux Fix",
        "about_text": "An independent graphical installer for GTA V Legacy and Majestic RP on Linux. It checks the system, creates a separate patched Proton tool, installs Majestic, and starts components in the correct order.",
        "privacy_text": "Third-party binaries are not bundled with the source. The MIT dependency is downloaded separately only with consent and verified by SHA-256.",
        "creator": "Created by",
        "version": "Version 1.1.2 · Qt 6 · KDE friendly",
        "confirm_install": "Steam, Rockstar Launcher, Majestic and GTA will be closed cleanly during installation. Continue?",
        "dependency_title": "External MIT dependency",
        "dependency_text": "Preparing Majestic requires majestic-rp-linux. It will be downloaded separately from a pinned GitHub commit, verified by SHA-256, and stored with its original MIT license. Continue?",
        "success": "Installation completed. The game is ready to launch.",
        "failed": "The operation failed. See the activity log for details.",
        "game_running": "The game is already running",
        "launched": "Steam and Majestic are starting in the correct order.",
        "gta_required": "GTA V Legacy is not installed yet. Open its Steam installation page? The download is large and starts only after confirmation in Steam.",
        "proton_required": "Proton Experimental is not installed yet. Open its Steam installation page? Click Start installation again when it finishes.",
    },
}


def process_exists(fragment: str) -> bool:
    for item in Path("/proc").iterdir():
        if not item.name.isdigit():
            continue
        try:
            cmd = (item / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
            if fragment in cmd:
                return True
        except (OSError, PermissionError):
            pass
    return False


def find_runner() -> Path | None:
    choices = [HOME / ".local/share/majestic-rp-runner", HOME / ".local/share/majestic-rp-runner-6.3.4"]
    choices.extend((HOME / ".local/share").glob("majestic-rp-runner-*"))
    return next((p for p in choices if (p / "majestic_linux/__main__.py").is_file()), None)


def backup_and_clear_log(path: Path, now: datetime | None = None) -> Path:
    """Archive an existing log and replace it with a private empty file."""
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.backup-{stamp}")
    path.replace(backup)
    path.touch(mode=0o600)
    path.chmod(0o600)
    return backup


def current_status() -> dict[str, bool]:
    patched = False
    target = PROTON / "files/lib/wine/x86_64-unix/ntdll.so"
    if target.is_file():
        result = subprocess.run(
            [sys.executable, str(APP_DIR / "patch_ntdll.py"), "--check", str(target)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        patched = result.returncode == 0
    launcher = PREFIX / "pfx/drive_c/users/steamuser/AppData/Local/MajesticLauncher/Majestic Launcher.exe"
    injection = PATCH_LOG.is_file() and "Injected DLL successfully" in PATCH_LOG.read_text(errors="ignore")
    return {
        "steam": process_exists("steamwebhelper") and process_exists("steam-runtime-launcher-service"),
        "gta": (GTA / "GTA5.exe").is_file(),
        "fix": patched,
        "runner": find_runner() is not None,
        "launcher": launcher.is_file(),
        "active": process_exists("GTA5.exe"),
        "injection": injection,
    }


class NavButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(48)


class StatusPill(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("statusPill")
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 13, 16, 13)
        self.dot = QLabel("●")
        self.name = QLabel(title)
        self.value = QLabel()
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self.dot)
        row.addWidget(self.name)
        row.addStretch()
        row.addWidget(self.value)

    def set_state(self, ok: bool, ready_text: str, missing_text: str) -> None:
        self.dot.setStyleSheet(f"color: {'#39d98a' if ok else '#ff5578'}; font-size: 17px;")
        self.value.setText(ready_text if ok else missing_text)
        self.value.setStyleSheet(f"color: {'#83e8b5' if ok else '#ff8ca2'}; font-weight: 700;")


class ActionCard(QFrame):
    clicked = Signal()

    def __init__(self, icon: str, title: str, text: str, button: str):
        super().__init__()
        self.setObjectName("actionCard")
        self.setMinimumHeight(190)
        box = QVBoxLayout(self)
        box.setContentsMargins(22, 20, 22, 20)
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setObjectName("muted")
        self.button = QPushButton(button)
        self.button.setObjectName("secondaryButton")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self.clicked)
        box.addWidget(icon_label)
        box.addWidget(title_label)
        box.addWidget(text_label)
        box.addStretch()
        box.addWidget(self.button)


class MainWindow(QMainWindow):
    def __init__(self, language: str = "ru"):
        super().__init__()
        self.lang = language
        self.t = TEXT[self.lang]
        self.proc: QProcess | None = None
        self.setWindowTitle("Majestic RP Linux Fix")
        self.setMinimumSize(1060, 700)
        self.resize(1180, 760)
        icon = HOME / ".local/share/icons/majestic-rp.png"
        if icon.is_file():
            self.setWindowIcon(QIcon(str(icon)))
        self._build()
        self.refresh_status()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(5000)

    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(235)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(24, 28, 20, 24)
        brand = QLabel("MAJESTIC")
        brand.setObjectName("brand")
        brand_sub = QLabel("LINUX FIX")
        brand_sub.setObjectName("brandSub")
        side.addWidget(brand)
        side.addWidget(brand_sub)
        side.addSpacing(36)
        self.nav = []
        for index, (icon, key) in enumerate((("⌂", "overview"), ("↓", "install"), ("≡", "logs"), ("?", "about"))):
            button = NavButton(f"{icon}    {self.t[key]}")
            button.clicked.connect(lambda checked=False, i=index: self.set_page(i))
            side.addWidget(button)
            self.nav.append(button)
        side.addStretch()
        language_label = QLabel("LANGUAGE / ЯЗЫК")
        language_label.setObjectName("languageLabel")
        side.addWidget(language_label)
        language_row = QHBoxLayout()
        language_row.setSpacing(6)
        for code, label in (("ru", "RU"), ("en", "EN")):
            button = QPushButton(label)
            button.setObjectName("languageButton")
            button.setCheckable(True)
            button.setChecked(code == self.lang)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, value=code: self.change_language(value))
            language_row.addWidget(button)
        side.addLayout(language_row)
        version = QLabel("v1.1.2")
        version.setObjectName("sideVersion")
        side.addWidget(version)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._overview_page())
        self.pages.addWidget(self._install_page())
        self.pages.addWidget(self._logs_page())
        self.pages.addWidget(self._about_page())
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)
        self.set_page(0)

    def scroll_page(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        return scroll

    def _overview_page(self) -> QWidget:
        content = QWidget()
        content.setObjectName("page")
        box = QVBoxLayout(content)
        box.setContentsMargins(42, 34, 42, 34)
        box.setSpacing(20)
        eyebrow = QLabel(self.t["eyebrow"])
        eyebrow.setObjectName("eyebrow")
        title = QLabel(self.t["title"])
        title.setObjectName("pageTitle")
        subtitle = QLabel(self.t["subtitle"])
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        box.addWidget(eyebrow)
        box.addWidget(title)
        box.addWidget(subtitle)

        hero = QFrame()
        hero.setObjectName("hero")
        shadow = QGraphicsDropShadowEffect(hero)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 100))
        hero.setGraphicsEffect(shadow)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 25, 28, 25)
        self.hero_status = QLabel()
        self.hero_status.setObjectName("heroTitle")
        self.hero_detail = QLabel()
        self.hero_detail.setObjectName("heroDetail")
        self.play_button = QPushButton(self.t["play"])
        self.play_button.setObjectName("primaryButton")
        self.play_button.setMinimumHeight(54)
        self.play_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_button.clicked.connect(self.launch)
        hero_layout.addWidget(self.hero_status)
        hero_layout.addWidget(self.hero_detail)
        hero_layout.addSpacing(8)
        hero_layout.addWidget(self.play_button)
        box.addWidget(hero)

        pills = QHBoxLayout()
        self.pills = {}
        for key in ("steam", "gta", "fix", "launcher"):
            pill = StatusPill(self.t[key])
            self.pills[key] = pill
            pills.addWidget(pill)
        box.addLayout(pills)

        quick = QLabel(self.t["quick"])
        quick.setObjectName("sectionTitle")
        box.addWidget(quick)
        cards = QHBoxLayout()
        repair = ActionCard("⚙", self.t["repair"], self.t["repair_desc"], self.t["repair"])
        repair.clicked.connect(lambda: self.set_page(1))
        logs = ActionCard("≡", self.t["logs"], self.t["logs_desc"], self.t["open_logs"])
        logs.clicked.connect(lambda: self.set_page(2))
        cards.addWidget(repair)
        cards.addWidget(logs)
        box.addLayout(cards)
        box.addStretch()
        return self.scroll_page(content)

    def _install_page(self) -> QWidget:
        content = QWidget()
        content.setObjectName("page")
        box = QVBoxLayout(content)
        box.setContentsMargins(46, 38, 46, 38)
        box.setSpacing(18)
        title = QLabel(self.t["wizard_title"])
        title.setObjectName("pageTitle")
        sub = QLabel(self.t["wizard_sub"])
        sub.setObjectName("subtitle")
        box.addWidget(title)
        box.addWidget(sub)
        steps = QFrame()
        steps.setObjectName("panel")
        steps_box = QVBoxLayout(steps)
        steps_box.setContentsMargins(28, 24, 28, 24)
        for number, key in enumerate(("step1", "step2", "step3", "step4"), 1):
            row = QHBoxLayout()
            badge = QLabel(str(number))
            badge.setObjectName("numberBadge")
            badge.setFixedSize(34, 34)
            label = QLabel(self.t[key])
            label.setObjectName("stepText")
            row.addWidget(badge)
            row.addWidget(label)
            row.addStretch()
            steps_box.addLayout(row)
            if number < 4:
                steps_box.addSpacing(10)
        box.addWidget(steps)
        self.install_button = QPushButton(self.t["start_install"])
        self.install_button.setObjectName("primaryButton")
        self.install_button.setMinimumHeight(52)
        self.install_button.clicked.connect(self.start_install)
        box.addWidget(self.install_button)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        box.addWidget(self.progress)
        activity_title = QLabel(self.t["activity"])
        activity_title.setObjectName("sectionTitle")
        box.addWidget(activity_title)
        self.activity = QPlainTextEdit()
        self.activity.setReadOnly(True)
        self.activity.setMinimumHeight(180)
        self.activity.setPlaceholderText("Ready / Готово")
        box.addWidget(self.activity)
        box.addStretch()
        return self.scroll_page(content)

    def _logs_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("page")
        box = QVBoxLayout(page)
        box.setContentsMargins(46, 38, 46, 38)
        header = QHBoxLayout()
        title = QLabel(self.t["log_title"])
        title.setObjectName("pageTitle")
        refresh = QPushButton(self.t["refresh"])
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_logs)
        copy = QPushButton(self.t["copy"])
        copy.setObjectName("secondaryButton")
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.log_view.toPlainText()))
        clear = QPushButton(self.t["clear_log"])
        clear.setObjectName("dangerButton")
        clear.clicked.connect(self.clear_injection_log)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh)
        header.addWidget(copy)
        header.addWidget(clear)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        box.addLayout(header)
        box.addWidget(self.log_view, 1)
        return page

    def _about_page(self) -> QWidget:
        content = QWidget()
        content.setObjectName("page")
        outer = QVBoxLayout(content)
        outer.setContentsMargins(54, 24, 54, 24)
        outer.addStretch()
        card = QFrame()
        card.setObjectName("aboutCard")
        card.setMaximumWidth(790)
        card.setMinimumHeight(580)
        box = QVBoxLayout(card)
        box.setContentsMargins(54, 28, 54, 28)
        box.setSpacing(10)
        mark = QLabel("M")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setObjectName("aboutMark")
        title = QLabel(self.t["about_title"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("pageTitle")
        text = QLabel(self.t["about_text"])
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)
        text.setObjectName("subtitle")
        text.setMinimumHeight(145)
        text.setMaximumWidth(650)
        privacy = QLabel(self.t["privacy_text"])
        privacy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        privacy.setWordWrap(True)
        privacy.setObjectName("aboutNote")
        privacy.setMinimumHeight(88)
        privacy.setMaximumWidth(650)
        creator = QLabel(
            f'{self.t["creator"]}: <b>Alley</b><br>'
            '<a style="color:#ff4b85" href="https://github.com/Alleyv2">github.com/Alleyv2</a>'
        )
        creator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creator.setOpenExternalLinks(True)
        creator.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        creator.setObjectName("creator")
        version = QLabel(self.t["version"])
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setObjectName("eyebrow")
        box.addWidget(mark, 0, Qt.AlignmentFlag.AlignCenter)
        box.addSpacing(8)
        box.addWidget(title)
        box.addWidget(text, 0, Qt.AlignmentFlag.AlignCenter)
        box.addWidget(privacy, 0, Qt.AlignmentFlag.AlignCenter)
        box.addWidget(creator)
        box.addSpacing(4)
        box.addWidget(version)
        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignCenter)
        outer.addStretch()
        return self.scroll_page(content)

    def set_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setChecked(i == index)
        if index == 2:
            self.refresh_logs()

    def change_language(self, language: str) -> None:
        if language == self.lang:
            return
        self.lang = language
        self.t = TEXT[language]
        old = self.centralWidget()
        old.deleteLater()
        self._build()
        self.refresh_status()

    def refresh_status(self) -> None:
        status = current_status()
        core_ready = status["gta"] and status["fix"] and status["runner"] and status["launcher"]
        self.hero_status.setText(("●  " if core_ready else "○  ") + self.t["ready" if core_ready else "needs"])
        self.hero_status.setStyleSheet(f"color: {'#72e5aa' if core_ready else '#ff8ca2'};")
        self.hero_detail.setText(self.t["ready_detail" if core_ready else "needs_detail"])
        self.play_button.setEnabled(core_ready)
        for key, actual in (("steam", status["steam"]), ("gta", status["gta"]), ("fix", status["fix"]), ("launcher", status["launcher"])):
            self.pills[key].set_state(actual, self.t[f"{key}_ready"], self.t[f"{key}_missing"])

    def launch(self) -> None:
        if process_exists("GTA5.exe"):
            QMessageBox.information(self, "Majestic RP", self.t["game_running"])
            return
        QProcess.startDetached(str(APP_DIR / "majestic-fix.sh"), ["--launch"], str(APP_DIR))
        QMessageBox.information(self, "Majestic RP", self.t["launched"])

    def start_install(self) -> None:
        if not (GTA / "GTA5.exe").is_file():
            if QMessageBox.question(self, "GTA V Legacy", self.t["gta_required"]) == QMessageBox.StandardButton.Yes:
                QProcess.startDetached("steam", ["steam://install/271590"])
            return
        source_proton = STEAM / "steamapps/common/Proton - Experimental/proton"
        if not source_proton.is_file():
            if QMessageBox.question(self, "Proton Experimental", self.t["proton_required"]) == QMessageBox.StandardButton.Yes:
                QProcess.startDetached("steam", ["steam://install/1493710"])
            return
        answer = QMessageBox.question(self, self.t["repair"], self.t["confirm_install"])
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.activity.clear()
        self.progress.setRange(0, 0)
        self.install_button.setEnabled(False)
        if find_runner() is None:
            consent = QMessageBox.question(self, self.t["dependency_title"], self.t["dependency_text"])
            if consent != QMessageBox.StandardButton.Yes:
                self.finish_operation(False)
                return
            self.run_process(sys.executable, [str(APP_DIR / "download_dependency.py")], self.install_backend)
        else:
            self.install_backend()

    def install_backend(self) -> None:
        env = QProcessEnvironment.systemEnvironment()
        env.insert("MAJESTIC_FIX_NONINTERACTIVE", "1")
        env.insert("MAJESTIC_FIX_NO_DIALOGS", "1")
        env.insert("MAJESTIC_FIX_FULL_INSTALL", "1")
        self.run_process(str(APP_DIR / "majestic-fix.sh"), ["--install"], self.install_done, env)

    def run_process(self, program: str, args: list[str], callback, environment: QProcessEnvironment | None = None) -> None:
        self.proc = QProcess(self)
        self.proc.setWorkingDirectory(str(APP_DIR))
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        if environment is not None:
            self.proc.setProcessEnvironment(environment)
        self.proc.readyReadStandardOutput.connect(self.read_process_output)
        self.proc.finished.connect(lambda code, status: callback() if code == 0 else self.finish_operation(False))
        self.proc.start(program, args)

    def read_process_output(self) -> None:
        if self.proc is None:
            return
        text = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        if text:
            self.activity.appendPlainText(text.rstrip())

    def install_done(self) -> None:
        subprocess.run([sys.executable, str(APP_DIR / "install_app.py")], check=False)
        self.finish_operation(True)

    def finish_operation(self, success: bool) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(100 if success else 0)
        self.install_button.setEnabled(True)
        self.refresh_status()
        QMessageBox.information(self, self.t["repair"], self.t["success"] if success else self.t["failed"])

    def refresh_logs(self) -> None:
        chunks = []
        for title, path in (("Majestic Multiplayer", PATCH_LOG), ("Majestic Launcher", MAIN_LOG)):
            chunks.append(f"===== {title} =====")
            if path.is_file():
                lines = path.read_text(errors="replace").splitlines()[-180:]
                chunks.extend(line.replace("Authorization:", "Authorization: [hidden]") for line in lines)
            else:
                chunks.append("No log / Лог отсутствует")
            chunks.append("")
        self.log_view.setPlainText("\n".join(chunks))

    def clear_injection_log(self) -> None:
        if process_exists("GTA5.exe") or process_exists("Majestic Launcher.exe"):
            QMessageBox.warning(self, self.t["clear_log"], self.t["clear_running"])
            return
        if not PATCH_LOG.is_file():
            QMessageBox.information(self, self.t["clear_log"], self.t["no_log"])
            return
        if QMessageBox.question(self, self.t["clear_log"], self.t["clear_confirm"]) != QMessageBox.StandardButton.Yes:
            return
        backup_and_clear_log(PATCH_LOG)
        self.refresh_logs()
        QMessageBox.information(self, self.t["clear_log"], self.t["clear_done"])


STYLE = r"""
QWidget { color: #f5f3f7; font-family: "Noto Sans", "Inter", sans-serif; font-size: 14px; }
QMainWindow, QWidget#page, QScrollArea { background: #0c0b10; }
QScrollArea > QWidget > QWidget { background: #0c0b10; }
QFrame#sidebar { background: #141218; border-right: 1px solid #29252f; }
QLabel#brand { color: white; font-size: 24px; font-weight: 900; letter-spacing: 1px; }
QLabel#brandSub { color: #ff2e72; font-size: 13px; font-weight: 800; letter-spacing: 3px; }
QLabel#sideVersion { color: #716b79; font-size: 12px; padding-top: 10px; }
QPushButton { border: none; border-radius: 10px; padding: 11px 16px; font-weight: 700; }
QPushButton:disabled { color: #77717d; background: #242128; }
QPushButton:hover { background: #312c36; }
QPushButton:checked { background: #29222b; color: #ff4b85; border-left: 3px solid #ff2e72; }
QFrame#sidebar QPushButton { text-align: left; color: #aaa4b0; background: transparent; }
QFrame#sidebar QPushButton:hover { color: white; background: #211e25; }
QFrame#sidebar QPushButton:checked { color: white; background: #2a2029; }
QLabel#languageLabel { color: #716b79; font-size: 10px; font-weight: 800; letter-spacing: 1px; padding-bottom: 2px; }
QPushButton#languageButton { color: #918a97; background: #211e25; border: 1px solid #34303a; border-radius: 8px; padding: 8px 10px; text-align: center; }
QPushButton#languageButton:hover { color: white; border-color: #665461; }
QPushButton#languageButton:checked { color: white; background: #d92360; border-color: #ff4b85; }
QLabel#eyebrow { color: #ff4b85; font-size: 12px; font-weight: 800; letter-spacing: 2px; }
QLabel#pageTitle { color: white; font-size: 34px; font-weight: 900; }
QLabel#subtitle { color: #a49eaa; font-size: 15px; line-height: 1.5; }
QFrame#hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2d1724, stop:0.55 #291521, stop:1 #19131a); border: 1px solid #5b273d; border-radius: 18px; }
QLabel#heroTitle { font-size: 21px; font-weight: 900; }
QLabel#heroDetail { color: #bdb5c1; font-size: 14px; }
QPushButton#primaryButton { color: white; background: #ec2365; font-size: 15px; border-radius: 12px; }
QPushButton#primaryButton:hover { background: #ff3d7b; }
QPushButton#secondaryButton { color: #f7eaf0; background: #302a33; border: 1px solid #443b47; }
QPushButton#secondaryButton:hover { border-color: #ff4b85; background: #3a2c35; }
QPushButton#dangerButton { color: #ff9db4; background: #2c1c23; border: 1px solid #5d2a3d; }
QPushButton#dangerButton:hover { color: white; background: #7d2345; border-color: #ff4b85; }
QFrame#statusPill { background: #18161c; border: 1px solid #2c2831; border-radius: 12px; }
QLabel#sectionTitle { color: white; font-size: 18px; font-weight: 800; margin-top: 4px; }
QFrame#actionCard, QFrame#panel { background: #18161c; border: 1px solid #2c2831; border-radius: 16px; }
QFrame#actionCard:hover { border-color: #5d3345; background: #1d191f; }
QLabel#cardIcon { color: #ff4b85; font-size: 27px; font-weight: 800; }
QLabel#cardTitle { color: white; font-size: 18px; font-weight: 800; }
QLabel#muted { color: #99929f; }
QLabel#numberBadge { color: white; background: #d92360; border-radius: 17px; font-weight: 900; qproperty-alignment: AlignCenter; }
QLabel#stepText { color: #eeeaf0; font-size: 15px; font-weight: 650; }
QProgressBar { background: #221e25; border: none; border-radius: 5px; height: 10px; }
QProgressBar::chunk { background: #ed2868; border-radius: 5px; }
QPlainTextEdit { color: #cfc8d2; background: #111015; border: 1px solid #2c2831; border-radius: 12px; padding: 13px; font-family: "JetBrains Mono", monospace; font-size: 12px; selection-background-color: #a91f50; }
QLabel#aboutMark { color: white; background: #ed2868; border-radius: 38px; font-size: 42px; font-weight: 900; min-width: 76px; min-height: 76px; max-width: 76px; max-height: 76px; qproperty-alignment: AlignCenter; }
QFrame#aboutCard { background: #151319; border: 1px solid #302a34; border-radius: 20px; }
QLabel#aboutNote { color: #8e8794; background: #1e1a21; border: 1px solid #302b34; border-radius: 10px; padding: 12px 16px; }
QLabel#creator { color: #d7d0da; font-size: 14px; padding: 8px; }
QLabel#creator a { color: #ff4b85; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: #3a343f; border-radius: 5px; min-height: 35px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=("ru", "en"), default="ru" if os.getenv("LANG", "").startswith("ru") else "en")
    parser.add_argument("--page", choices=("overview", "install", "logs", "about"), default="overview")
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName("Majestic RP Linux Fix")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Noto Sans", 10))
    window = MainWindow(args.lang)
    window.set_page({"overview": 0, "install": 1, "logs": 2, "about": 3}[args.page])
    window.show()
    if args.screenshot:
        def capture() -> None:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            window.grab().save(str(args.screenshot))
            app.quit()
        QTimer.singleShot(900, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
