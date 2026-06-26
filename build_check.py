from __future__ import annotations

import compileall
import json
import re
from pathlib import Path

from jarvis.core.config_migration import (
    STARTUP_PROMPTS_MIGRATION_KEY,
    STARTUP_PROMPTS_MIGRATION_VERSION,
    migrate_startup_prompt_settings,
)

ROOT = Path(__file__).resolve().parent
EXPECTED_VERSION = "JARVIS v8.4"
EXPECTED_RELEASE_TAG = "v8.4"

SKIP_DIRS = {".venv", "venv", "build", "dist", "dist_setup", "__pycache__"}
RUNTIME_DATA_FILES = {
    "config.json",
    "history.txt",
    "memory_profile.json",
    "notes.txt",
    "reminders.json",
    "system_events.log",
    "ui_session.json",
    "startup_crash.log",
    "data_health_report.json",
}
BAT_FILES = [
    "START_JARVIS.bat",
    "RUN_DEBUG.bat",
    "build_exe.bat",
    "build_installer.bat",
    "install_requirements.bat",
    "run.bat",
    "COPY_CONFIG_IF_NEEDED.bat",
    "SET_CLOUD_KEY_WINDOWS.bat",
    "REMOVE_CLOUD_KEY_WINDOWS.bat",
    "SETUP_LOCAL_MODEL_WINDOWS.bat",
    "CHECK_LOCAL_MODEL_WINDOWS.bat",
    "CLEAR_REMINDERS_WINDOWS.bat",
]
TEXT_EXTS = {".py", ".txt", ".json", ".bat", ".spec", ".iss", ".md", ".yml", ".yaml"}

REQUIRED_REPOSITORY_FILES = {
    "README.md",
    "ARCHITECTURE_RU.md",
    "CHANGELOG.txt",
    ".gitignore",
    ".github/workflows/python-check.yml",
    "tests/test_config_migration.py",
    "tests/test_version.py",
}


def fail(message: str) -> None:
    raise SystemExit(f"BUILD CHECK FAILED: {message}")


def iter_project_files():
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def check_version() -> None:
    version_text = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
    if version_text != EXPECTED_VERSION:
        fail(f"VERSION.txt mismatch: {version_text!r}")
    from jarvis.core.version import APP_VERSION, APP_CODENAME, APP_TITLE
    if APP_VERSION != EXPECTED_RELEASE_TAG:
        fail(f"APP_VERSION parsed wrong: {APP_VERSION!r}")
    if APP_CODENAME:
        fail(f"APP_CODENAME should be empty for public release: {APP_CODENAME!r}")
    if APP_TITLE != EXPECTED_VERSION:
        fail(f"APP_TITLE mismatch: {APP_TITLE!r}")


def check_config_json() -> None:
    cfg = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))
    checks = {
        "voice_input_engine": "vosk",
        "wake_word": "джарвис",
        "model_provider": "auto",
        "ollama_model": "llama3.2:1b",
    }
    for key, expected in checks.items():
        if cfg.get(key) != expected:
            fail(f"config.example.json {key} should be {expected!r}")
    if cfg.get("model_answers_enabled") is not True:
        fail("model_answers_enabled should default to true")
    if cfg.get("auto_start_voice") is not True:
        fail("auto_start_voice should default to true for normal desktop start")
    startup_checks = {
        "first_run_completed": True,
        "show_first_run_wizard": False,
        "show_model_setup_wizard": False,
        "local_model_setup_completed": True,
        "startup_recovery_prompt": False,
        "restore_last_session": False,
        STARTUP_PROMPTS_MIGRATION_KEY: STARTUP_PROMPTS_MIGRATION_VERSION,
    }
    for key, expected in startup_checks.items():
        if cfg.get(key) != expected:
            fail(f"config.example.json {key} should be {expected!r}")
    if cfg.get("cloud_api_key"):
        fail("config.example.json must not contain cloud key")


def check_startup_prompt_migration() -> None:
    old_cfg = {
        "show_first_run_wizard": True,
        "first_run_completed": False,
        "show_model_setup_wizard": True,
        "local_model_setup_completed": False,
        "startup_recovery_prompt": True,
    }
    migrated, changed = migrate_startup_prompt_settings(old_cfg)
    if not changed:
        fail("startup prompt migration did not run for an old config")
    expected = {
        "show_first_run_wizard": False,
        "first_run_completed": True,
        "show_model_setup_wizard": False,
        "local_model_setup_completed": True,
        "startup_recovery_prompt": False,
        STARTUP_PROMPTS_MIGRATION_KEY: STARTUP_PROMPTS_MIGRATION_VERSION,
    }
    for key, value in expected.items():
        if migrated.get(key) != value:
            fail(f"startup prompt migration produced wrong {key}: {migrated.get(key)!r}")

    migrated["startup_recovery_prompt"] = True
    second_pass, changed_again = migrate_startup_prompt_settings(migrated)
    if changed_again:
        fail("startup prompt migration must run only once")
    if second_pass.get("startup_recovery_prompt") is not True:
        fail("startup prompt migration must preserve later user choices")


def check_compile() -> None:
    ok = compileall.compile_dir(str(ROOT), quiet=1, maxlevels=20)
    if not ok:
        fail("Python compileall failed")


def check_bat_files() -> None:
    for name in BAT_FILES:
        path = ROOT / name
        if not path.exists():
            fail(f"missing {name}")
        raw = path.read_bytes()
        if any(b >= 128 for b in raw):
            fail(f"{name} is not ASCII-only")
        if b"\r\n" not in raw or raw.count(b"\n") != raw.count(b"\r\n"):
            fail(f"{name} must use CRLF line endings")


