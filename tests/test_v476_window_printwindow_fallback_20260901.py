import ast
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_capture_function():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_qqfarm_capture_visible_farm_frame"
    ]
    if not nodes:
        raise AssertionError("hook.py is missing _qqfarm_capture_visible_farm_frame")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"np": np, "__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_qqfarm_capture_visible_farm_frame"], namespace


class WindowPrintWindowFallback20260901Tests(unittest.TestCase):
    def test_wgc_failure_uses_window_owned_printwindow_before_desktop_grab(self):
        capture, namespace = load_capture_function()
        printwindow_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        printwindow_calls = []
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 771,
            "_share_get_rect": lambda _hwnd: (10, 20, 438, 820),
            "_qqfarm_get_physical_window_rect": (
                lambda _hwnd, fallback=None: fallback
            ),
            "_qqfarm_capture_printwindow_farm_frame": (
                lambda hwnd, rect: printwindow_calls.append((hwnd, rect))
                or printwindow_frame
            ),
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: (
                frame is printwindow_frame
            ),
            "_qqfarm_remember_good_capture_frame": lambda _frame: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        with mock.patch(
            "PIL.ImageGrab.grab",
            side_effect=AssertionError("desktop grab must not run first"),
        ):
            result = capture()

        self.assertIs(printwindow_frame, result)
        self.assertEqual([(771, (10, 20, 438, 820))], printwindow_calls)

    def test_hidden_surface_uses_capture_hwnd_when_visible_finder_has_no_rect(self):
        capture, namespace = load_capture_function()
        printwindow_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        printwindow_calls = []
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 0,
            "_qqfarm_find_farm_capture_hwnd": lambda: 772,
            "_share_get_rect": lambda hwnd: (
                (30, 40, 458, 840) if int(hwnd) == 772 else None
            ),
            "_qqfarm_get_physical_window_rect": (
                lambda _hwnd, fallback=None: fallback
            ),
            "_qqfarm_capture_printwindow_farm_frame": (
                lambda hwnd, rect: printwindow_calls.append((hwnd, rect))
                or printwindow_frame
            ),
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: (
                frame is printwindow_frame
            ),
            "_qqfarm_remember_good_capture_frame": lambda _frame: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        with mock.patch(
            "PIL.ImageGrab.grab",
            side_effect=AssertionError("hidden fallback must not use desktop pixels"),
        ):
            result = capture()

        self.assertIs(printwindow_frame, result)
        self.assertEqual([(772, (30, 40, 458, 840))], printwindow_calls)

    def test_hidden_blank_latch_queries_physical_rect_for_capture_hwnd(self):
        capture, namespace = load_capture_function()
        printwindow_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        physical_calls = []
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": time.monotonic() - 10.0,
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_share_find_farm_window_hwnd": lambda: 0,
            "_qqfarm_find_farm_capture_hwnd": lambda: 773,
            "_share_get_rect": lambda _hwnd: (40, 50, 468, 850),
            "_qqfarm_get_physical_window_rect": (
                lambda hwnd, fallback=None: physical_calls.append(int(hwnd))
                or fallback
            ),
            "_qqfarm_capture_printwindow_farm_frame": (
                lambda _hwnd, _rect: printwindow_frame
            ),
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: (
                frame is printwindow_frame
            ),
            "_qqfarm_remember_good_capture_frame": lambda _frame: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        with mock.patch(
            "PIL.ImageGrab.grab",
            side_effect=AssertionError("hidden blank recovery must not grab desktop"),
        ):
            result = capture()

        self.assertIs(printwindow_frame, result)
        self.assertEqual([773], physical_calls)

    def test_missing_printwindow_frame_with_no_visible_hwnd_never_uses_desktop(self):
        capture, namespace = load_capture_function()
        grab_calls = []
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 0,
            "_qqfarm_find_farm_capture_hwnd": lambda: 774,
            "_share_get_rect": lambda _hwnd: (50, 60, 478, 860),
            "_qqfarm_get_physical_window_rect": (
                lambda _hwnd, fallback=None: fallback
            ),
            "_qqfarm_capture_printwindow_farm_frame": lambda *_args: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        with mock.patch(
            "PIL.ImageGrab.grab",
            side_effect=lambda *_args, **_kwargs: grab_calls.append(True) or None,
        ):
            result = capture()

        self.assertIsNone(result)
        self.assertEqual([], grab_calls)


if __name__ == "__main__":
    unittest.main()
