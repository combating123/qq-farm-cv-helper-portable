import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "portable" / "launcher.ps1"


class LauncherStartupClockBridgeRegression20260901Tests(unittest.TestCase):
    def test_launcher_integrates_future_date_bootstrap_bridge(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")

        self.assertIn("$StartupClockBridgePath = Join-Path $AppDir 'startup_clock_bridge.ps1'", text)
        self.assertIn(". $StartupClockBridgePath", text)
        self.assertIn("Test-StartupClockBridgeRequired", text)
        self.assertIn("Enter-StartupClockBridge", text)
        self.assertIn("Exit-StartupClockBridge", text)
        self.assertIn("Wait-AssistantBootstrapReady", text)

        # The bridge must be restored in a finally block after the child has
        # crossed the packaged bootstrap boundary.
        launch_index = text.index("$assistantProcess = Start-Process")
        restore_index = text.index("Exit-StartupClockBridge", launch_index)
        self.assertLess(launch_index, restore_index)


if __name__ == "__main__":
    unittest.main()
