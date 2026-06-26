import unittest

from jarvis.core.config_migration import (
    STARTUP_PROMPTS_MIGRATION_KEY,
    STARTUP_PROMPTS_MIGRATION_VERSION,
    migrate_startup_prompt_settings,
)


class StartupPromptMigrationTests(unittest.TestCase):
    def test_old_config_is_cleaned_once(self):
        old_config = {
            "show_first_run_wizard": True,
            "first_run_completed": False,
            "show_model_setup_wizard": True,
            "local_model_setup_completed": False,
            "startup_recovery_prompt": True,
        }

        migrated, changed = migrate_startup_prompt_settings(old_config)

        self.assertTrue(changed)
        self.assertFalse(migrated["show_first_run_wizard"])
        self.assertTrue(migrated["first_run_completed"])
        self.assertFalse(migrated["show_model_setup_wizard"])
        self.assertTrue(migrated["local_model_setup_completed"])
        self.assertFalse(migrated["startup_recovery_prompt"])
        self.assertEqual(
            migrated[STARTUP_PROMPTS_MIGRATION_KEY],
            STARTUP_PROMPTS_MIGRATION_VERSION,
        )

    def test_later_user_choice_is_preserved(self):
        config = {
            STARTUP_PROMPTS_MIGRATION_KEY: STARTUP_PROMPTS_MIGRATION_VERSION,
            "startup_recovery_prompt": True,
        }

        migrated, changed = migrate_startup_prompt_settings(config)

        self.assertFalse(changed)
        self.assertTrue(migrated["startup_recovery_prompt"])

    def test_input_dictionary_is_not_modified(self):
        original = {"show_first_run_wizard": True}

        migrated, changed = migrate_startup_prompt_settings(original)

        self.assertTrue(changed)
        self.assertEqual(original, {"show_first_run_wizard": True})
        self.assertIsNot(migrated, original)

    def test_invalid_migration_marker_is_repaired(self):
        config = {STARTUP_PROMPTS_MIGRATION_KEY: "broken"}

        migrated, changed = migrate_startup_prompt_settings(config)

        self.assertTrue(changed)
        self.assertEqual(
            migrated[STARTUP_PROMPTS_MIGRATION_KEY],
            STARTUP_PROMPTS_MIGRATION_VERSION,
        )


if __name__ == "__main__":
    unittest.main()
