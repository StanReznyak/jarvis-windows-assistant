
import asyncio
import json
import math
import os
import queue
import subprocess
import traceback
import re
import shutil
import threading
import time
import webbrowser
import difflib
import sys
import ctypes

try:
    import winsound
except Exception:
    winsound = None

try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None
    ImageDraw = None

try:
    import pystray
except Exception:
    pystray = None
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from jarvis.core.config_migration import (
    STARTUP_PROMPTS_MIGRATION_KEY,
    STARTUP_PROMPTS_MIGRATION_VERSION,
    migrate_startup_prompt_settings,
)

from jarvis_runtime import (
    APP_DIR,
    APP_VERSION,
    APP_CODENAME,
    APP_TITLE,
    APP_SUBTITLE,
    PORTABLE_MARKER,
    DATA_DIR,
    STORAGE_MODE,
    CONFIG_PATH,
    NOTES_PATH,
    HISTORY_PATH,
    REMINDERS_PATH,
    MEMORY_PATH,
    BACKUP_DIR,
    AUTOSAVE_PROFILE_PATH,
    SESSION_STATE_PATH,
    SYSTEM_LOG_PATH,
    DATA_HEALTH_REPORT_PATH,
    STARTUP_CRASH_LOG_PATH,
    FIRST_RUN_MARKER,
    get_portable_base_dir,
    get_installed_base_dir,
    get_data_dir_for_mode,
    log_app_exception,
    load_json_file,
    save_json_file,
    ensure_runtime_files,
 )

FIRST_RUN_CREATED = ensure_runtime_files()

from jarvis.model_chat import (
    ask_model,
    looks_like_model_request,
    strip_model_prefix,
    get_cloud_api_key,
)

from command_core import (
    SUPPORTED_INTENTS,
    INTENT_DEFAULTS,
    BRAND_ALIASES,
    ACTION_ALIASES,
    MEMORY_STOPWORDS,
    build_command_help_text,
    normalize_text,
    compact_text,
    cleanup_memory_value,
    looks_like_bad_memory_value,
    extract_after_prefix,
    fuzzy_normalize,
    wake_variants_from_value,
    strip_wake_words,
    has_wake_word,
    extract_wake_tail,
    is_free_text_command,
    phrase_similarity,
)

DEFAULT_CONFIG = {
    "user_name": "Пользователь",
    "assistant_name": "JARVIS",
    "telegram_path": "",
    "discord_path": "",
    "steam_path": "",
    "auto_tts": True,
    "auto_start_voice": True,
    "tts_mode": "edge_female",
    "overlay_enabled": False,
    "visualizer_enabled": True,
    "theme": "cyan",
    "hud_mode": False,
    "window_opacity": 1.0,
    "overlay_opacity": 0.88,
    "splash_opacity": 0.96,
    "hud_opacity": 0.82,
    "always_on_top": False,
    "overlay_topmost": True,
    "overlay_scale": 1.0,
    "quick_bar_topmost": True,
    "minimize_to_tray": True,
    "close_to_tray": True,
    "start_minimized": False,
    "autostart_enabled": False,
    "restore_last_session": False,
    "startup_recovery_prompt": False,
    "toast_notifications": True,
    "system_event_toasts": True,
    "favorite_apps": {},
    "favorite_sites": {
        "гугл": "https://www.google.com",
        "ютуб": "https://www.youtube.com",
        "вк": "https://vk.com",
        "vk": "https://vk.com",
        "github": "https://github.com",
        "гитхаб": "https://github.com",
        "яндекс": "https://ya.ru",
        "яндекс музыка": "https://music.yandex.ru",
        "яндексмузыка": "https://music.yandex.ru",
        "музыка": "https://music.yandex.ru"
    },
    "launcher_order_apps": [],
    "launcher_order_sites": [],
    "launcher_app_icons": {},
    "launcher_site_icons": {},
    "aliases": {},
    "glass_preset": "glass",
    "tts_preferred_engine": "auto",
    "custom_intents": {},
    "command_core_mode": "smart",
    "wake_word_enabled": True,
    "wake_word": "джарвис",
    "first_run_completed": True,
    "install_mode": STORAGE_MODE,
    "show_first_run_wizard": False,
    "license_accepted": True,
    "last_data_dir": str(DATA_DIR),
    "reminder_alert_repeats": 5,
    "reminder_alert_interval_sec": 5.0,
    "reminder_melody_mode": "loud",
    "voice_input_engine": "vosk",
    "speechkit_api_key": "",
    "speechkit_folder_id": "",
    "speechkit_lang": "ru-RU",
    "speechkit_topic": "general",
    "speechkit_silence_ms": 900,
    "speechkit_max_phrase_sec": 8.0,
    "whisper_model_size": "tiny",
    "whisper_compute_type": "int8",
    "whisper_device": "auto",
    "whisper_silence_ms": 900,
    "whisper_max_phrase_sec": 8.0,
    "whisper_cpp_cli_path": "",
    "whisper_cpp_model_path": "",
    "whisper_cpp_language": "ru",
    "whisper_cpp_threads": 4,
    "whisper_cpp_processors": 1,
    "whisper_cpp_silence_ms": 900,
    "whisper_cpp_max_phrase_sec": 8.0,
    "model_answers_enabled": True,
    "model_fallback_unknown": True,
    "model_provider": "auto",
    "show_model_setup_wizard": False,
    "local_model_setup_completed": True,
    "startup_prompts_migration": STARTUP_PROMPTS_MIGRATION_VERSION,
    "ollama_base_url": "http://127.0.0.1:11434",
    "ollama_model": "llama3.2:1b",
    "ollama_max_output_tokens": 500,
    "ollama_timeout_sec": 60,
    "cloud_api_key": "",
    "cloud_model": "gpt-5-mini",
    "cloud_max_output_tokens": 500,
}


BG = "#060d17"
PANEL = "#0b1523"
PANEL_2 = "#101e31"
CARD = "#122136"
CARD_ALT = "#0f1b2c"
ACCENT = "#73e0ff"
ACCENT_2 = "#8df7b8"
TEXT = "#f4f8ff"
MUTED = "#90a4c3"
BORDER = "#1d3248"
WARN = "#ffd27a"
DANGER = "#ff7f96"


THEMES = {
    "cyan": {
        "accent": "#59d8ff",
        "accent_2": "#7CFC90",
        "danger": "#ff7b7b",
        "warn": "#ffcc66",
        "name": "Cyan JARVIS",
    },
    "red": {
        "accent": "#ff5c7a",
        "accent_2": "#ffb86c",
        "danger": "#ff6b6b",
        "warn": "#ffd166",
        "name": "Red Combat",
    },
    "green": {
        "accent": "#4df5a6",
        "accent_2": "#97ff7c",
        "danger": "#ff8f8f",
        "warn": "#ffe27a",
        "name": "Green Reactor",
    },
}

SCENARIOS = {
    "work": {
        "title": "Рабочий режим",
        "command": "рабочий режим",
        "apps": ["telegram", "discord"],
        "theme": "cyan",
        "overlay": True,
        "voice": True,
        "message": "Включаю рабочий режим."
    },
    "game": {
        "title": "Игровой режим",
        "command": "игровой режим",
        "apps": ["discord", "steam"],
        "theme": "red",
        "overlay": True,
        "voice": True,
        "message": "Включаю игровой режим."
    },
    "silent": {
        "title": "Тихий режим",
        "command": "тихий режим",
        "apps": [],
        "theme": "green",
        "overlay": True,
        "voice": False,
        "message": "Включаю тихий режим."
    },
}


