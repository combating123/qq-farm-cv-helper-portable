import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "portable" / "ui_personalization.py"


def load_module():
    spec = importlib.util.spec_from_file_location("qqfarm_ui_personalization_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeCheckBox:
    def __init__(self, *, visible=True, enabled=True, self_candidate=False):
        self._visible = visible
        self._enabled = enabled
        self._checked = False
        self._properties = {
            "_qqfarm_friend_guard_self_candidate": bool(self_candidate),
        }

    def isVisible(self):
        return self._visible

    def isEnabled(self):
        return self._enabled

    def property(self, name):
        return self._properties.get(name)

    def setChecked(self, value):
        self._checked = bool(value)

    def isChecked(self):
        return self._checked


class FakeButton:
    def __init__(self):
        self.clicks = 0

    def click(self):
        self.clicks += 1


class FriendGuardEditorTests(unittest.TestCase):
    def test_bottom_fixed_self_profile_is_not_a_guard_candidate(self):
        mod = load_module()
        classify = mod._friend_guard_candidate_is_self_overlay
        frame_shape = (800, 428, 3)

        self.assertFalse(classify({"rect": (250, 592, 382, 660)}, frame_shape))
        self.assertTrue(classify({"rect": (250, 704, 382, 772)}, frame_shape))

    def test_bulk_select_skips_hidden_disabled_and_self_candidate_rows(self):
        mod = load_module()
        items = [
            FakeCheckBox(),
            FakeCheckBox(visible=False),
            FakeCheckBox(enabled=False),
            FakeCheckBox(self_candidate=True),
            FakeCheckBox(),
        ]

        selected = mod._friend_guard_select_valid_checkboxes(items, True)

        self.assertEqual(2, selected)
        self.assertEqual([True, False, False, False, True], [x.isChecked() for x in items])

    def test_one_click_select_and_save_checks_valid_rows_then_clicks_native_save(self):
        mod = load_module()
        items = [FakeCheckBox(), FakeCheckBox(self_candidate=True), FakeCheckBox()]
        save = FakeButton()

        selected = mod._friend_guard_select_and_save(items, save)

        self.assertEqual(2, selected)
        self.assertEqual(1, save.clicks)
        self.assertEqual([True, False, True], [x.isChecked() for x in items])

    def test_manual_guard_save_marks_global_and_instance_friend_sections_confirmed(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config-multi.ini"
            path.write_text(
                "[friend]\n"
                "enable_guard_dog_help_only = True\n"
                "guard_dog_detection_mode = friend_guard_list\n\n"
                "[instance.1.friend]\n"
                "enable_guard_dog_help_only = True\n"
                "guard_dog_detection_mode = friend_guard_list\n",
                encoding="utf-8",
            )

            self.assertTrue(
                mod._persist_friend_guard_list_confirmed(True, ini_paths=[str(path)])
            )
            text = path.read_text(encoding="utf-8")
            self.assertEqual(2, text.count("friend_guard_list_confirmed = True"))

            self.assertFalse(
                mod._persist_friend_guard_list_confirmed(True, ini_paths=[str(path)])
            )
            self.assertEqual(
                2,
                path.read_text(encoding="utf-8").count(
                    "friend_guard_list_confirmed = True"
                ),
            )


if __name__ == "__main__":
    unittest.main()
