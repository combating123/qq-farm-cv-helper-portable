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


class FakeSignal:
    def __init__(self, *slots):
        self.slots = list(slots)

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self):
        self.slots.clear()

    def emit(self):
        for slot in list(self.slots):
            slot(False)


class FakeAboutButton:
    def __init__(self, native_slot):
        self.clicked = FakeSignal(native_slot)
        self._properties = {}
        self._tooltip = "\u5173\u4e8e"

    def objectName(self):
        return "githubBtn"

    def text(self):
        return ""

    def toolTip(self):
        return self._tooltip

    def setToolTip(self, value):
        self._tooltip = str(value)

    def property(self, name):
        return self._properties.get(name)

    def setProperty(self, name, value):
        self._properties[name] = value


class FakeWidget:
    def __init__(self, *, name="", text="", parent=None):
        self._name = name
        self._text = text
        self._parent = parent
        self.hidden = False
        self.visible = True

    def objectName(self):
        return self._name

    def text(self):
        return self._text

    def toolTip(self):
        return ""

    def parentWidget(self):
        return self._parent

    def hide(self):
        self.hidden = True
        self.visible = False

    def setVisible(self, value):
        self.visible = bool(value)


class FriendGuardEditorTests(unittest.TestCase):
    def test_about_button_replaces_native_dialog_before_first_paint(self):
        mod = load_module()
        events = []

        def native_dialog(checked=False):
            events.append("native")

        button = FakeAboutButton(native_dialog)
        mod._show_project_info_dialog = (
            lambda anchor=None, opener=None: events.append(("project", anchor))
        )

        changed = mod.patch_widget(button)
        button.clicked.emit()

        self.assertEqual(1, changed)
        self.assertNotIn("native", events)
        self.assertEqual([("project", button)], events)
        self.assertTrue(button.property(mod._ABOUT_MARK))
        self.assertIn("GitHub", button.toolTip())

    def test_about_button_remains_project_dialog_after_repeated_patch_passes(self):
        mod = load_module()
        events = []
        button = FakeAboutButton(lambda checked=False: events.append("native"))
        mod._show_project_info_dialog = (
            lambda anchor=None, opener=None: events.append(("project", anchor))
        )
        opener = lambda url: events.append(("url", url))

        mod.patch_widget(button, opener=opener)
        mod.patch_widget(button, opener=opener)
        button.clicked.emit()

        self.assertEqual([("project", button)], events)

    def test_about_expiry_title_hides_unnamed_parent_card(self):
        mod = load_module()
        card = FakeWidget(name="")
        title = FakeWidget(name="aboutSectionTitle", parent=card)

        mod._hide_parent_card(title)

        self.assertTrue(card.hidden)
        self.assertFalse(card.visible)

    def test_about_expiry_copy_is_removed_even_without_object_name(self):
        mod = load_module()
        card = FakeWidget(name="")
        title = FakeWidget(text="\u8fc7\u671f\u65f6\u95f4", parent=card)

        changed = mod.patch_widget(title)

        self.assertEqual(1, changed)
        self.assertTrue(card.hidden)
        self.assertFalse(card.visible)

    def test_friend_screenshot_card_stays_visible_when_status_is_cleaned(self):
        mod = load_module()
        card = FakeWidget(name="templateDebugCard")
        status = FakeWidget(
            name="templateDebugStatus",
            text="\u72b6\u6001\uff1a\u7b49\u5f85\u622a\u56fe",
            parent=card,
        )

        changed = mod.patch_widget(status)

        self.assertEqual(1, changed)
        self.assertFalse(status.visible)
        self.assertTrue(card.visible)
        self.assertFalse(card.hidden)

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