def load_config():
    data = load_json_file(CONFIG_PATH, default=None)
    if isinstance(data, dict):
        stored, startup_prompts_migrated = migrate_startup_prompt_settings(data)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(stored)
        if not stored.get("last_data_dir"):
            cfg["last_data_dir"] = str(DATA_DIR)
        if not stored.get("install_mode"):
            cfg["install_mode"] = STORAGE_MODE
        # In earlier test builds auto_start_voice could be saved as False.
        # For this desktop release the voice listener should start by itself.
        # If the user later turns it off in settings, we keep that choice using
        # auto_start_voice_user_disabled=True.
        if data.get("auto_start_voice") is False and data.get("auto_start_voice_user_disabled") is not True:
            cfg["auto_start_voice"] = True
        if getattr(sys, "frozen", False):
            cfg["wake_word_enabled"] = True
            cfg["wake_word"] = normalize_text(cfg.get("wake_word", "джарвис")) or "джарвис"
        if startup_prompts_migrated:
            save_json_file(CONFIG_PATH, cfg)
        return cfg
    fresh = DEFAULT_CONFIG.copy()
    fresh["last_data_dir"] = str(DATA_DIR)
    fresh["install_mode"] = STORAGE_MODE
    if getattr(sys, "frozen", False):
        fresh["wake_word_enabled"] = True
        fresh["wake_word"] = normalize_text(fresh.get("wake_word", "джарвис")) or "джарвис"
    save_json_file(CONFIG_PATH, fresh)
    return fresh


def save_config(cfg):
    cfg["last_data_dir"] = str(DATA_DIR)
    cfg["install_mode"] = cfg.get("install_mode") or STORAGE_MODE
    save_json_file(CONFIG_PATH, cfg)

def load_reminders():
    data = load_json_file(REMINDERS_PATH, default=[])
    if isinstance(data, list):
        return data
    save_json_file(REMINDERS_PATH, [])
    return []


def save_reminders(items):
    save_json_file(REMINDERS_PATH, items)


def get_candidate_reminder_paths():
    paths = []
    for candidate in [REMINDERS_PATH, get_portable_base_dir() / "data" / "reminders.json", get_installed_base_dir() / "data" / "reminders.json"]:
        try:
            candidate = Path(candidate)
        except Exception:
            continue
        if candidate not in paths:
            paths.append(candidate)
    return paths


def load_reminders_any():
    merged = []
    seen = set()
    for path in get_candidate_reminder_paths():
        data = load_json_file(path, default=[])
        if not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            rid = str(item.get("id") or "").strip()
            when = str(item.get("when") or "").strip()
            text = str(item.get("text") or "").strip()
            key = rid or f"{when}|{text}|{int(bool(item.get('done')))}"
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return sorted(merged, key=lambda x: x.get("when", ""))


def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def parse_simple_reminder(text: str):
    return parse_natural_reminder(text)


def _salvage_reminder_phrase(text: str) -> str:
    t = normalize_text(text)
    if not t:
        return ""
    triggers = [
        "напомни", "напоминай", "удали", "удалить", "убери", "убрать",
        "покажи напоминания", "покажи напоминалки", "мои напоминания", "напоминания"
    ]
    best = None
    for trig in triggers:
        idx = t.find(trig)
        if idx != -1 and (best is None or idx < best[0]):
            best = (idx, trig)
    if best and best[0] > 0:
        t = t[best[0]:].strip()
    t = re.sub(r"^(какая|какой|какое|какие|скажи|слушай|пожалуйста|короче|ну|а)\s+", "", t).strip()
    return t


def _normalize_reminder_command_text(text: str) -> str:
    t = _salvage_reminder_phrase(text)
    if not t:
        return ""
    replacements = [
        (r"^напоминани[ея]\s+", "напомни "),
        (r"^напомнить\s+", "напомни "),
        (r"^напомина[йя]\s+", "напомни "),
        (r"^на\s+помни\s+", "напомни "),
        (r"^на\s+по\s+мни\s+", "напомни "),
        (r"^на\s+по\s+мне\s+", "напомни мне "),
        (r"^на\s+по\s+меня\s+", "напомни мне "),
        (r"^на\s+по\s+мя\s+", "напомни мне "),
        (r"^напомни\s+голоса\s+", "напомни "),
        (r"^удалить\s+", "удали "),
        (r"^убрать\s+", "убери "),
    ]
    for pattern, repl in replacements:
        t = re.sub(pattern, repl, t)
    t = re.sub(r"\bчерез\s+минуту\b", "через 1 минуту", t)
    t = re.sub(r"\bчерез\s+одну\s+минуту\b", "через 1 минуту", t)
    t = re.sub(r"\bчерез\s+час\b", "через 1 час", t)
    t = re.sub(r"\bчерез\s+один\s+час\b", "через 1 час", t)
    t = re.sub(r"\bчерез\s+секунду\b", "через 1 секунду", t)
    t = re.sub(r"\bчерез\s+одну\s+секунду\b", "через 1 секунду", t)
    t = re.sub(r"\bнапоминани[ея]\b", "напоминание", t)
    t = re.sub(r"\bнапоминалки\b", "напоминания", t)
    t = re.sub(r"\bде\s+сайт\s+unk\b", "", t).strip()
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _strip_leading_filler_words(text: str) -> str:
    t = normalize_text(text)
    fillers = ["мне", "пожалуйста", "ка", "голосом", "голоса"]
    changed = True
    while changed and t:
        changed = False
        for word in fillers:
            if t.startswith(word + " "):
                t = t[len(word):].strip()
                changed = True
    return t


def _parse_russian_number(raw: str | None):
    if raw is None:
        return None
    value = normalize_text(raw).replace('-', ' ').strip()
    if not value:
        return None
    if value.isdigit():
        return int(value)
    units = {
        'ноль': 0,
        'один': 1, 'одна': 1, 'одно': 1,
        'два': 2, 'две': 2, 'три': 3, 'четыре': 4,
        'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
        'десять': 10,
        'одиннадцать': 11, 'одинадцать': 11,
        'двенадцать': 12, 'двинадцать': 12,
        'тринадцать': 13,
        'четырнадцать': 14,
        'пятнадцать': 15, 'пятнацать': 15,
        'шестнадцать': 16, 'шеснадцать': 16,
        'семнадцать': 17,
        'восемнадцать': 18,
        'девятнадцать': 19,
    }
    tens = {
        'двадцать': 20,
        'тридцать': 30, 'трицать': 30,
        'сорок': 40,
        'пятьдесят': 50,
    }
    total = 0
    for token in value.split():
        if token in units:
            total += units[token]
        elif token in tens:
            total += tens[token]
        else:
            return None
    return total if total > 0 or value == 'ноль' else None


def _looks_like_reminder_request(text: str) -> bool:
    t = _normalize_reminder_command_text(text)
    if not t:
        return False
    reminder_words = ["напомни", "напомнить", "напоминай", "напоминания", "напоминание", "удали", "убери"]
    time_words = ["через", "завтра", "сегодня", "послезавтра", "утром", "днем", "днём", "вечером", "ночью", "минут", "минута", "минуты", "час", "часа", "часов", "в "]
    return any(word in t for word in reminder_words) or any(word in t for word in time_words)


def _looks_like_asr_garbage(text: str) -> bool:
    t = normalize_text(text)
    if not t:
        return True
    if _looks_like_reminder_request(t):
        return False
    keep_markers = [
        "телеграм", "телеграмм", "telegram", "дискорд", "discord", "стим", "steam", "ютуб", "youtube",
        "какая дата", "который час", "сколько времени", "память", "заметки", "покажи", "запомни"
    ]
    compact = compact_text(t)
    if any(compact_text(marker) in compact for marker in keep_markers):
        # mixed garbage like 'режим тишина дисс открой юту' should still be treated as garbage if overloaded
        tokens = t.split()
        garbage_words = {"режим", "тишина", "дисс", "дис", "юту", "на", "память", "число", "речь", "unk", "сайт"}
        garbage_hits = sum(1 for token in tokens if token in garbage_words)
        return len(tokens) >= 5 and garbage_hits >= 2 and not any(marker in t for marker in ["какая дата", "который час", "сколько времени"])
    tokens = t.split()
    garbage_words = {"режим", "тишина", "дисс", "дис", "юту", "unk", "сайт", "речь", "число", "память"}
    return len(tokens) >= 4 and sum(1 for token in tokens if token in garbage_words) >= 2


