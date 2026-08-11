import ast
import time
import types
import unittest
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
DESKTOP = ROOT / "tests" / "fixtures" / "live-hidden-miniapp-desktop-fallback-20260811.png"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FakeStartButton:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.calls = []
    def text(self): return "\u5f00\u59cb\u8fd0\u884c"
    def isVisible(self): return True
    def isEnabled(self): return self.enabled
    def setEnabled(self, value):
        self.enabled = bool(value); self.calls.append(bool(value))
    def setDisabled(self, value): self.setEnabled(not bool(value))


class FakeApp:
    def __init__(self, widgets): self.widgets = list(widgets)
    def allWidgets(self): return list(self.widgets)


class HiddenCaptureAndRestartTests(unittest.TestCase):
    def test_real_hidden_desktop_fixture_is_not_a_farm_scene(self):
        ns = load_functions("_qqfarm_visible_frame_has_farm_scene")
        frame = cv2.imread(str(DESKTOP), cv2.IMREAD_COLOR)
        self.assertIsNotNone(frame)
        self.assertFalse(ns["_qqfarm_visible_frame_has_farm_scene"](frame))

    def test_native_desktop_fallback_is_rejected_and_stale_cache_is_cleared(self):
        ns = load_functions(
            "_qqfarm_visible_frame_has_farm_scene",
            "_qqfarm_remember_good_capture_frame",
            "_qqfarm_recent_good_capture_frame",
            "_qqfarm_native_capture_frame_is_business_safe",
            "_get_frame_from_bot",
        )
        desktop = cv2.imread(str(DESKTOP), cv2.IMREAD_COLOR)
        stale = object()
        class Capture:
            def get_window_frame(self): return desktop
        bot = types.SimpleNamespace(screen_capture=Capture())
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
            "_qqfarm_native_capture_fallback_allowed": lambda: True,
            "_qqfarm_note_native_capture_fallback": lambda: None,
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": stale,
            "_QQFARM_LAST_GOOD_CAPTURE_TS": time.monotonic(),
            "_throttled_write": lambda *a, **k: None,
        })
        self.assertIsNone(ns["_get_frame_from_bot"](bot))
        self.assertIsNone(ns.get("_QQFARM_LAST_GOOD_CAPTURE_FRAME"))
        self.assertEqual(0.0, ns.get("_QQFARM_LAST_GOOD_CAPTURE_TS"))

    def test_start_button_is_reenabled_when_qq_farm_window_is_missing(self):
        ns = load_functions("_qqfarm_reenable_start_without_window")
        self.assertIn("_qqfarm_reenable_start_without_window", ns)
        button = FakeStartButton(False); app = FakeApp([button])
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_qt_runtime_already_running": lambda current: False,
            "_share_find_farm_window_hwnd": lambda: 0,
        })
        self.assertEqual(1, ns["_qqfarm_reenable_start_without_window"](app))
        self.assertTrue(button.enabled)

    def test_start_button_stays_disabled_while_runtime_is_starting_or_running(self):
        ns = load_functions("_qqfarm_reenable_start_without_window")
        self.assertIn("_qqfarm_reenable_start_without_window", ns)
        button = FakeStartButton(False); app = FakeApp([button])
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_qt_runtime_already_running": lambda current: True,
            "_share_find_farm_window_hwnd": lambda: 0,
        })
        self.assertEqual(0, ns["_qqfarm_reenable_start_without_window"](app))
        self.assertFalse(button.enabled)


if __name__ == "__main__": unittest.main()
