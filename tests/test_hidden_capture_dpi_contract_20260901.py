import ast
import sys
import threading
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


class HiddenCaptureDpiContractTests(unittest.TestCase):
    def test_printwindow_capture_records_physical_provenance_for_normalization(self):
        namespace = load_functions("_qqfarm_capture_visible_farm_frame")
        capture = namespace["_qqfarm_capture_visible_farm_frame"]
        raw_physical = np.zeros((1200, 642, 3), dtype=np.uint8)
        namespace.update({
            "_qqfarm_capture_wgc_farm_frame": lambda: None,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 591632,
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_share_get_rect": lambda _hwnd: (5, 5, 433, 805),
            "_qqfarm_get_physical_window_rect": (
                lambda _hwnd, fallback=None: (8, 8, 650, 1208)
            ),
            "_qqfarm_capture_printwindow_farm_frame": (
                lambda _hwnd, _rect: raw_physical
            ),
            "_qqfarm_visible_frame_has_farm_scene": lambda _frame: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        result = capture()

        self.assertIs(raw_physical, result)
        self.assertEqual(591632, namespace.get(
            "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_HWND"
        ))
        self.assertEqual((8, 8, 650, 1208), namespace.get(
            "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_RECT"
        ))

    def test_physical_printwindow_frame_is_normalized_before_business_return(self):
        namespace = load_functions("_get_frame_from_bot")
        raw_physical = np.zeros((1200, 642, 3), dtype=np.uint8)
        normalized = np.full((800, 428, 3), 17, dtype=np.uint8)
        calls = []

        def normalize(frame):
            calls.append(frame)
            return normalized

        bot = types.SimpleNamespace()
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: raw_physical,
            "_qqfarm_visible_capture_frame_is_trusted": lambda _frame: False,
            "_qqfarm_visible_frame_has_farm_scene": lambda _frame: True,
            "_qqfarm_prepare_visible_frame_for_business": normalize,
            "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_FRAME_ID": id(raw_physical),
            "_QQFARM_LAST_VISIBLE_CAPTURE_FRAME_ID": id(raw_physical),
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(normalized, result)
        self.assertEqual(1, len(calls))
        self.assertIs(raw_physical, calls[0])
        self.assertEqual((800, 428, 3), result.shape)

    def test_client_geometry_maps_virtual_window_to_physical_frame_without_guessing(self):
        namespace = load_functions("_qqfarm_compute_client_crop_box")
        compute = namespace.get("_qqfarm_compute_client_crop_box")
        self.assertTrue(callable(compute))

        # The live 150% case is a borderless client surface: the DWM frame and
        # the client surface have the same physical bounds.
        self.assertEqual(
            (0, 0, 642, 1200),
            compute(
                (642, 1200),
                (8, 8, 650, 1208),
                (5, 5, 433, 805),
                (0, 0, 428, 800),
                (5, 5),
            ),
        )

        # A window with a real non-client inset must crop that inset before
        # resizing, rather than shifting all template coordinates.
        self.assertEqual(
            (9, 18, 651, 1218),
            compute(
                (660, 1230),
                (8, 8, 668, 1238),
                (5, 5, 445, 825),
                (0, 0, 428, 800),
                (11, 17),
            ),
        )

    def test_blank_hidden_recovery_is_not_blocked_by_disabled_optional_compat_flag(self):
        namespace = load_functions(
            "_qqfarm_restore_hidden_miniapp_taskbar_card"
        )
        calls = []

        class FakeUser32:
            def GetWindowLongPtrW(self, hwnd, index):
                calls.append(("get-style", int(hwnd), int(index)))
                return 0x00000080

            def SetWindowLongPtrW(self, hwnd, index, value):
                calls.append(("set-style", int(hwnd), int(index), int(value)))
                return 0

            def ShowWindowAsync(self, hwnd, command):
                calls.append(("show-async", int(hwnd), int(command)))
                return True

            def SetWindowPos(self, hwnd, insert_after, x, y, cx, cy, flags):
                calls.append(("pos", int(hwnd), int(flags)))
                return True

        fake_ctypes = types.SimpleNamespace(windll=types.SimpleNamespace(
            user32=FakeUser32()
        ))
        namespace.update({
            "_configured_bool": lambda _sections, key, default=False: False,
            "_active_bot_sections": lambda: ("instance.1.bot", "bot"),
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_QQFARM_HIDDEN_RESTORE_LOCK": threading.Lock(),
            "_QQFARM_HIDDEN_RESTORE_COOLDOWN_UNTIL": 0.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        with mock.patch.dict(sys.modules, {"ctypes": fake_ctypes}):
            result = namespace[
                "_qqfarm_restore_hidden_miniapp_taskbar_card"
            ]("blank-surface")

        self.assertTrue(result)
        self.assertIn(("show-async", 591632, 9), calls)
        self.assertIn(("pos", 591632, 0x0057), calls)


if __name__ == "__main__":
    unittest.main()