def _strip_noise_tokens(text: str) -> str:
    t = normalize_text(text)
    if not t:
        return ""
    noise = {
        "какая", "какой", "какое", "какие", "скажи", "слушай", "пожалуйста", "короче", "ну", "а",
        "открой", "открыть", "речь", "работа", "сайт", "включена", "включить", "режим", "память",
        "число", "на", "по", "меня", "unk", "де", "voice", "guard"
    }
    parts = [w for w in t.split() if w not in noise]
    return " ".join(parts).strip()


def _coerce_to_reminder_phrase(text: str) -> str:
    t = _normalize_reminder_command_text(text)
    if not t:
        return ""
    if t.startswith(("напомни", "удали", "убери", "покажи напоминания", "мои напоминания", "напоминания")):
        return t
    if any(token in t for token in ["через", "завтра", "сегодня", "послезавтра"]):
        cleaned = _strip_noise_tokens(t)
        if not cleaned:
            cleaned = t
        if not cleaned.startswith("напомни"):
            cleaned = "напомни " + cleaned
        return re.sub(r"\s+", " ", cleaned).strip()
    return t


def _extract_relative_delta(text: str):
    t = _normalize_reminder_command_text(text)
    if not (t.startswith("напомни") or t.startswith("напомнить")):
        return None, None
    if "через" not in t:
        return None, None
    tail = t.split("через", 1)[1].strip()
    if not tail:
        return None, None

    units = [
        ("hours", ["час", "часа", "часов"]),
        ("minutes", ["минуту", "минута", "минуты", "минут"]),
        ("seconds", ["секунду", "секунда", "секунды", "секунд"]),
    ]
    values = {"hours": 0, "minutes": 0, "seconds": 0}
    rest = tail

    for key, forms in units:
        forms_group = "|".join(forms)
        m = re.search(rf"(?P<num>(?:\d+|[а-яё-]+(?:\s+[а-яё-]+)*))?\s*(?P<unit>{forms_group})\b", rest)
        if not m:
            continue
        raw_num = (m.group("num") or "").strip()
        unit = m.group("unit")
        parsed = _parse_russian_number(raw_num) if raw_num else 1
        if parsed is None:
            parsed = 1 if unit in {"минуту", "час", "секунду"} else 0
        values[key] = max(values[key], int(parsed or 0))
        rest = (rest[:m.start()] + " " + rest[m.end():]).strip()

    body = _strip_leading_filler_words(rest)
    if not body or not any(values.values()):
        return None, None
    return datetime.now() + timedelta(hours=values["hours"], minutes=values["minutes"], seconds=values["seconds"]), body


def _part_of_day_hour(token: str | None):
    mapping = {
        "утром": 9,
        "днем": 14,
        "днём": 14,
        "вечером": 19,
        "ночью": 23,
    }
    return mapping.get((token or '').strip())


def _build_day_target(days_ahead: int, part_of_day: str | None, body: str):
    now = datetime.now()
    hour = _part_of_day_hour(part_of_day)
    minute = 0
    if hour is None:
        hour = 9
    target = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target, body.strip()


def _adjust_hour_by_period(hour: int, marker: str | None):
    marker = normalize_text(marker or "")
    if not marker:
        return hour
    if marker in {"вечера", "дня", "днем", "днём"} and 1 <= hour <= 11:
        return hour + 12
    if marker == "ночи":
        if hour == 12:
            return 0
        if 1 <= hour <= 5:
            return hour
        if 6 <= hour <= 11:
            return hour + 12
    if marker == "утра" and hour == 12:
        return 0
    return hour


def _parse_hour_minute(hour_raw: str | None, minute_raw: str | None = None, marker: str | None = None):
    hour = _parse_russian_number(hour_raw)
    minute = _parse_russian_number(minute_raw) if minute_raw else 0
    if hour is None:
        return None, None
    if minute is None:
        minute = 0
    hour = _adjust_hour_by_period(int(hour), marker)
    if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
        return None, None
    return int(hour), int(minute)


def _extract_absolute_day_time(text: str):
    t = _coerce_to_reminder_phrase(text)
    if not (t.startswith("напомни") or t.startswith("напомнить")):
        return None, None

    m = re.search(
        r"напомн(?:и|ить)(?:\s+мне)?\s+(?P<day>сегодня|завтра|послезавтра)(?:\s+в)?\s+"
        r"(?P<hour>\d{1,2}|[а-яё-]+)"
        r"(?:\s*[:.]\s*(?P<minute_colon>\d{1,2}))?"
        r"(?:\s+(?P<minute_word>\d{1,2}|[а-яё-]+)(?:\s*(?:минута|минуту|минуты|минут))?)?"
        r"\s*(?:час|часа|часов)?\s*"
        r"(?P<period>утра|вечера|дня|днем|днём|ночи)?\s+"
        r"(?P<body>.+)$",
        t,
    )
    if m:
        hour_token = m.group("hour")
        minute_token = m.group("minute_colon") or m.group("minute_word")
        period_token = m.group("period")
        body = _strip_leading_filler_words((m.group("body") or "").strip())
        hour, minute_val = _parse_hour_minute(hour_token, minute_token, period_token)
        if hour is not None and body:
            base = datetime.now()
            day_token = m.group("day")
            days_ahead = 2 if day_token == "послезавтра" else 1 if day_token == "завтра" else 0
            target = (base + timedelta(days=days_ahead)).replace(hour=hour, minute=minute_val, second=0, microsecond=0)
            if days_ahead == 0 and target <= base:
                target += timedelta(days=1)
            return target, body

    tokens = t.split()
    if not tokens:
        return None, None

    idx = 1
    if idx < len(tokens) and tokens[idx] == "мне":
        idx += 1

    day_token = None
    if idx < len(tokens) and tokens[idx] in {"сегодня", "завтра", "послезавтра"}:
        day_token = tokens[idx]
        idx += 1

    if idx < len(tokens) and tokens[idx] == "в":
        idx += 1

    if idx >= len(tokens):
        return None, None

    hour_token = tokens[idx]
    idx += 1
    if not re.fullmatch(r"\d{1,2}|[а-яё-]+|\d{1,2}:\d{2}", hour_token):
        return None, None

    minute_token = None
    period_token = None

    if ":" in hour_token:
        try:
            hour_token, minute_token = hour_token.split(":", 1)
        except Exception:
            return None, None

    if idx < len(tokens) and tokens[idx] in {"час", "часа", "часов"}:
        idx += 1
    elif idx < len(tokens) and re.fullmatch(r"\d{1,2}|[а-яё-]+", tokens[idx]):
        candidate = tokens[idx]
        next_token = tokens[idx + 1] if idx + 1 < len(tokens) else ""
        if next_token in {"час", "часа", "часов", "утра", "вечера", "дня", "днем", "днём", "ночи", "минута", "минуты", "минут", "минуту"} or re.fullmatch(r"\d{1,2}", candidate) or _parse_russian_number(candidate) is not None:
            minute_token = candidate
            idx += 1
            if idx < len(tokens) and tokens[idx] in {"час", "часа", "часов", "минута", "минуты", "минут", "минуту"}:
                idx += 1

    if idx < len(tokens) and tokens[idx] in {"утра", "вечера", "дня", "днем", "днём", "ночи"}:
        period_token = tokens[idx]
        idx += 1

    body = _strip_leading_filler_words(" ".join(tokens[idx:]).strip())
    if not body:
        return None, None

    hour, minute_val = _parse_hour_minute(hour_token, minute_token, period_token)
    if hour is None:
        return None, None

    base = datetime.now()
    if day_token == "послезавтра":
        days_ahead = 2
    elif day_token == "завтра":
        days_ahead = 1
    elif day_token == "сегодня":
        days_ahead = 0
    else:
        days_ahead = None

    target = base.replace(hour=hour, minute=minute_val, second=0, microsecond=0)
    if days_ahead is None:
        if target <= base:
            target += timedelta(days=1)
    else:
        target = (base + timedelta(days=days_ahead)).replace(hour=hour, minute=minute_val, second=0, microsecond=0)
        if days_ahead == 0 and target <= base:
            target += timedelta(days=1)
    return target, body

