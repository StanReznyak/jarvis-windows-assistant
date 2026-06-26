from __future__ import annotations

from pathlib import Path
import re

ROOT_DIR = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT_DIR / "VERSION.txt"

DEFAULT_VERSION_LINE = "JARVIS v8.4"
DEFAULT_APP_VERSION = "v8.4"
DEFAULT_CODENAME = ""
DEFAULT_SUBTITLE = "Голосовой помощник для Windows"
PUBLISHER = "StanReznyak"
PRODUCT_DESCRIPTION = "Голосовой помощник для Windows"


def read_version_line() -> str:
    try:
        raw = VERSION_FILE.read_text(encoding="utf-8").strip()
        return raw or DEFAULT_VERSION_LINE
    except Exception:
        return DEFAULT_VERSION_LINE


VERSION_RE = r"v\d+\.\d+(?:\.\d+)?(?:\.\d+)?"


def parse_version_token(version_line: str) -> str:
    match = re.search(VERSION_RE, version_line)
    return match.group(0) if match else DEFAULT_APP_VERSION


def parse_codename(version_line: str) -> str:
    version_token = parse_version_token(version_line)
    prefix = f"JARVIS {version_token}"
    tail = version_line.replace(prefix, "", 1).strip()
    tail = tail.lstrip(" -•—")
    return tail


VERSION_LINE = read_version_line()
APP_VERSION = parse_version_token(VERSION_LINE)
APP_CODENAME = parse_codename(VERSION_LINE)
APP_SUBTITLE = DEFAULT_SUBTITLE
APP_TITLE = f"JARVIS {APP_VERSION}" if not APP_CODENAME else f"JARVIS {APP_VERSION} {APP_CODENAME}"
