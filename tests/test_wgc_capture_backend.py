import ast
import ctypes
import time
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FakeWidget:
    def __init__(self, title, visible=True):
        self._title = title
        self._visible = visible
        self.set_calls = []

    def windowTitle(self):
        return self._title

    def setWindowTitle(self, title):
        self._title = title
        self.set_calls.append(title)

    def isVisible(self):
        return self._visible


class FakeApplication:
    def __init__(self, widgets):
        self._widgets = list(widgets)

    def topLevelWidgets(self):
        return list(self._widgets)


class WGCCaptureBackendTests(unittest.TestCase):
    def test_assistant_title_is_deconflicted_without_touching_exact_game_title(self):
        namespace = load_functions("_qqfarm_deconflict_assistant_window_titles")
        rename = namespace.get("_qqfarm_deconflict_assistant_window_titles")
        self.assertIsNotNone(rename)
        assistant = FakeWidget(
            "QQ\u7ecf\u5178\u519c\u573a - \u89c6\u89c9\u81ea\u52a8\u5316"
        )
        game = FakeWidget("QQ\u7ecf\u5178\u519c\u573a")
        unrelated = FakeWidget("Settings")
        app = FakeApplication([assistant, game, unrelated])

        changed = rename(app)

        self.assertEqual(1, changed)
        self.assertEqual(
            "\u519c\u573a\u52a9\u624b - \u89c6\u89c9\u81ea\u52a8\u5316",
            assistant.windowTitle(),
        )
        self.assertEqual("QQ\u7ecf\u5178\u519c\u573a", game.windowTitle())
        self.assertEqual("Settings", unrelated.windowTitle())

    def test_qt_maintenance_reapplies_title_deconfliction(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        body = source.split("def _qt_unlock_pass", 1)[1].split(
            "def _has_real_main_window", 1
        )[0]
        self.assertIn("_qqfarm_deconflict_assistant_window_titles(app)", body)

    def test_wgc_callback_drops_frames_inside_the_copy_interval(self):
        namespace = load_functions("_qqfarm_wgc_frame_arrived")
        callback = namespace["_qqfarm_wgc_frame_arrived"]
        namespace.update({
            "_QQFARM_WGC_FRAME": None,
            "_QQFARM_WGC_FRAME_TS": 0.0,
            "_QQFARM_WGC_RAW_SIZE": None,
            "_QQFARM_WGC_FRAME_ACCEPT_TS": 0.0,
            "_QQFARM_WGC_FRAME_COPY_INTERVAL": 10.0,
        })
        first = (ctypes.c_ubyte * 4)(10, 20, 30, 255)
        second = (ctypes.c_ubyte * 4)(90, 80, 70, 255)

        callback(ctypes.addressof(first), len(first), 1, 1, [], 1.0)
        accepted = namespace["_QQFARM_WGC_FRAME"]
        callback(ctypes.addressof(second), len(second), 1, 1, [], 2.0)

        self.assertIs(accepted, namespace["_QQFARM_WGC_FRAME"])
        self.assertEqual(10, int(namespace["_QQFARM_WGC_FRAME"][0, 0, 0]))

    def test_wgc_callback_uses_single_contiguous_copy(self):
        namespace = load_functions("_qqfarm_wgc_frame_arrived")
        callback = namespace["_qqfarm_wgc_frame_arrived"]

        class CopyForbiddenArray(np.ndarray):
            def copy(self, *args, **kwargs):
                raise AssertionError("callback attempted a redundant second copy")

        class NumpyProxy:
            ctypeslib = np.ctypeslib

            @staticmethod
            def ascontiguousarray(value):
                return np.ascontiguousarray(value).view(CopyForbiddenArray)

        namespace.update({
            "np": NumpyProxy,
            "_QQFARM_WGC_FRAME": None,
            "_QQFARM_WGC_FRAME_TS": 0.0,
            "_QQFARM_WGC_RAW_SIZE": None,
            "_QQFARM_WGC_FRAME_ACCEPT_TS": 0.0,
            "_QQFARM_WGC_FRAME_COPY_INTERVAL": 0.0,
        })
        raw = (ctypes.c_ubyte * 16)(
            10, 20, 30, 255, 40, 50, 60, 255,
            70, 80, 90, 255, 100, 110, 120, 255,
        )

        callback(ctypes.addressof(raw), len(raw), 2, 2, [], 1.0)

        frame = namespace["_QQFARM_WGC_FRAME"]
        self.assertIsNotNone(frame)
        self.assertTrue(frame.flags.c_contiguous)
        self.assertEqual((2, 2, 3), frame.shape)
        self.assertEqual(10, int(frame[0, 0, 0]))
        raw[0] = 199
        self.assertEqual(10, int(frame[0, 0, 0]))

    def test_finished_wgc_control_clears_blank_surface_latch(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")

        class FinishedControl:
            def is_finished(self):
                return True

        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": FinishedControl(),
            "_QQFARM_WGC_BLANK_TS": time.monotonic(),
            "_QQFARM_WGC_START_ATTEMPT_TS": time.monotonic(),
        })

        self.assertFalse(namespace["_qqfarm_start_wgc_capture"]())
        self.assertEqual(0.0, namespace["_QQFARM_WGC_BLANK_TS"])

    def test_wgc_start_renames_assistant_before_title_fallback_with_known_hwnd(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        start = namespace.get("_qqfarm_start_wgc_capture")
        self.assertIsNotNone(start)
        events = []
        instances = []

        class FakeCapture:
            def __init__(self, callback, on_closed, **kwargs):
                events.append("construct")
                self.callback = callback
                self.on_closed = on_closed
                self.kwargs = kwargs
                self.started = False
                instances.append(self)

            def start_free_threaded(self):
                events.append("start")
                self.started = True

        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_qqfarm_deconflict_assistant_window_titles": (
                lambda app=None: events.append("rename") or 1
            ),
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: FakeCapture,
            # The compatibility capture class has no ``window_hwnd``
            # constructor parameter.  A concrete farm handle is still
            # required before the title-only fallback can be selected.
            "_share_find_farm_window_hwnd": lambda: 25167910,
            "_qqfarm_wgc_frame_arrived": lambda *args: None,
            "_qqfarm_wgc_closed": lambda *args: None,
            "_throttled_write": lambda *args: None,
        })

        self.assertTrue(start())
        self.assertEqual(["rename", "construct", "start"], events)
        self.assertEqual(1, len(instances))
        self.assertTrue(instances[0].started)
        self.assertEqual(
            "QQ\u7ecf\u5178\u519c\u573a",
            instances[0].kwargs.get("window_name"),
        )

    def test_wgc_start_prefers_farm_hwnd_when_capture_supports_it(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        start = namespace.get("_qqfarm_start_wgc_capture")
        self.assertIsNotNone(start)
        instances = []

        class HwndCapture:
            def __init__(
                    self, callback, on_closed, window_hwnd=None, **kwargs):
                self.callback = callback
                self.on_closed = on_closed
                self.window_hwnd = window_hwnd
                self.kwargs = kwargs
                instances.append(self)

            def start_free_threaded(self):
                return object()

        farm_hwnd = 25167910
        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_qqfarm_deconflict_assistant_window_titles": lambda app=None: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: HwndCapture,
            "_share_find_farm_window_hwnd": lambda: farm_hwnd,
            "_qqfarm_wgc_frame_arrived": lambda *args: None,
            "_qqfarm_wgc_closed": lambda *args: None,
            "_throttled_write": lambda *args: None,
        })

        self.assertTrue(start())
        self.assertEqual(1, len(instances))
        self.assertEqual(farm_hwnd, instances[0].window_hwnd)
        self.assertNotIn("window_name", instances[0].kwargs)
        self.assertEqual(333, instances[0].kwargs.get("minimum_update_interval"))

    def test_wgc_start_tries_known_hwnd_when_native_signature_is_opaque(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        start = namespace.get("_qqfarm_start_wgc_capture")
        self.assertIsNotNone(start)
        instances = []

        class OpaqueHwndCapture:
            # Some C-extension builds accept the HWND keyword while exposing
            # no inspectable constructor signature.  The selector must still
            # be attempted with the concrete farm handle first.
            __signature__ = object()

            def __init__(self, callback, on_closed, window_hwnd=None, **kwargs):
                self.window_hwnd = window_hwnd
                self.kwargs = kwargs
                instances.append(self)

            def start_free_threaded(self):
                return object()

        farm_hwnd = 25167910
        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_qqfarm_deconflict_assistant_window_titles": lambda app=None: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": (
                lambda: OpaqueHwndCapture
            ),
            "_qqfarm_find_farm_capture_hwnd": lambda: farm_hwnd,
            "_qqfarm_wgc_frame_arrived": lambda *args: None,
            "_qqfarm_wgc_closed": lambda *args: None,
            "_throttled_write": lambda *args: None,
        })

        self.assertTrue(start())
        self.assertEqual(1, len(instances))
        self.assertEqual(farm_hwnd, instances[0].window_hwnd)
        self.assertNotIn("window_name", instances[0].kwargs)

    def test_wgc_start_falls_back_to_title_when_opaque_build_rejects_hwnd(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        start = namespace.get("_qqfarm_start_wgc_capture")
        self.assertIsNotNone(start)
        attempts = []

        class OpaqueTitleCapture:
            __signature__ = object()

            def __init__(self, callback, on_closed, **kwargs):
                attempts.append(dict(kwargs))
                if "window_hwnd" in kwargs:
                    raise TypeError("window_hwnd is not supported")
                self.kwargs = kwargs

            def start_free_threaded(self):
                return object()

        farm_hwnd = 25167910
        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_qqfarm_deconflict_assistant_window_titles": lambda app=None: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": (
                lambda: OpaqueTitleCapture
            ),
            "_qqfarm_find_farm_capture_hwnd": lambda: farm_hwnd,
            "_qqfarm_wgc_frame_arrived": lambda *args: None,
            "_qqfarm_wgc_closed": lambda *args: None,
            "_throttled_write": lambda *args: None,
        })

        self.assertTrue(start())
        self.assertEqual(2, len(attempts))
        self.assertEqual(farm_hwnd, attempts[0]["window_hwnd"])
        self.assertNotIn("window_hwnd", attempts[1])
        self.assertEqual(
            "QQ\u7ecf\u5178\u519c\u573a",
            attempts[1].get("window_name"),
        )

    def test_wgc_callback_copies_bgra_pixels_into_owned_bgr_frame(self):
        namespace = load_functions("_qqfarm_wgc_frame_arrived")
        callback = namespace.get("_qqfarm_wgc_frame_arrived")
        self.assertIsNotNone(callback)
        namespace.update({
            "_QQFARM_WGC_FRAME": None,
            "_QQFARM_WGC_FRAME_TS": 0.0,
            "_QQFARM_WGC_RAW_SIZE": None,
        })
        raw = (ctypes.c_ubyte * 8)(
            10, 20, 30, 255,
            40, 50, 60, 255,
        )

        callback(ctypes.addressof(raw), len(raw), 2, 1, [], 123.0)
        frame = namespace.get("_QQFARM_WGC_FRAME")

        self.assertIsNotNone(frame)
        self.assertEqual((1, 2, 3), frame.shape)
        np.testing.assert_array_equal(
            np.array([[[10, 20, 30], [40, 50, 60]]], dtype=np.uint8),
            frame,
        )
        raw[0] = 99
        self.assertEqual(10, int(frame[0, 0, 0]))
        self.assertEqual((2, 1), namespace.get("_QQFARM_WGC_RAW_SIZE"))
        self.assertGreater(namespace.get("_QQFARM_WGC_FRAME_TS", 0.0), 0.0)

    def test_rendered_surface_gate_rejects_blank_webview_and_accepts_game(self):
        namespace = load_functions("_qqfarm_wgc_frame_is_rendered_game_surface")
        gate = namespace.get("_qqfarm_wgc_frame_is_rendered_game_surface")
        self.assertIsNotNone(gate)
        fixtures = ROOT / "tests" / "fixtures"
        blank = cv2.imread(str(fixtures / "blank-qq-webview-20260803.png"))
        home = cv2.imread(str(
            fixtures / "live-full-yellow-seedling-false-empty-20260803.png"
        ))
        friend = cv2.imread(str(fixtures / "friend_farm_current_live_sanitized.png"))

        self.assertIsNotNone(blank)
        self.assertIsNotNone(home)
        self.assertIsNotNone(friend)
        self.assertFalse(gate(blank))
        self.assertTrue(gate(home))
        self.assertTrue(gate(friend))

    def test_blank_wgc_frame_is_rejected_and_clears_stale_safe_cache(self):
        namespace = load_functions(
            "_qqfarm_wgc_frame_is_rendered_game_surface",
            "_qqfarm_capture_wgc_farm_frame",
        )
        fixtures = ROOT / "tests" / "fixtures"
        blank = cv2.imread(str(fixtures / "blank-qq-webview-20260803.png"))
        self.assertIsNotNone(blank)
        stale = object()
        namespace.update({
            "_QQFARM_WGC_FRAME": blank,
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": stale,
            "_QQFARM_LAST_GOOD_CAPTURE_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": stale,
            "_QQFARM_LAST_WGC_NORMALIZED_TS": time.monotonic(),
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_throttled_write": lambda *args: None,
        })

        frame = namespace["_qqfarm_capture_wgc_farm_frame"](max_age=3.0)

        self.assertIsNone(frame)
        self.assertIsNone(namespace["_QQFARM_LAST_GOOD_CAPTURE_FRAME"])
        self.assertEqual(0.0, namespace["_QQFARM_LAST_GOOD_CAPTURE_TS"])
        self.assertIsNone(namespace["_QQFARM_LAST_WGC_NORMALIZED_FRAME"])
        self.assertGreater(namespace["_QQFARM_WGC_BLANK_TS"], 0.0)

    def test_visible_capture_prefers_wgc_before_desktop_image_grab(self):
        namespace = load_functions("_qqfarm_capture_visible_farm_frame")
        capture = namespace.get("_qqfarm_capture_visible_farm_frame")
        self.assertIsNotNone(capture)
        wgc = object()
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: wgc,
            "_share_find_farm_window_hwnd": (
                lambda: self.fail("desktop capture must not run after WGC succeeds")
            ),
        })

        self.assertIs(wgc, capture())

    def test_latched_blank_wgc_skips_expensive_desktop_fallback(self):
        namespace = load_functions("_qqfarm_capture_visible_farm_frame")
        capture = namespace.get("_qqfarm_capture_visible_farm_frame")
        self.assertIsNotNone(capture)
        desktop_calls = []
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": time.monotonic() - 30.0,
            "_share_find_farm_window_hwnd": (
                lambda: desktop_calls.append("find-window") or 0
            ),
        })

        self.assertIsNone(capture())
        self.assertEqual([], desktop_calls)

    def test_native_fallback_is_blocked_while_blank_wgc_is_latched(self):
        namespace = load_functions("_qqfarm_native_capture_fallback_allowed")
        gate = namespace.get("_qqfarm_native_capture_fallback_allowed")
        self.assertIsNotNone(gate)
        now = time.monotonic()
        namespace.update({
            "_QQFARM_WGC_BLANK_TS": now - 30.0,
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_QQFARM_WGC_STARTED_TS": 0.0,
            "_QQFARM_VISIBLE_CAPTURE_OCCLUDED_TS": 0.0,
            "_QQFARM_NATIVE_CAPTURE_LAST_TS": 0.0,
        })

        self.assertFalse(gate(now=now))

    def test_wgc_cached_frame_is_normalized_to_game_coordinates(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace.get("_qqfarm_capture_wgc_farm_frame")
        self.assertIsNotNone(capture)
        source = np.zeros((1200, 642, 3), dtype=np.uint8)
        source[:, :, 0] = 180
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda frame: True,
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: True,
            "_QQFARM_WGC_BLANK_TS": time.monotonic() - 30.0,
        })

        frame = capture(max_age=3.0)

        self.assertIsNotNone(frame)
        self.assertEqual((800, 428, 3), frame.shape)
        self.assertIsNot(frame, source)
        self.assertEqual(0.0, namespace["_QQFARM_WGC_BLANK_TS"])

    def test_wgc_capture_reuses_normalized_frame_for_same_source_timestamp(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace["_qqfarm_capture_wgc_farm_frame"]
        source_ts = time.monotonic()
        source = np.zeros((800, 428, 3), dtype=np.uint8)
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": source_ts,
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": None,
            "_QQFARM_LAST_WGC_NORMALIZED_TS": 0.0,
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS": 0.0,
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID": 0,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BAD_GEOMETRY_COUNT": 0,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda frame: True,
        })

        first = capture(max_age=3.0)
        second = capture(max_age=3.0)

        self.assertIsNotNone(first)
        self.assertIs(first, second)

        fresh_source = source.copy()
        fresh_source[0, 0, 0] = 99
        namespace["_QQFARM_WGC_FRAME"] = fresh_source
        namespace["_QQFARM_WGC_FRAME_TS"] = source_ts + 0.01

        third = capture(max_age=3.0)

        self.assertIsNotNone(third)
        self.assertIsNot(first, third)
        self.assertEqual(99, int(third[0, 0, 0]))

    def test_wgc_close_clears_blank_surface_latch(self):
        namespace = load_functions("_qqfarm_wgc_closed")
        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": object(),
            "_QQFARM_WGC_BLANK_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": object(),
            "_QQFARM_LAST_WGC_NORMALIZED_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID": 123,
            "_throttled_write": lambda *args: None,
        })

        namespace["_qqfarm_wgc_closed"]()

        self.assertEqual(0.0, namespace["_QQFARM_WGC_BLANK_TS"])
        self.assertIsNone(namespace["_QQFARM_LAST_WGC_NORMALIZED_FRAME"])
        self.assertEqual(0.0, namespace["_QQFARM_LAST_WGC_NORMALIZED_TS"])
        self.assertEqual(0.0, namespace["_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS"])
        self.assertEqual(0, namespace["_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID"])

    def test_wgc_stop_clears_blank_surface_latch(self):
        namespace = load_functions("_qqfarm_stop_wgc_capture")
        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": object(),
            "_QQFARM_WGC_BLANK_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": object(),
            "_QQFARM_LAST_WGC_NORMALIZED_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID": 123,
            "_throttled_write": lambda *args: None,
        })

        namespace["_qqfarm_stop_wgc_capture"]("test")

        self.assertEqual(0.0, namespace["_QQFARM_WGC_BLANK_TS"])
        self.assertIsNone(namespace["_QQFARM_LAST_WGC_NORMALIZED_FRAME"])
        self.assertEqual(0.0, namespace["_QQFARM_LAST_WGC_NORMALIZED_TS"])
        self.assertEqual(0.0, namespace["_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS"])
        self.assertEqual(0, namespace["_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID"])


if __name__ == "__main__":
    unittest.main()