def parse_natural_reminder(text: str):
    t = _coerce_to_reminder_phrase(text)
    rel_dt, rel_body = _extract_relative_delta(t)
    if rel_dt and rel_body:
        return rel_dt, rel_body

    abs_dt, abs_body = _extract_absolute_day_time(t)
    if abs_dt and abs_body:
        return abs_dt, abs_body

    day_patterns = [
        (r"напомни(?:\s+мне)?\s+послезавтра(?:\s+(утром|днем|днём|вечером|ночью))?\s+(.+)", 2),
        (r"напомни(?:\s+мне)?\s+завтра(?:\s+(утром|днем|днём|вечером|ночью))?\s+(.+)", 1),
        (r"напомни(?:\s+мне)?\s+сегодня(?:\s+(утром|днем|днём|вечером|ночью))?\s+(.+)", 0),
    ]
    for pattern, days_ahead in day_patterns:
        m = re.match(pattern, t)
        if not m:
            continue
        part = m.group(1)
        body = _strip_leading_filler_words(m.group(2).strip())
        return _build_day_target(days_ahead, part, body)

    return None, None


def parse_loose_reminder(text: str):
    t = _normalize_reminder_command_text(text)
    if not t:
        return None, None
    anchors = ["напомни", "напомнить", "напоминай", "через", "завтра", "сегодня", "послезавтра", "в "]
    positions = [t.find(a) for a in anchors if t.find(a) != -1]
    if positions:
        t = t[min(positions):].strip()
    if t.startswith("через "):
        t = "напомни " + t
    dt, body = parse_natural_reminder(t)
    if dt and body:
        return dt, body
    if "через" in t:
        tail = t.split("через", 1)[1].strip()
        m = re.search(
            r"(?:(?P<hours>(?:\d+|[а-яё\s-]+?))\s*(?:час|часа|часов))?\s*"
            r"(?:(?P<minutes>(?:\d+|[а-яё\s-]+?))\s*(?:минуту|минут|минута|минуты))?\s*"
            r"(?:(?P<seconds>(?:\d+|[а-яё\s-]+?))\s*(?:секунду|секунд|секунда|секунды))?\s+(?P<body>.+)",
            tail,
        )
        if m:
            hours = _parse_russian_number(m.group('hours')) or 0
            minutes = _parse_russian_number(m.group('minutes')) or 0
            seconds = _parse_russian_number(m.group('seconds')) or 0
            body = _strip_leading_filler_words((m.group('body') or '').strip())
            if body and (hours or minutes or seconds):
                return datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds), body
    abs_dt, abs_body = _extract_absolute_day_time(t)
    if abs_dt and abs_body:
        return abs_dt, abs_body
    day_match = re.search(r"(?:завтра|сегодня|послезавтра)(?:\s+(утром|днем|днём|вечером|ночью))?\s+(.+)", t)
    if day_match:
        token_part = day_match.group(1)
        body = _strip_leading_filler_words(day_match.group(2).strip())
        anchor_text = day_match.group(0)
        days = 2 if anchor_text.startswith("послезавтра") else 1 if anchor_text.startswith("завтра") else 0
        if body:
            return _build_day_target(days, token_part, body)
    return None, None



def parse_unified_reminder_request(text: str):
    t = _normalize_reminder_command_text(text)
    if not t:
        return None

    delete_cmd = parse_reminder_delete_command(t)
    if delete_cmd:
        return {"kind": "delete", "command": delete_cmd, "text": t}

    compact = compact_text(t)
    if compact in {"напоминания", "показатьнапоминания", "моинапоминания", "покажинапоминания", "покажинапоминалки"} or t in {"напоминания", "мои напоминания", "покажи напоминания", "покажи напоминалки", "покажи напоминание"}:
        return {"kind": "show", "text": t}

    reminderish = any(token in t for token in ["напомни", "напомнить", "напоминай", "напоминание", "напоминания", "через", "завтра", "сегодня", "послезавтра"])
    if not reminderish:
        return None

    dt, body = parse_natural_reminder(t)
    if not (dt and body):
        dt, body = parse_loose_reminder(t)
    if dt and body:
        return {"kind": "create", "dt": dt, "body": body, "text": t}

    return {"kind": "unclear", "text": t}

def parse_reminder_delete_command(text: str):
    t = _normalize_reminder_command_text(text)
    if not t:
        return None
    compact = re.sub(r"\s+", " ", t).strip()
    has_delete = bool(re.search(r"\b(?:удали|убери|удалить|убрать|отмени|отменить|сотри|стереть|снеси)\b", compact))
    has_reminder = "напомин" in compact
    if not has_delete:
        return None

    if re.search(r"\bпоследн(?:ее|ий|ие|яя|юю|его|ем|им|их)?\b", compact):
        return {"mode": "last"}
    if re.search(r"\b(?:все|всё)\b", compact) and (has_reminder or len(compact.split()) <= 5):
        return {"mode": "all"}

    m = re.search(r"\bномер\s+(\d+)\b", compact)
    if m:
        return {"mode": "index", "index": int(m.group(1))}

    payload = re.sub(r"^.*?\b(?:удали|убери|удалить|убрать|отмени|отменить|сотри|стереть|снеси)\b\s*", "", compact).strip()
    payload = re.sub(r"^напоминани(?:е|я)\s*", "", payload).strip()
    payload = _strip_leading_filler_words(payload)
    payload = re.sub(r"^(?:де|это|эти|эту|мне|их)\s*", "", payload).strip()

    if not payload or payload in {"все", "всё", "последнее", "последний", "последние", "последних", "напоминание", "напоминания"}:
        if re.search(r"\b(?:все|всё)\b", compact):
            return {"mode": "all"}
        return {"mode": "last"}

    if has_reminder and len(payload.split()) <= 2:
        cleaned = re.sub(r"\b(?:телегу|телега|телеграм|телеги|тг|де|это|эти|эту|их|его|её|ее|мне|напоминание|напоминания)\b", " ", payload)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned:
            return {"mode": "last"}
        payload = cleaned

    return {"mode": "text", "text": payload}

def format_reminder_item(item):
    when = item.get("when", "")
    try:
        dt = datetime.fromisoformat(when)
        when_text = dt.strftime("%d.%m %H:%M")
    except Exception:
        when_text = when
    status = "✓" if item.get("done") else "•"
    return f"{status} {when_text} — {item.get('text','')}"


def load_memory_profile():
    default = {
        "profile": {"name": "", "nickname": "", "city": "", "about": ""},
        "facts": [],
        "favorites": {"sites": {}, "apps": {}}
    }
    data = load_json_file(MEMORY_PATH, default=None)
    if isinstance(data, dict):
        default["profile"].update(data.get("profile", {}) or {})
        favorites = data.get("favorites", {}) or {}
        default["favorites"]["sites"].update(favorites.get("sites", {}) or {})
        default["favorites"]["apps"].update(favorites.get("apps", {}) or {})
        facts = data.get("facts", [])
        if isinstance(facts, list):
            default["facts"] = facts
        return default
    save_json_file(MEMORY_PATH, default)
    return default


def save_memory_profile(data):
    save_json_file(MEMORY_PATH, data)


def parse_recurring_reminder(text: str):
    t = normalize_text(text)
    patterns = [
        (r"напоминай\s+каждый\s+день\s+в\s+(\d{1,2})(?::(\d{2}))?\s+(.+)", "daily"),
        (r"напоминай\s+по\s+будням\s+в\s+(\d{1,2})(?::(\d{2}))?\s+(.+)", "weekdays"),
    ]
    for pattern, mode in patterns:
        m = re.match(pattern, t)
        if not m:
            continue
        hour = int(m.group(1)); minute = int(m.group(2) or 0)
        body = m.group(3).strip()
        target = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= datetime.now():
            target += timedelta(days=1)
        if mode == "weekdays":
            while target.weekday() >= 5:
                target += timedelta(days=1)
        return target, body, mode
    return None, None, None


def next_recurring_time(current_dt: datetime, repeat: str):
    if repeat == "daily":
        return current_dt + timedelta(days=1)
    if repeat == "weekdays":
        nxt = current_dt + timedelta(days=1)
        while nxt.weekday() >= 5:
            nxt += timedelta(days=1)
        return nxt
    return None


