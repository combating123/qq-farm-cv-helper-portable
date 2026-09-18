import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "portable" / "launcher.ps1"


class V486FriendListRolloutGate20260918Tests(unittest.TestCase):
    """The production launcher must not force the temporary self-only rollout."""

    @classmethod
    def setUpClass(cls):
        cls.text = LAUNCHER.read_text(encoding="utf-8-sig")

    def test_friend_patrol_is_not_locked_by_forced_strict_rollout(self):
        assignment = re.search(
            r"(?m)^\s*\$env:QQFARM_STRICT_PLANTING_ROLLOUT\s*=\s*(.+?)\s*$",
            self.text,
        )
        self.assertIsNotNone(
            assignment,
            "launcher must explicitly publish the rollout default for diagnosis",
        )
        self.assertNotEqual(
            "'1'",
            assignment.group(1).strip(),
            "the temporary self-only rollout must not be forced in production",
        )
        self.assertRegex(
            assignment.group(1),
            r"'0'|\"0\"",
            "production default must leave normal friend routing enabled",
        )


if __name__ == "__main__":
    unittest.main()
