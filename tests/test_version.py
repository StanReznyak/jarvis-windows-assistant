import unittest

from jarvis.core.version import parse_codename, parse_version_token


class VersionTests(unittest.TestCase):
    def test_public_version(self):
        self.assertEqual(parse_version_token("JARVIS v8.4"), "v8.4")
        self.assertEqual(parse_codename("JARVIS v8.4"), "")

    def test_optional_codename(self):
        self.assertEqual(
            parse_codename("JARVIS v8.4 • Desktop Release"),
            "Desktop Release",
        )

    def test_missing_version_uses_public_default(self):
        self.assertEqual(parse_version_token("JARVIS"), "v8.4")


if __name__ == "__main__":
    unittest.main()