def describe_memory_profile(memory):
    profile = memory.get("profile", {}) or {}
    facts = memory.get("facts", []) or []
    parts = []
    if profile.get("name"):
        parts.append(f"Имя: {profile['name']}")
    if profile.get("nickname"):
        parts.append(f"Ник: {profile['nickname']}")
    if profile.get("city"):
        parts.append(f"Город: {profile['city']}")
    if profile.get("about"):
        parts.append(f"О себе: {profile['about']}")
    if facts:
        parts.append("Факты: " + "; ".join(f.get("text","") for f in facts[-5:] if f.get("text")))
    return "\n".join(parts) if parts else "Пока ничего личного не запомнил."


def append_history(line: str):
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_vosk_model() -> Path | None:
    candidates = [APP_DIR / "model", APP_DIR / "vosk-model-small-ru-0.22", APP_DIR / "vosk-model-ru"]
    for base in candidates:
        if base.exists() and (base / "am").exists() and (base / "conf").exists():
            return base
        if base.exists():
            for child in base.iterdir():
                if child.is_dir() and (child / "am").exists() and (child / "conf").exists():
                    return child
    return None




def diagnose_voice_environment() -> dict:
    """Быстрая диагностика модели Vosk и микрофона при запуске."""
    report = {
        "checked_at": now_iso(),
        "app_dir": str(APP_DIR),
        "vosk_package": "unknown",
        "sounddevice_package": "unknown",
        "model_status": "missing",
        "model_path": "",
        "microphone_status": "unknown",
        "microphone_device_count": 0,
        "microphone_default": "",
        "issues": [],
        "warnings": [],
    }

    try:
        import importlib.util
        report["vosk_package"] = "ok" if importlib.util.find_spec("vosk") else "missing"
    except Exception as exc:
        report["vosk_package"] = f"error: {exc}"
    try:
        import importlib.util
        report["sounddevice_package"] = "ok" if importlib.util.find_spec("sounddevice") else "missing"
    except Exception as exc:
        report["sounddevice_package"] = f"error: {exc}"

    model_dir = find_vosk_model()
    if model_dir:
        report["model_status"] = "ok"
        report["model_path"] = str(model_dir)
    else:
        report["model_status"] = "missing"
        report["issues"].append(
            "Модель Vosk не найдена. Положите распакованную модель в папку model рядом с JARVIS.exe "
            "или в корень проекта перед сборкой EXE."
        )

    if report["vosk_package"] != "ok":
        report["issues"].append("Python-пакет vosk не найден. Запусти install_requirements.bat или build_exe.bat.")
    if report["sounddevice_package"] != "ok":
        report["issues"].append("Python-пакет sounddevice не найден. Запусти install_requirements.bat или build_exe.bat.")

    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = []
        for idx, dev in enumerate(devices):
            try:
                if int(dev.get("max_input_channels", 0)) > 0:
                    input_devices.append((idx, dev.get("name", "unknown")))
            except Exception:
                pass
        report["microphone_device_count"] = len(input_devices)
        try:
            default_input = sd.default.device[0]
            if default_input is not None and int(default_input) >= 0:
                report["microphone_default"] = str(devices[int(default_input)].get("name", default_input))
        except Exception:
            report["microphone_default"] = ""
        if input_devices:
            report["microphone_status"] = "ok"
            if not report["microphone_default"]:
                report["warnings"].append("Микрофон найден, но устройство записи по умолчанию не выбрано.")
        else:
            report["microphone_status"] = "missing"
            report["issues"].append("Микрофон не найден. Проверь устройство записи в Windows.")
    except Exception as exc:
        report["microphone_status"] = f"error: {exc}"
        report["issues"].append(f"Не удалось проверить микрофон через sounddevice: {exc}")

    return report


def format_voice_diagnostics(report: dict) -> str:
    lines = [
        f"Диагностика голоса • {report.get('checked_at', '')}",
        f"APP_DIR: {report.get('app_dir', '')}",
        f"Пакет vosk: {report.get('vosk_package', 'unknown')}",
        f"Пакет sounddevice: {report.get('sounddevice_package', 'unknown')}",
        f"Модель Vosk: {report.get('model_status', 'unknown')} {report.get('model_path', '')}".strip(),
        f"Микрофон: {report.get('microphone_status', 'unknown')} • устройств={report.get('microphone_device_count', 0)} • по умолчанию={report.get('microphone_default', '')}",
        "",
        "Проблемы:",
    ]
    lines.extend([f"- {x}" for x in report.get("issues", [])] or ["- нет"])
    lines.append("")
    lines.append("Предупреждения:")
    lines.extend([f"- {x}" for x in report.get("warnings", [])] or ["- нет"])
    return "\n".join(lines)


