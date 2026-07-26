import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "portable" / "launcher.ps1"


class LauncherStabilityTests(unittest.TestCase):
    def test_launcher_forces_close_reopen_periodic_restart_off(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("Disable-CloseReopenPeriodicRestart", text)
        self.assertIn("enable_periodic_restart = False", text)
        self.assertIn("Disable-CloseReopenPeriodicRestart $LegacyProfile", text)
        self.assertIn("Disable-CloseReopenPeriodicRestart $LegacyPortable", text)

    def test_launcher_restarts_only_unexpected_nonzero_exits(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("$UnexpectedRestartLimit = 3", text)
        self.assertIn("if ($process.ExitCode -eq 0) { break }", text)
        self.assertIn("unexpected_exit", text)
        self.assertIn("Start-Sleep -Seconds 10", text)


if __name__ == "__main__":
    unittest.main()
