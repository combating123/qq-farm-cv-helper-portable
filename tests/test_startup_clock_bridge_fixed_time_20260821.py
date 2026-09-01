import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "portable" / "startup_clock_bridge.ps1"


class StartupClockBridgeFixedTimeTests(unittest.TestCase):
    def test_startup_bridge_uses_fixed_safe_time_instead_of_current_time_of_day(self):
        source = BRIDGE.read_text(encoding="utf-8-sig")

        self.assertIn("-Hour 12 -Minute 0", source)
        self.assertNotIn("-Hour $realStart.Hour", source)


if __name__ == "__main__":
    unittest.main()