class TTSWorker(threading.Thread):
    def __init__(self, enabled_getter, log_callback=None, mode_getter=None):
        super().__init__(daemon=True)
        self.queue = queue.Queue()
        self.enabled_getter = enabled_getter
        self.log_callback = log_callback
        self.mode_getter = mode_getter or (lambda: "auto")
        self.engine = None
        self.edge_available = False
        self.voice_name = "ru-RU-SvetlanaNeural"
        self.audio_backend = "edge_wmp"
        self.stop_signal = threading.Event()
        self.current_lock = threading.Lock()
        self.current_player = None
        self.current_process = None
        self.current_alias = None
        self._edge_counter = 0
        self._init_engine()

    def _emit(self, message: str):
        if self.log_callback:
            try:
                self.log_callback(message)
            except Exception:
                pass

    def _init_engine(self):
        self.edge_available = False
        try:
            import edge_tts  # noqa: F401
            self.edge_available = True
            self._emit("edge-tts доступен")
        except Exception as e:
            self.edge_available = False
            self._emit(f"edge-tts недоступен: {e}")

        self.current_player = None
        self.current_process = None
        self.current_alias = None

        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            rate = self.engine.getProperty("rate")
            self.engine.setProperty("rate", max(165, int(rate * 0.95)))
            self.audio_backend = "pyttsx3"
            self._emit("pyttsx3 инициализирован")
        except Exception as e:
            self.engine = None
            if os.name == "nt":
                self.audio_backend = "windows_sapi"
            else:
                self.audio_backend = "offline"
            self._emit(f"pyttsx3 недоступен: {e}")

    def say(self, text: str):
        self._emit(f"в очередь TTS: {text}")
        self.queue.put(text)

    def stop(self):
        self._emit("получен стоп речи")
        self.stop_signal.set()
        with self.current_lock:
            try:
                if self.current_process is not None and self.current_process.poll() is None:
                    self.current_process.terminate()
            except Exception:
                pass
            try:
                alias = self.current_alias
                if alias and os.name == "nt":
                    import ctypes
                    ctypes.windll.winmm.mciSendStringW(f"stop {alias}", None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)
                    self._emit(f"winmm stop/close: {alias}")
            except Exception as e:
                self._emit(f"winmm stop ошибка: {e}")
            try:
                if self.engine is not None:
                    self.engine.stop()
            except Exception:
                pass
            self.current_process = None
            self.current_alias = None
        try:
            while not self.queue.empty():
                self.queue.get_nowait()
        except Exception:
            pass
        time.sleep(0.05)
        self.stop_signal.clear()

    def _say_windows_sapi(self, text: str):
        if os.name != "nt":
            self._emit("windows sapi недоступен вне Windows, fallback offline")
            return self._say_offline(text)
        self._emit("озвучка через Windows SAPI")
        safe_text = text.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$speak.Rate = 0; "
            f"$speak.Speak('{safe_text}')"
        )
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        with self.current_lock:
            self.current_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        while self.current_process and self.current_process.poll() is None:
            if self.stop_signal.is_set():
                try:
                    self.current_process.terminate()
                except Exception:
                    pass
                break
            time.sleep(0.05)

    async def _save_edge_audio_async(self, text: str, out_path: Path):
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=self.voice_name)
        await communicate.save(str(out_path))

    def _play_mp3_windows(self, mp3_path: Path):
        self._emit(f"проигрывание mp3: {mp3_path.name}")
        alias = f"jarvis_tts_{int(time.time() * 1000)}_{self._edge_counter}"

        try:
            import ctypes
            safe_path = str(mp3_path.resolve()).replace('"', '')
            with self.current_lock:
                self.current_alias = alias
            self._emit("backend winmm mci")
            open_cmd = f'open "{safe_path}" type mpegvideo alias {alias}'
            play_cmd = f'play {alias} wait'
            err = ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, None)
            if err != 0:
                raise RuntimeError(f"mci open error={err}")
            err = ctypes.windll.winmm.mciSendStringW(play_cmd, None, 0, None)
            if err != 0:
                raise RuntimeError(f"mci play error={err}")
            self._emit("winmm завершил проигрывание")
            return True
        except Exception as e:
            self._emit(f"winmm mci не сработал: {e}")
        finally:
            try:
                import ctypes
                ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)
            except Exception:
                pass
            with self.current_lock:
                if self.current_alias == alias:
                    self.current_alias = None

        try:
            from playsound import playsound
            self._emit("backend playsound")
            playsound(str(mp3_path))
            self._emit("playsound завершил проигрывание")
            return True
        except Exception as e:
            self._emit(f"playsound не сработал: {e}")

        safe_path = str(mp3_path.resolve()).replace("'", "''")
        script = f"""
$path = '{safe_path}'
$player = New-Object -ComObject WMPlayer.OCX
$player.settings.autoStart = $false
$player.settings.volume = 100
$player.URL = $path
$player.controls.play()
$started = $false
$deadline = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $deadline) {{
    $state = $player.playState
    if ($state -eq 3) {{ $started = $true }}
    if ($started -and ($state -eq 1 -or $state -eq 8 -or $state -eq 10)) {{ break }}
    Start-Sleep -Milliseconds 120
}}
$player.controls.stop()
""".strip()
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self._emit("backend Windows Media Player COM")
        with self.current_lock:
            self.current_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        while self.current_process and self.current_process.poll() is None:
            if self.stop_signal.is_set():
                try:
                    self.current_process.terminate()
                except Exception:
                    pass
                break
            time.sleep(0.05)
        return True

    def _say_edge(self, text: str):
        if not self.edge_available:
            self._emit("edge-tts недоступен, fallback")
            if os.name == "nt":
                return self._say_windows_sapi(text)
            return self._say_offline(text)
        self._edge_counter += 1
        out_path = DATA_DIR / f"edge_tts_{self._edge_counter}.mp3"
        try:
            self._emit(f"генерация Edge mp3: {out_path.name}")
            asyncio.run(self._save_edge_audio_async(text, out_path))
            if os.name == "nt" and out_path.exists():
                self._emit("mp3 создан успешно")
                self._play_mp3_windows(out_path)
            elif out_path.exists():
                self._emit("mp3 создан, но Windows backend недоступен -> offline")
                self._say_offline(text)
            else:
                raise RuntimeError("edge tts file not created")
        finally:
            try:
                if out_path.exists():
                    out_path.unlink()
                    self._emit("временный mp3 удалён")
            except Exception as e:
                self._emit(f"не удалился временный mp3: {e}")

    def _say_offline(self, text: str):
        if self.engine is None:
            self._emit("offline-движок отсутствует")
            return
        self._emit("озвучка через pyttsx3")
        self.engine.say(text)
        self.engine.runAndWait()

    def _say_auto(self, text: str):
        if self.edge_available:
            try:
                return self._say_edge(text)
            except Exception as e:
                self._emit(f"edge не сработал: {e}")
        if os.name == "nt":
            return self._say_windows_sapi(text)
        return self._say_offline(text)

    def run(self):
        while True:
            text = self.queue.get()
            if not text or not self.enabled_getter():
                continue
            self.stop_signal.clear()
            mode = str(self.mode_getter() or "auto")
            self._emit(f"старт озвучки | режим={mode} | текст={text}")
            try:
                if mode == "edge":
                    self._say_edge(text)
                elif mode == "system":
                    if os.name == "nt":
                        self._say_windows_sapi(text)
                    else:
                        self._say_offline(text)
                else:
                    self._say_auto(text)
                self._emit("озвучка завершена")
            except Exception as e:
                self._emit(f"ошибка озвучки: {e}")
                try:
                    self._init_engine()
                    if os.name == "nt":
                        self._emit("авто-fallback на Windows SAPI")
                        self._say_windows_sapi(text)
                    else:
                        self._emit("авто-fallback на pyttsx3")
                        self._say_offline(text)
                except Exception as e2:
                    self._emit(f"fallback тоже не сработал: {e2}")



class WhisperPhraseCollector:
    def __init__(self, app, sample_rate: int = 16000):
        self.app = app
        self.sample_rate = sample_rate
        self.silence_ms = int(app.cfg.get("whisper_silence_ms", 900) or 900)
        self.max_phrase_sec = float(app.cfg.get("whisper_max_phrase_sec", 8.0) or 8.0)
        self.reset()

    def reset(self):
        self.frames = []
        self.started = False
        self.started_at = None
        self.last_voice_at = None

    def push(self, data: bytes):
        import audioop
        now = time.time()
        rms = 0
        try:
            rms = audioop.rms(data, 2)
        except Exception:
            rms = 0
        threshold = 220
        voiced = rms >= threshold
        if voiced and not self.started:
            self.started = True
            self.started_at = now
        if self.started:
            self.frames.append(data)
            if voiced:
                self.last_voice_at = now
        if not self.started:
            return None
        phrase_age = now - (self.started_at or now)
        silence_age = now - (self.last_voice_at or now) if self.last_voice_at else 0
        if phrase_age >= self.max_phrase_sec or (self.last_voice_at and silence_age * 1000 >= self.silence_ms):
            payload = b"".join(self.frames)
            self.reset()
            return payload if payload else None
        return None


def write_pcm16_wav(path: Path, raw_audio: bytes, sample_rate: int = 16000):
    import wave
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw_audio)


