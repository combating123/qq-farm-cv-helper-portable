import ast
import time
import types
import unittest
from pathlib import Path

import cv2
import numpy as np

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


    def test_repeated_blank_wgc_surface_restarts_capture_session(self):
        ns = load_functions("_qqfarm_capture_wgc_farm_frame")
        events = []
        blank = np.full((800, 428, 3), 255, dtype=np.uint8)

        def stop_capture(reason=""):
            events.append(reason)
            ns["_QQFARM_WGC_CAPTURE"] = None
            ns["_QQFARM_WGC_CONTROL"] = None
            return True

        ns.update({
            "np": np,
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": object(),
            "_QQFARM_WGC_FRAME": blank,
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BLANK_COUNT": 0,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: False,
            "_qqfarm_stop_wgc_capture": stop_capture,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        self.assertIsNone(ns["_qqfarm_capture_wgc_farm_frame"]())
        self.assertIsNone(ns["_qqfarm_capture_wgc_farm_frame"]())
        self.assertIn("blank-surface", events)
        self.assertGreater(ns.get("_QQFARM_WGC_BLANK_TS", 0.0), 0.0)


    def test_visible_window_allows_validated_native_fallback_after_wgc_blank(self):
        ns = load_functions("_qqfarm_native_capture_fallback_allowed")
        ns.update({
            "_QQFARM_WGC_BLANK_TS": 90.0,
            "_QQFARM_WGC_START_ATTEMPT_TS": 80.0,
            "_QQFARM_WGC_STARTED_TS": 80.0,
            "_QQFARM_VISIBLE_CAPTURE_OCCLUDED_TS": 0.0,
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_NATIVE_CAPTURE_LAST_TS": 0.0,
            "_qqfarm_farm_window_is_visible": lambda: True,
        })
        self.assertTrue(ns["_qqfarm_native_capture_fallback_allowed"](now=100.0))

    def test_hidden_window_keeps_native_fallback_blocked_after_wgc_blank(self):
        ns = load_functions("_qqfarm_native_capture_fallback_allowed")
        ns.update({
            "_QQFARM_WGC_BLANK_TS": 90.0,
            "_QQFARM_WGC_START_ATTEMPT_TS": 80.0,
            "_QQFARM_WGC_STARTED_TS": 80.0,
            "_QQFARM_VISIBLE_CAPTURE_OCCLUDED_TS": 0.0,
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_NATIVE_CAPTURE_LAST_TS": 0.0,
            "_qqfarm_farm_window_is_visible": lambda: False,
        })
        self.assertFalse(ns["_qqfarm_native_capture_fallback_allowed"](now=100.0))

    def test_wgc_rebinds_when_qq_farm_window_handle_changes(self):
        ns = load_functions("_qqfarm_start_wgc_capture")
        events = []

        class ExistingControl:
            def is_finished(self): return False

        class ReplacementControl:
            def is_finished(self): return False

        class ReplacementCapture:
            def __init__(self, frame_callback, close_callback, window_hwnd=None, **kwargs):
                events.append(("created", int(window_hwnd or 0)))
            def start_free_threaded(self):
                events.append(("started",))
                return ReplacementControl()

        def stop_capture(reason=""):
            events.append(("stopped", reason))
            ns["_QQFARM_WGC_CAPTURE"] = None
            ns["_QQFARM_WGC_CONTROL"] = None
            return True

        ns.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": ExistingControl(),
            "_QQFARM_WGC_BOUND_HWND": 111,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 222,
            "_qqfarm_stop_wgc_capture": stop_capture,
            "_qqfarm_deconflict_assistant_window_titles": lambda: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: ReplacementCapture,
            "_qqfarm_wgc_frame_arrived": lambda *args, **kwargs: None,
            "_qqfarm_wgc_closed": lambda *args, **kwargs: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        self.assertTrue(ns["_qqfarm_start_wgc_capture"]())
        self.assertIn(("stopped", "window-handle-changed"), events)
        self.assertIn(("created", 222), events)
        self.assertEqual(222, ns.get("_QQFARM_WGC_BOUND_HWND"))


if __name__ == "__main__": unittest.main()
