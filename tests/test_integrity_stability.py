import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
LAUNCHER = ROOT / "portable" / "launcher.ps1"


class IntegrityStabilityTests(unittest.TestCase):
    def test_obfuscated_integrity_modules_are_scanned_on_import(self):
        text = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("low.startswith('_q')", text)
        self.assertIn("_looks_integrity_exit_module", text)
        self.assertIn("_is_target_module_name(mn) or _looks_integrity_exit_module(m)", text)

    def test_known_access_violation_primitive_is_neutralized(self):
        text = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("_qf_abc077a3d0ac", text)
        self.assertIn("_INTEGRITY_EXIT_NOOP_NAMES", text)

    def test_launcher_self_elevates_before_starting_watchdog(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("Test-IsAdministrator", text)
        self.assertIn("-Verb RunAs", text)
        self.assertIn("QQFARM_LAUNCHER_ELEVATED", text)
        self.assertIn("Start-Process -FilePath $Exe", text)


if __name__ == "__main__":
    unittest.main()