def transcribe_with_whisper_cpp(raw_audio: bytes, cli_path: Path, model_path: Path, sample_rate: int = 16000, language: str = "ru", threads: int = 4, processors: int = 1) -> str:
    import tempfile
    if not raw_audio or not cli_path.exists() or not model_path.exists():
        return ""
    language = (language or "ru").strip() or "ru"
    threads = max(1, int(threads or 1))
    processors = max(1, int(processors or 1))
    with tempfile.TemporaryDirectory(prefix="jarvis_whcpp_") as td:
        td_path = Path(td)
        wav_path = td_path / "phrase.wav"
        write_pcm16_wav(wav_path, raw_audio, sample_rate=sample_rate)
        cmd = [str(cli_path), "-m", str(model_path), "-f", str(wav_path), "-l", language, "-otxt", "-of", str(td_path / "out"), "-np", "-nt", str(threads), "-p", str(processors)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except Exception:
            return ""
        txt_path = td_path / "out.txt"
        text = ""
        if txt_path.exists():
            try:
                text = txt_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
        if not text:
            stdout = (result.stdout or "") + "\n" + (result.stderr or "")
            lines = []
            for line in stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("[") or line.startswith("system_info") or line.startswith("main:"):
                    continue
                lines.append(line)
            text = " ".join(lines).strip()
        text = re.sub(r"\[[^\]]+\]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return normalize_text(text)


def find_whisper_cpp_cli() -> Path | None:
    names = ["whisper-cli.exe", "whisper-cli", "main.exe", "main"]
    candidates = [
        APP_DIR / "whisper_cpp",
        APP_DIR / "whisper_cpp" / "bin",
        APP_DIR / "whispercpp",
        APP_DIR / "tools" / "whisper_cpp",
        APP_DIR,
    ]
    for base in candidates:
        for name in names:
            path = base / name
            if path.exists():
                return path
    return None


def find_whisper_cpp_model() -> Path | None:
    candidates = [
        APP_DIR / "whisper_cpp" / "models",
        APP_DIR / "models",
        APP_DIR / "whisper_models",
        APP_DIR,
    ]
    pats = ["ggml-*.bin", "*.gguf"]
    for base in candidates:
        if not base.exists():
            continue
        for pat in pats:
            items = sorted(base.glob(pat))
            if items:
                return items[0]
    return None


def transcribe_with_faster_whisper(raw_audio: bytes, model, sample_rate: int = 16000) -> str:
    try:
        import numpy as np
    except Exception:
        return ""
    if not raw_audio:
        return ""
    pcm = np.frombuffer(raw_audio, dtype=np.int16).astype("float32") / 32768.0
    if pcm.size == 0:
        return ""
    try:
        segments, _info = model.transcribe(pcm, language="ru", vad_filter=True, beam_size=1, best_of=1, condition_on_previous_text=False)
        text = " ".join((seg.text or "").strip() for seg in segments).strip()
        return normalize_text(text)
    except Exception:
        return ""


class VoiceWorker(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def _resolve_engine_order(self):
        selected = normalize_text(self.app.cfg.get("voice_input_engine", "auto")) or "auto"
        if selected == "auto":
            # Release default: use local Vosk first.
            # Whisper backends stay available when selected manually in Settings.
            return ["vosk", "whisper_cpp", "whisper"]
        if selected == "speechkit":
            return ["speechkit", "whisper_cpp", "whisper", "vosk"]
        if selected == "whisper_cpp":
            return ["whisper_cpp", "whisper", "vosk"]
        if selected == "whisper":
            return ["whisper", "whisper_cpp", "vosk"]
        return ["vosk"]

    def _run_speechkit(self):
        try:
            import requests
            import sounddevice as sd
        except Exception as e:
            self.app.post_log(f"[voice] SpeechKit backend недоступен: {e}")
            return False
        api_key = str(self.app.cfg.get("speechkit_api_key", "") or "").strip()
        folder_id = str(self.app.cfg.get("speechkit_folder_id", "") or "").strip()
        if not api_key or not folder_id:
            self.app.post_log("[voice] SpeechKit не настроен: добавь API key и Folder ID в настройках.")
            return False
        lang = str(self.app.cfg.get("speechkit_lang", "ru-RU") or "ru-RU")
        topic = str(self.app.cfg.get("speechkit_topic", "general") or "general")
        sample_rate = 16000
        q = queue.Queue()
        collector = WhisperPhraseCollector(self.app, sample_rate=sample_rate)
        collector.silence_ms = int(self.app.cfg.get("speechkit_silence_ms", self.app.cfg.get("whisper_silence_ms", 900)) or 900)
        collector.max_phrase_sec = float(self.app.cfg.get("speechkit_max_phrase_sec", self.app.cfg.get("whisper_max_phrase_sec", 8.0)) or 8.0)
        self.app.set_status("слушаю")
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        transcripts = 0

        def callback(indata, frames, time_info, status):
            _ = frames, time_info
            if status:
                self.app.post_log(f"[voice] SpeechKit mic status: {status}")
            q.put(bytes(indata))

        def recognize_phrase(raw_audio: bytes) -> str:
            params = {
                "lang": lang,
                "topic": topic,
                "folderId": folder_id,
                "format": "lpcm",
                "sampleRateHertz": str(sample_rate),
            }
            headers = {
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/octet-stream",
            }
            try:
                response = requests.post(url, params=params, headers=headers, data=raw_audio, timeout=25)
                if response.status_code != 200:
                    self.app.post_log(f"[voice] SpeechKit HTTP {response.status_code}: {response.text[:200]}")
                    return ""
                payload = response.json()
                return normalize_text(payload.get("result", ""))
            except Exception as e:
                self.app.post_log(f"[voice] SpeechKit request error: {e}")
                return ""

        try:
            with sd.RawInputStream(samplerate=sample_rate, blocksize=4096, dtype="int16", channels=1, callback=callback):
                self.app.post_log("[voice] SpeechKit voice mode запущен.")
                while not self.stop_event.is_set():
                    try:
                        data = q.get(timeout=0.25)
                    except queue.Empty:
                        continue
                    self.app.bump_visualizer()
                    phrase = collector.push(data)
                    if not phrase:
                        continue
                    self.app.post_log(f"[voice] SpeechKit phrase bytes={len(phrase)}")
                    resolved = recognize_phrase(phrase)
                    if not resolved:
                        self.app.post_log("[voice] SpeechKit transcript пустой")
                        continue
                    transcripts += 1
                    self.app.post_log(f"[speechkit] {resolved}")
                    if getattr(self.app, "should_ignore_voice_result", lambda _text: False)(resolved):
                        continue
                    self.app.on_voice_text(resolved)
            return True
        except Exception as e:
            self.app.post_log(f"[voice] Ошибка микрофона SpeechKit: {e}")
            self.app.set_status("ошибка микрофона")
            return False

    def _run_whisper_cpp(self):
        try:
            import sounddevice as sd
        except Exception as e:
            self.app.post_log(f"[voice] whisper.cpp backend недоступен: {e}")
            return False
        cli_cfg = str(self.app.cfg.get("whisper_cpp_cli_path", "") or "").strip()
        model_cfg = str(self.app.cfg.get("whisper_cpp_model_path", "") or "").strip()
        cli_path = Path(cli_cfg) if cli_cfg else find_whisper_cpp_cli()
        model_path = Path(model_cfg) if model_cfg else find_whisper_cpp_model()
        if not cli_path or not Path(cli_path).exists():
            self.app.post_log("[voice] Не найден whisper.cpp CLI. Укажи путь к whisper-cli.exe в настройках.")
            return False
        if not model_path or not Path(model_path).exists():
            self.app.post_log("[voice] Не найдена модель whisper.cpp. Укажи путь к ggml-*.bin или *.gguf в настройках.")
            return False
        language = str(self.app.cfg.get("whisper_cpp_language", "ru") or "ru")
        threads = int(self.app.cfg.get("whisper_cpp_threads", 4) or 4)
        processors = int(self.app.cfg.get("whisper_cpp_processors", 1) or 1)
        sample_rate = 16000
        q = queue.Queue()
        collector = WhisperPhraseCollector(self.app, sample_rate=sample_rate)
        collector.silence_ms = int(self.app.cfg.get("whisper_cpp_silence_ms", self.app.cfg.get("whisper_silence_ms", 900)) or 900)
        collector.max_phrase_sec = float(self.app.cfg.get("whisper_cpp_max_phrase_sec", self.app.cfg.get("whisper_max_phrase_sec", 8.0)) or 8.0)
        transcripts = 0
        empty_phrases = 0
        start_ts = time.time()
        self.app.post_log(f"[voice] whisper.cpp загружен: cli={Path(cli_path).name} model={Path(model_path).name} lang={language} threads={threads}")
        self.app.set_status("слушаю")

        def callback(indata, frames, time_info, status):
            _ = frames, time_info
            if status:
                self.app.post_log(f"[voice] whisper.cpp mic status: {status}")
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=sample_rate, blocksize=4096, dtype="int16", channels=1, callback=callback):
                self.app.post_log("[voice] whisper.cpp voice mode запущен.")
                while not self.stop_event.is_set():
                    try:
                        data = q.get(timeout=0.25)
                    except queue.Empty:
                        continue
                    self.app.bump_visualizer()
                    phrase = collector.push(data)
                    if not phrase:
                        continue
                    self.app.post_log(f"[voice] whisper.cpp phrase bytes={len(phrase)}")
                    resolved = transcribe_with_whisper_cpp(phrase, Path(cli_path), Path(model_path), sample_rate=sample_rate, language=language, threads=threads, processors=processors)
                    if not resolved:
                        empty_phrases += 1
                        self.app.post_log(f"[voice] whisper.cpp transcript пустой ({empty_phrases})")
                        if transcripts == 0 and empty_phrases >= 2:
                            self.app.post_log("[voice] whisper.cpp не дал текста, fallback дальше.")
                            return False
                        continue
                    transcripts += 1
                    self.app.post_log(f"[whisper.cpp] {resolved}")
                    if getattr(self.app, "should_ignore_voice_result", lambda _text: False)(resolved):
                        continue
                    self.app.on_voice_text(resolved)
            return True
        except Exception as e:
            self.app.post_log(f"[voice] Ошибка микрофона whisper.cpp: {e}")
            self.app.set_status("ошибка микрофона")
            return False

    def _run_whisper(self):
        try:
            from faster_whisper import WhisperModel
            import sounddevice as sd
        except Exception as e:
            self.app.post_log(f"[voice] Whisper backend недоступен: {e}")
            return False
        model_name = str(self.app.cfg.get("whisper_model_size", "tiny") or "tiny")
        compute_type = str(self.app.cfg.get("whisper_compute_type", "int8") or "int8")
        device = str(self.app.cfg.get("whisper_device", "auto") or "auto")
        if device == "auto":
            device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        model_root = APP_DIR / "whisper_models"
        model_root.mkdir(parents=True, exist_ok=True)
        try:
            model = WhisperModel(model_name, device=device, compute_type=compute_type, download_root=str(model_root))
        except Exception as e:
            self.app.post_log(f"[voice] Ошибка загрузки Whisper: {e}")
            return False
        self.app.post_log(f"[voice] Whisper загружен: model={model_name} device={device} compute={compute_type}")
        self.app.set_status("слушаю")
        sample_rate = 16000
        q = queue.Queue()
        collector = WhisperPhraseCollector(self.app, sample_rate=sample_rate)
        transcripts = 0
        empty_phrases = 0
        start_ts = time.time()

        def callback(indata, frames, time_info, status):
            _ = frames, time_info
            if status:
                self.app.post_log(f"[voice] Whisper mic status: {status}")
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=sample_rate, blocksize=4096, dtype="int16", channels=1, callback=callback):
                self.app.post_log("[voice] Whisper voice mode запущен.")
                while not self.stop_event.is_set():
                    try:
                        data = q.get(timeout=0.25)
                    except queue.Empty:
                        continue
                    self.app.bump_visualizer()
                    phrase = collector.push(data)
                    if not phrase:
                        continue
                    self.app.post_log(f"[voice] Whisper phrase bytes={len(phrase)}")
                    resolved = transcribe_with_faster_whisper(phrase, model, sample_rate=sample_rate)
                    if not resolved:
                        empty_phrases += 1
                        self.app.post_log(f"[voice] Whisper transcript пустой ({empty_phrases})")
                        if transcripts == 0 and empty_phrases >= 2:
                            self.app.post_log("[voice] Whisper не дал текста, fallback на Vosk.")
                            return False
                        continue
                    transcripts += 1
                    self.app.post_log(f"[whisper] {resolved}")
                    if getattr(self.app, "should_ignore_voice_result", lambda _text: False)(resolved):
                        continue
                    self.app.on_voice_text(resolved)
            return True
        except Exception as e:
            self.app.post_log(f"[voice] Ошибка микрофона Whisper: {e}")
            self.app.set_status("ошибка микрофона")
            return False

    def _run_vosk(self):
        try:
            from vosk import KaldiRecognizer, Model
            import sounddevice as sd
        except Exception as exc:
            diag = diagnose_voice_environment()
            self.app.post_log(f"[voice] Оффлайн-распознавание недоступно: {exc}")
            self.app.post_log("[voice] " + format_voice_diagnostics(diag).replace("\n", " | "))
            self.app.set_status("ошибка голоса")
            self.app.post_response("Оффлайн-голос не готов: нет vosk/sounddevice. Запусти install_requirements.bat или пересобери EXE через build_exe.bat.")
            return True

        model_dir = find_vosk_model()
        if not model_dir:
            diag = diagnose_voice_environment()
            self.app.post_log("[voice] Модель Vosk не найдена. Нужна папка model рядом с JARVIS.exe.")
            self.app.post_log("[voice] " + format_voice_diagnostics(diag).replace("\n", " | "))
            self.app.set_status("нет модели")
            self.app.post_response("Не вижу модель Vosk. Положите распакованную модель в папку model рядом с JARVIS.exe и перезапустите голосовой режим.")
            try:
                messagebox.showwarning("JARVIS — модель Vosk не найдена", "Не найдена папка model с моделью Vosk.\n\nЧто сделать:\n1) Скачайте и распакуйте русскую модель Vosk.\n2) Положите содержимое в папку model рядом с JARVIS.exe.\n3) Перезапустите JARVIS или голосовой режим.")
            except Exception:
                pass
            return True

        try:
            model = Model(str(model_dir))
        except Exception as e:
            self.app.post_log(f"[voice] Ошибка загрузки модели: {e}")
            self.app.set_status("ошибка модели")
            self.app.post_response("Модель есть, но не загрузилась. Проверь содержимое папки model.")
            return True

        self.app.post_log(f"[voice] Модель Vosk загружена: {model_dir.name}")
        self.app.set_status("слушаю")

        sample_rate = 16000
        grammar = self.app.build_vosk_grammar()
        free_recognizer = KaldiRecognizer(model, sample_rate)
        try:
            recognizer = KaldiRecognizer(model, sample_rate, grammar)
            self.app.post_log("[voice] Командная грамматика Vosk загружена.")
            self.app.post_log("[voice] Hybrid core: command + free text recognizers активны.")
        except Exception as e:
            recognizer = KaldiRecognizer(model, sample_rate)
            self.app.post_log(f"[voice] Грамматика не загрузилась, fallback на обычный режим: {e}")
            free_recognizer = None
        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            _ = frames, time_info
            if status:
                pass
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype="int16", channels=1, callback=callback):
                self.app.post_log("[voice] Голосовой режим Vosk запущен.")
                while not self.stop_event.is_set():
                    try:
                        data = q.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    self.app.bump_visualizer()
                    cmd_ready = recognizer.AcceptWaveform(data)
                    free_ready = free_recognizer.AcceptWaveform(data) if free_recognizer is not None else False
                    if not (cmd_ready or free_ready):
                        continue
                    command_text = ""
                    free_text = ""
                    if cmd_ready:
                        try:
                            result = json.loads(recognizer.Result())
                            command_text = normalize_text(result.get("text", ""))
                        except Exception:
                            command_text = ""
                    if free_ready:
                        try:
                            free_result = json.loads(free_recognizer.Result())
                            free_text = normalize_text(free_result.get("text", ""))
                        except Exception:
                            free_text = ""
                    resolved = self.app.resolve_hybrid_voice_text(command_text, free_text)
                    if resolved:
                        if getattr(self.app, "tts_busy", False):
                            interrupt = normalize_text(resolved)
                            if not self.app.match_any(interrupt, getattr(self.app, "interrupt_phrases", [])):
                                continue
                        self.app.on_voice_text(resolved)
            return True
        except Exception as e:
            diag = diagnose_voice_environment()
            self.app.post_log(f"[voice] Ошибка микрофона: {e}")
            self.app.post_log("[voice] " + format_voice_diagnostics(diag).replace("\n", " | "))
            self.app.set_status("ошибка микрофона")
            self.app.post_response("Не удалось открыть микрофон. Проверь устройство записи в Windows и доступ к микрофону.")
            try:
                messagebox.showwarning("JARVIS — микрофон не открыт", f"Не удалось открыть микрофон:\n{e}\n\nПроверь устройство записи Windows и доступ к микрофону.")
            except Exception:
                pass
            return True

    def run(self):
        for engine in self._resolve_engine_order():
            if self.stop_event.is_set():
                return
            if engine == "speechkit":
                self.app.post_log("[voice] STT engine → SpeechKit")
                if self._run_speechkit():
                    return
                self.app.post_log("[voice] SpeechKit не поднялся, fallback дальше.")
                continue
            if engine == "whisper_cpp":
                self.app.post_log("[voice] STT engine → whisper.cpp")
                if self._run_whisper_cpp():
                    return
                self.app.post_log("[voice] whisper.cpp не поднялся, fallback дальше.")
                continue
            if engine == "whisper":
                self.app.post_log("[voice] STT engine → Whisper")
                if self._run_whisper():
                    return
                self.app.post_log("[voice] Whisper не поднялся, fallback дальше.")
                continue
            if engine == "vosk":
                self.app.post_log("[voice] STT engine → Vosk")
                if self._run_vosk():
                    return
        self.app.set_status("ошибка голоса")
        self.app.post_response("Не удалось поднять whisper.cpp, Whisper или Vosk. Проверь зависимости STT.")


