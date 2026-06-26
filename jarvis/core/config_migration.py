from __future__ import annotations

from typing import Any

STARTUP_PROMPTS_MIGRATION_KEY = "startup_prompts_migration"
STARTUP_PROMPTS_MIGRATION_VERSION = 1

_CLEAN_STARTUP_VALUES = {
    "first_run_completed": True,
    "show_first_run_wizard": False,
    "show_model_setup_wizard": False,
    "local_model_setup_completed": True,
    "startup_recovery_prompt": False,
}


def migrate_startup_prompt_settings(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Apply the one-time v8.4 clean-start migration to a saved config.

    Old builds could persist startup prompt flags as true. The migration disables
    those prompts once, records its version, and then leaves later user choices
    untouched.
    """
    result = dict(data)
    raw_version = result.get(STARTUP_PROMPTS_MIGRATION_KEY, 0)
    try:
        current_version = int(raw_version or 0)
    except (TypeError, ValueError):
        current_version = 0

    if current_version >= STARTUP_PROMPTS_MIGRATION_VERSION:
        return result, False

    result.update(_CLEAN_STARTUP_VALUES)
    result[STARTUP_PROMPTS_MIGRATION_KEY] = STARTUP_PROMPTS_MIGRATION_VERSION
    return result, True
