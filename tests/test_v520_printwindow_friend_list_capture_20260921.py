import ast
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FRIEND_LIST_FIXTURE = (
    ROOT / "tests" / "fixtures" / "live-v422-visible-friend-list-20260808-0346.png"
)
TASK_FIXTURE = (
    ROOT / "tests" / "fixtures" / "live-v422-current-friend-list-20260808.png"
)


def load_capture_function():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_qqfarm_capture_visible_farm_frame"
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "np": np}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_qqfarm_capture_visible_farm_frame"], namespace


def load_frame_from_bot_function():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_get_frame_from_bot"
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_get_frame_from_bot"], namespace


def read_bgr(path):
    encoded = np.fromfile(str(path), dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        raise AssertionError(f"fixture cannot be decoded: {path}")
    return frame


class V520PrintWindowFriendListCaptureTests(unittest.TestCase):
    def _capture(self, printwindow_frame, friend_rows):
        capture, namespace = load_capture_function()
        fallback = np.zeros((800, 428, 3), dtype=np.uint8)
        logs = []
        namespace.update(
            {
                "_qqfarm_capture_wgc_farm_frame": lambda: None,
                "_QQFARM_WGC_BLANK_TS": 0.0,
                "_share_find_farm_window_hwnd": lambda: 771,
                "_share_get_rect": lambda _hwnd: (10, 20, 589, 1083),
                "_qqfarm_get_physical_window_rect": (
                    lambda _hwnd, fallback_rect=None: fallback_rect
                ),
                "_qqfarm_capture_printwindow_farm_frame": (
                    lambda _hwnd, _rect: printwindow_frame
                ),
                "_qqfarm_visible_frame_has_farm_scene": lambda _frame: False,
                "_friend_list_visit_button_rows": (
                    lambda frame: friend_rows if frame is printwindow_frame else []
                ),
                "_qqfarm_remember_good_capture_frame": lambda _frame: None,
                "_throttled_write": lambda *args, **_kwargs: logs.append(args),
            }
        )
        with patch(
            "PIL.ImageGrab.grab",
            return_value=Image.fromarray(
                cv2.cvtColor(fallback, cv2.COLOR_BGR2RGB), mode="RGB"
            ),
        ):
            result = capture(prefer_desktop=True)
        return result, logs

    def test_window_owned_friend_list_is_authoritative_before_desktop_grab(self):
        friend_list = read_bgr(FRIEND_LIST_FIXTURE)
        rows = [{"center": (400, 300 + index * 120)} for index in range(5)]

        result, logs = self._capture(friend_list, rows)

        self.assertIs(friend_list, result, logs)
        self.assertFalse(
            any("v311 visible QQ rectangle" in str(item) for item in logs),
            logs,
        )

    def test_window_owned_task_surface_stays_rejected(self):
        task_panel = read_bgr(TASK_FIXTURE)

        result, _logs = self._capture(task_panel, [])

        self.assertIsNone(result)

    def test_window_owned_friend_list_survives_frame_from_bot_capture_gate(self):
        """A validated physical friend list must not fall through to native desktop capture."""
        friend_list = read_bgr(FRIEND_LIST_FIXTURE)
        get_frame, namespace = load_frame_from_bot_function()
        native_calls = []
        fallback = types.SimpleNamespace(
            get_window_frame=lambda: native_calls.append("native") or None
        )
        bot = types.SimpleNamespace(screen_capture=fallback)
        rows = [{"center": (400, 300 + index * 120)} for index in range(5)]
        namespace.update(
            {
                "_active_is_qq_mode": lambda: True,
                "_active_is_weixin_mode": lambda: False,
                "_qqfarm_capture_visible_farm_frame": lambda: friend_list,
                "_qqfarm_prepare_visible_frame_for_business": lambda frame: frame,
                "_qqfarm_visible_capture_frame_is_trusted": lambda _frame: False,
                "_qqfarm_visible_frame_has_farm_scene": lambda _frame: False,
                "_friend_list_visit_button_rows": lambda _frame: rows,
                "_qqfarm_native_capture_fallback_allowed": lambda: True,
                "_qqfarm_note_native_capture_fallback": lambda: None,
                "_qqfarm_native_capture_frame_is_business_safe": lambda _frame: False,
                "_qqfarm_recent_good_capture_frame": lambda: None,
                "_qqfarm_remember_good_capture_frame": lambda _frame: None,
            }
        )

        result = get_frame(bot)

        self.assertIs(friend_list, result)
        self.assertEqual([], native_calls)


if __name__ == "__main__":
    unittest.main()
