import ast
import ctypes
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class _FakeUser32:
    def __init__(self, calls):
        self.calls = calls

    def GetWindowLongPtrW(self, hwnd, index):
        self.calls.append(("get-style", int(hwnd), int(index)))
        return 0x00000080

    def SetWindowLongPtrW(self, hwnd, index, value):
        self.calls.append(("set-style", int(hwnd), int(index), int(value)))
        return 0

    def ShowWindowAsync(self, hwnd, command):
        self.calls.append(("show-async", int(hwnd), int(command)))
        return True

    def SetWindowPos(self, hwnd, insert_after, x, y, cx, cy, flags):
        self.calls.append(("pos", int(hwnd), int(flags)))
        return True


class HiddenRestoreFreshFrameTests(unittest.TestCase):
    def test_successful_restore_arms_a_short_fresh_frame_lease(self):
        namespace = load_functions(
            "_qqfarm_restore_hidden_miniapp_taskbar_card"
        )
        calls = []
        fake_ctypes = types.SimpleNamespace(windll=types.SimpleNamespace(
            user32=_FakeUser32(calls)
        ))
        old_frame = object()
        old_ts = time.monotonic()
        namespace.update({
            "_configured_bool": lambda _sections, key, default=False: True,
            "_active_bot_sections": lambda: ("instance.1.bot", "bot"),
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_QQFARM_HIDDEN_RESTORE_LOCK": threading.Lock(),
            "_QQFARM_HIDDEN_RESTORE_COOLDOWN_UNTIL": 0.0,
            "_QQFARM_WGC_FRAME": old_frame,
            "_QQFARM_WGC_FRAME_TS": old_ts,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        with mock.patch.dict(sys.modules, {"ctypes": fake_ctypes}):
            result = namespace[
                "_qqfarm_restore_hidden_miniapp_taskbar_card"
            ]("capture-recovery")

        self.assertTrue(result)
        self.assertTrue(namespace.get(
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"
        ))
        self.assertEqual(id(old_frame), namespace.get(
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_ID"
        ))
        self.assertEqual(old_ts, namespace.get(
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_TS"
        ))
        self.assertGreater(
            namespace.get("_QQFARM_HIDDEN_RESTORE_LEASE_UNTIL", 0.0),
            time.monotonic(),
        )

    def test_wgc_rejects_the_same_source_frame_while_waiting_for_restore_refresh(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace["_qqfarm_capture_wgc_farm_frame"]
        source = np.zeros((800, 428, 3), dtype=np.uint8)
        source_ts = time.monotonic()
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": source_ts,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BAD_GEOMETRY_COUNT": 0,
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_ID": id(source),
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_TS": source_ts,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: True,
        })

        self.assertIsNone(capture(max_age=3.0))
        self.assertTrue(namespace.get(
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"
        ))

    def test_wgc_releases_the_lease_only_after_a_new_source_frame(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace["_qqfarm_capture_wgc_farm_frame"]
        source = np.zeros((800, 428, 3), dtype=np.uint8)
        source_ts = time.monotonic()
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": source_ts,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BAD_GEOMETRY_COUNT": 0,
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_ID": id(object()),
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_TS": source_ts - 0.1,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: True,
        })

        result = capture(max_age=3.0)

        self.assertIsNotNone(result)
        self.assertFalse(namespace.get(
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"
        ))

    def test_wgc_accepts_same_source_object_when_native_timestamp_advances(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace["_qqfarm_capture_wgc_farm_frame"]
        source = np.zeros((800, 428, 3), dtype=np.uint8)
        source_ts = time.monotonic()
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": source_ts + 0.2,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BAD_GEOMETRY_COUNT": 0,
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_ID": id(source),
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_TS": source_ts,
            "_QQFARM_HIDDEN_RESTORE_LEASE_UNTIL": time.monotonic() + 5.0,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: True,
        })

        result = capture(max_age=3.0)

        self.assertIsNotNone(result)
        self.assertFalse(namespace.get(
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"
        ))

    def test_wgc_drops_stale_restore_frame_after_lease_expiry(self):
        namespace = load_functions("_qqfarm_capture_wgc_farm_frame")
        capture = namespace["_qqfarm_capture_wgc_farm_frame"]
        source = np.zeros((800, 428, 3), dtype=np.uint8)
        source_ts = time.monotonic()
        namespace.update({
            "_QQFARM_WGC_FRAME": source,
            "_QQFARM_WGC_FRAME_TS": source_ts,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BAD_GEOMETRY_COUNT": 0,
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_ID": id(source),
            "_QQFARM_HIDDEN_RESTORE_BASE_FRAME_TS": source_ts,
            "_QQFARM_HIDDEN_RESTORE_LEASE_UNTIL": time.monotonic() - 1.0,
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: True,
        })

        result = capture(max_age=3.0)

        self.assertIsNone(result)
        self.assertFalse(namespace.get(
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"
        ))
        self.assertIsNone(namespace.get("_QQFARM_WGC_FRAME"))


if __name__ == "__main__":
    unittest.main()