def cleanup_pycache() -> None:
    import shutil
    for path in ROOT.rglob("__pycache__"):
        if any(part in SKIP_DIRS - {"__pycache__"} for part in path.parts):
            continue
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob("*.pyc"):
        if any(part in SKIP_DIRS - {"__pycache__"} for part in path.parts):
            continue
        path.unlink(missing_ok=True)


def check_release_clean() -> None:
    cleanup_pycache()
    trash = []
    for path in iter_project_files():
        if path.name == "__pycache__" or path.suffix == ".pyc":
            trash.append(str(path.relative_to(ROOT)))
    if trash:
        fail("trash files found: " + ", ".join(trash[:10]))
    data_root = ROOT / "data"
    data_root_files = {p.name for p in data_root.glob("*") if p.is_file()}
    extra = data_root_files - {".gitkeep"}
    unknown_extra = extra - RUNTIME_DATA_FILES
    if unknown_extra:
        fail("unknown files in data root: " + ", ".join(sorted(unknown_extra)))
    if extra:
        print("BUILD CHECK NOTE: local runtime data found in data; it is not bundled into the EXE")


def check_no_control_chars() -> None:
    allowed = {9, 10, 13}
    for path in iter_project_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        raw = path.read_bytes()
        bad = [b for b in raw if b < 32 and b not in allowed]
        if bad:
            fail(f"control characters found in {path.relative_to(ROOT)}")


def check_no_stale_text() -> None:
    old_version_re = re.compile(r"(?:v)?8[._]4[._]6[._](\d+)")
    hits = []
    for path in iter_project_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if path.name == "build_check.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in old_version_re.finditer(text):
            hits.append(f"{path.relative_to(ROOT)} contains old version {match.group(0)}")
    if hits:
        fail("stale release text found: " + "; ".join(hits[:8]))


def check_file_version_info() -> None:
    text = (ROOT / "file_version_info.txt").read_text(encoding="utf-8")
    if "filevers=(8, 4, 0, 0)" not in text or "prodvers=(8, 4, 0, 0)" not in text:
        fail("file_version_info.txt numeric version must be 8.4")
    if "FileVersion', '8.4'" not in text or "ProductVersion', '8.4'" not in text:
        fail("file_version_info.txt string version must be 8.4")


def check_repository_hygiene() -> None:
    missing = [name for name in sorted(REQUIRED_REPOSITORY_FILES) if not (ROOT / name).is_file()]
    if missing:
        fail("missing repository files: " + ", ".join(missing))

    if (ROOT / "PROJECT_NOTES_RU.md").exists():
        fail("remove PROJECT_NOTES_RU.md from the public release")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if readme.count("```") % 2:
        fail("README.md has an unclosed code fence")
    if "ARCHITECTURE_RU.md" not in readme:
        fail("README.md must link to ARCHITECTURE_RU.md")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_ignore_rules = {
        "data/*",
        "!data/.gitkeep",
        "model/*",
        "!model/README",
        "models/*",
        "!models/README.txt",
        "*.env",
    }
    missing_rules = sorted(rule for rule in required_ignore_rules if rule not in gitignore)
    if missing_rules:
        fail(".gitignore is missing rules: " + ", ".join(missing_rules))

    workflow = (ROOT / ".github/workflows/python-check.yml").read_text(encoding="utf-8")
    if "python build_check.py" not in workflow or "unittest discover" not in workflow:
        fail("GitHub Actions workflow must run build_check and unit tests")

    forbidden_fragments = [
        "Shram" + "535",
        "exstas" + "535",
        "Chat" + "GPT",
        "generated " + "by AI",
        "AI-" + "generated",
        "сгенерировано " + "нейросетью",
    ]
    risky_hits = []
    for path in iter_project_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if path.name == "build_check.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for fragment in forbidden_fragments:
            if fragment.lower() in lowered:
                risky_hits.append(f"{path.relative_to(ROOT)}: {fragment}")
        if re.search(r"[A-Za-z]:\\Users\\[^\r\n]+", text, flags=re.IGNORECASE):
            risky_hits.append(f"{path.relative_to(ROOT)}: local Windows user path")
        if "/home/" in text or "/mnt/" in text:
            risky_hits.append(f"{path.relative_to(ROOT)}: local Unix path")
    if risky_hits:
        fail("portfolio hygiene markers found: " + "; ".join(risky_hits[:8]))


def check_secret_markers() -> None:
    risky = []
    for path in iter_project_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if path.name in ('config.example.json', '.gitignore', 'README.md', 'README_RU.txt', 'MODEL_SETUP_RU.txt', 'SET_CLOUD_KEY_WINDOWS.bat', 'REMOVE_CLOUD_KEY_WINDOWS.bat', 'build_check.py'):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        cloud_marker = "JARVIS_" + "CLOUD" + "_API_KEY="
        if cloud_marker in text or re.search(r"\bs" + "k-[A-Za-z0-9]", text):
            risky.append(str(path.relative_to(ROOT)))
    if risky:
        fail("possible secret markers found: " + ", ".join(risky[:8]))


if __name__ == "__main__":
    check_version()
    check_config_json()
    check_startup_prompt_migration()
    check_compile()
    check_bat_files()
    check_no_control_chars()
    check_no_stale_text()
    check_file_version_info()
    check_repository_hygiene()
    check_secret_markers()
    check_release_clean()
    print("BUILD CHECK OK")
