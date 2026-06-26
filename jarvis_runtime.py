from __future__ import annotations

# Compatibility layer for legacy imports. Prefer jarvis.core.version and core runtime modules in new code.

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from jarvis.core.version import APP_CODENAME, APP_SUBTITLE, APP_TITLE, APP_VERSION


if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent
PORTABLE_MARKER = APP_DIR / "portable_mode.flag"


def resolve_data_dir() -> tuple[Path, str]:
    forced_portable = os.environ.get("JARVIS_PORTABLE", "").strip() == "1"
    if PORTABLE_MARKER.exists() or forced_portable:
        base = APP_DIR
        mode = "portable"
    elif getattr(sys, "frozen", False) and os.name == "nt":
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
        base = appdata / "JARVIS"
        mode = "installed"
    else:
        base = APP_DIR
        mode = "portable"
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, mode


def get_portable_base_dir() -> Path:
    return APP_DIR


def get_installed_base_dir() -> Path:
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    return appdata / "JARVIS"


def get_data_dir_for_mode(mode: str) -> Path:
    mode = str(mode or "portable").strip().lower()
    base = get_installed_base_dir() if mode == "installed" else get_portable_base_dir()
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR, STORAGE_MODE = resolve_data_dir()
CONFIG_PATH = DATA_DIR / "config.json"
NOTES_PATH = DATA_DIR / "notes.txt"
HISTORY_PATH = DATA_DIR / "history.txt"
REMINDERS_PATH = DATA_DIR / "reminders.json"
MEMORY_PATH = DATA_DIR / "memory_profile.json"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
AUTOSAVE_PROFILE_PATH = BACKUP_DIR / "jarvis_profile_autosave.json"
SESSION_STATE_PATH = DATA_DIR / "ui_session.json"
SYSTEM_LOG_PATH = DATA_DIR / "system_events.log"
DATA_HEALTH_REPORT_PATH = DATA_DIR / "data_health_report.json"
STARTUP_CRASH_LOG_PATH = DATA_DIR / "startup_crash.log"
FIRST_RUN_MARKER = DATA_DIR / ".first_run_complete"

TEMPLATES_DIR = DATA_DIR / "templates"


def _root_template_path(name: str) -> Path:
    return APP_DIR / name


def _data_template_path(name: str) -> Path:
    return TEMPLATES_DIR / name


def _copy_if_missing(src: Path, dst: Path) -> bool:
    if dst.exists() or not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def ensure_runtime_files() -> list[str]:
    created: list[str] = []
    templates = {
        CONFIG_PATH: [_root_template_path("config.example.json")],
        NOTES_PATH: [_data_template_path("notes.txt")],
        HISTORY_PATH: [_data_template_path("history.txt")],
        REMINDERS_PATH: [_data_template_path("reminders.json")],
        MEMORY_PATH: [_data_template_path("memory_profile.json")],
    }
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for target, sources in templates.items():
        if target.exists():
            continue
        for src in sources:
            if _copy_if_missing(src, target):
                created.append(target.name)
                break
    if not SESSION_STATE_PATH.exists():
        save_json_file(SESSION_STATE_PATH, {})
        created.append(SESSION_STATE_PATH.name)
    if not SYSTEM_LOG_PATH.exists():
        SYSTEM_LOG_PATH.write_text("", encoding="utf-8")
        created.append(SYSTEM_LOG_PATH.name)
    # First-run marker must be created only after the wizard is actually completed.
    # Creating it during bootstrap makes the first-run state inconsistent.
    return created


def load_json_file(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def log_app_exception(context: str, exc: Exception | None = None, extra: str = "") -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"[{stamp}] {context}"]
    if exc is not None:
        parts.append(f"{type(exc).__name__}: {exc}")
    if extra:
        parts.append(extra)
    payload = "\n".join(parts).strip() + "\n\n"
    try:
        STARTUP_CRASH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STARTUP_CRASH_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(payload)
            if exc is not None:
                fh.write(traceback.format_exc())
                fh.write("\n")
    except Exception:
        pass
