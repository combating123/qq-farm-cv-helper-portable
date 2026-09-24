import ast
import types
import time
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


def load_functions(*wanted):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(wanted)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError(f"hook.py is missing: {sorted(missing)}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "np": np}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def read_bgr(path):
    encoded = np.fromfile(str(path), dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        raise AssertionError(f"fixture cannot be decoded: {path}")
    return frame


class V539FriendCaptureCacheAndDpiClickTests(unittest.TestCase):
    def test_printwindow_friend_list_capture_remembers_frame_for_native_owner(self):
        namespace = load_functions("_qqfarm_capture_visible_farm_frame")
        capture = namespace["_qqfarm_capture_visible_farm_frame"]
        friend_list = read_bgr(FRIEND_LIST_FIXTURE)
        context = types.SimpleNamespace()
        rows = [{"center": (312, 434 + index * 142)} for index in range(3)]
        remembered = []

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
                    lambda _hwnd, _rect: friend_list
                ),
                "_qqfarm_visible_frame_has_farm_scene": lambda _frame: False,
                "_friend_list_visit_button_rows": (
                    lambda frame: rows if frame is friend_list else []
                ),
                "_ACTIVE_RUN_CYCLE_CONTEXT": context,
                "_qqfarm_remember_friend_list_frame": (
                    lambda owner, frame, detected_rows=None: remembered.append(
                        (owner, frame, list(detected_rows or []))
                    ) or True
                ),
                "_qqfarm_remember_good_capture_frame": lambda _frame: None,
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )

        result = capture(prefer_desktop=True)

        self.assertIs(friend_list, result)
        self.assertEqual(1, len(remembered), remembered)
        self.assertIs(context, remembered[0][0])
        self.assertIs(friend_list, remembered[0][1])
        self.assertEqual(rows, remembered[0][2])

    def test_native_friend_owner_uses_recent_cached_rows_after_blank_owner_frame(self):
        namespace = load_functions("_qqfarm_resolve_friend_list_frame")
        resolver = namespace["_qqfarm_resolve_friend_list_frame"]
        context = types.SimpleNamespace(
            _qqfarm_friend_list_frame_cache=read_bgr(FRIEND_LIST_FIXTURE),
            _qqfarm_friend_list_rows_cache=[
                {"center": (312, 434 + index * 142)} for index in range(3)
            ],
            _qqfarm_friend_list_frame_cache_ts=time.monotonic(),
            _qqfarm_friend_list_surface_seen_ts=time.monotonic(),
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_friend_entry_pending=True,
        )
        owner_blank = np.zeros((800, 428, 3), dtype=np.uint8)
        namespace.update(
            {
                "_friend_list_visit_button_rows": (
                    lambda frame: [] if frame is owner_blank else list(
                        context._qqfarm_friend_list_rows_cache
                    )
                ),
                "_get_frame_from_bot": lambda *_args, **_kwargs: None,
                "_throttled_write": lambda *_args, **_kwargs: None,
                "_QQFARM_FRIEND_LIST_FRAME_CACHE": None,
                "_QQFARM_FRIEND_LIST_ROWS_CACHE": [],
                "_QQFARM_FRIEND_LIST_FRAME_CACHE_TS": 0.0,
            }
        )

        resolved_frame, resolved_rows = resolver(context, owner_blank)

        self.assertIs(context._qqfarm_friend_list_frame_cache, resolved_frame)
        self.assertEqual(
            context._qqfarm_friend_list_rows_cache,
            resolved_rows,
        )

    def test_physical_printwindow_geometry_remaps_old_logical_click(self):
        namespace = load_functions(
            "_qqfarm_rect_tuple",
            "_qqfarm_rect_contains",
            "_qqfarm_remap_stale_screen_point",
            "_qqfarm_invalidate_stale_surface_cache",
            "_qqfarm_choose_live_surface",
            "_qqfarm_rebase_surface_candidates_to_physical",
            "_qqfarm_resolve_live_surface_click",
        )
        logical_root = (944, 174, 1615, 1425)
        physical_root = (629, 116, 1076, 950)
        candidates = [
            {
                "hwnd": 200,
                "root_hwnd": 200,
                "is_root": True,
                "class_name": "Chrome_WidgetWin_1",
                "class_rank": 3,
                "visible": True,
                "rect": logical_root,
                "width": 671,
                "height": 1251,
            },
            {
                "hwnd": 300,
                "root_hwnd": 200,
                "is_root": False,
                "class_name": "Chrome_RenderWidgetHostHWND",
                "class_rank": 0,
                "visible": True,
                "rect": (944, 216, 1615, 1425),
                "width": 671,
                "height": 1209,
            },
        ]
        old_route = {
            "root_hwnd": 200,
            "target_hwnd": 300,
            "root_rect": logical_root,
            "target_rect": (944, 216, 1615, 1425),
            "input_screen_point": (1544, 384),
        }
        fake_win32gui = types.SimpleNamespace(
            WindowFromPoint=lambda _point: 0,
        )
        namespace.update(
            {
                "_qqfarm_collect_live_surface_candidates": (
                    lambda _win32gui, _title: [dict(item) for item in candidates]
                ),
                "_QQFARM_LAST_NATIVE_SURFACE_ROUTE": old_route,
                "_QQFARM_STALE_NATIVE_SURFACE_ROUTE": None,
                "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_FRAME_ID": 1,
                "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_HWND": 200,
                "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_RECT": physical_root,
                "_QQFARM_WGC_BOUND_HWND": 200,
                "_QQFARM_LAST_FARM_HWND": 200,
                "_QQFARM_LAST_GOOD_CAPTURE_HWND": 200,
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )

        route = namespace["_qqfarm_resolve_live_surface_click"](
            "click",
            1544,
            384,
            frame_width=428,
            frame_height=800,
            win32gui_module=fake_win32gui,
        )

        self.assertIsNotNone(route)
        self.assertEqual(physical_root, route["root_rect"])
        self.assertEqual("physical-printwindow-remapped", route["coordinate_space"])
        self.assertTrue(route.get("physical_geometry_evidence"))
        self.assertNotEqual((600, 210), tuple(route["client_point"]))
        self.assertGreaterEqual(route["screen_point"][0], physical_root[0])
        self.assertLess(route["screen_point"][0], physical_root[2])
        self.assertGreaterEqual(route["screen_point"][1], physical_root[1])
        self.assertLess(route["screen_point"][1], physical_root[3])


if __name__ == "__main__":
    unittest.main()
