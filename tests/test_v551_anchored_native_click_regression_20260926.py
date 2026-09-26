import ast
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


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
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class AnchoredNativeClickRegressionTests(unittest.TestCase):
    def test_anchor_preserves_the_native_pre_move_coordinate_space_without_rescaling(self):
        namespace = load_functions("_qqfarm_anchor_miniapp_top_left")
        moves = []
        fake_win32gui = types.SimpleNamespace(
            GetWindowRect=lambda hwnd: (629, 116, 1271, 1316),
            SetWindowPos=lambda hwnd, after, x, y, cx, cy, flags: moves.append(
                (int(hwnd), int(x), int(y), int(cx), int(cy), int(flags))
            ),
        )
        fake_win32api = types.SimpleNamespace(
            MonitorFromWindow=lambda hwnd, flags: 77,
            GetMonitorInfo=lambda monitor: {"Work": (0, 0, 1920, 1080)},
        )

        class FakeUser32:
            GetDpiForWindow = staticmethod(lambda hwnd: 144)

        fake_ctypes = types.SimpleNamespace(
            windll=types.SimpleNamespace(user32=FakeUser32())
        )
        with mock.patch.dict(
            sys.modules,
            {
                "win32gui": fake_win32gui,
                "win32api": fake_win32api,
                "ctypes": fake_ctypes,
            },
        ):
            self.assertTrue(namespace["_qqfarm_anchor_miniapp_top_left"](99))

        self.assertEqual([(99, 0, 0, 642, 1200, 0x0054)], moves)
        route = namespace["_QQFARM_STALE_NATIVE_SURFACE_ROUTE"]
        self.assertEqual((629, 116, 1271, 1316), route["root_rect"])

    def test_live_resolver_retries_the_preserved_pre_anchor_route(self):
        namespace = load_functions("_qqfarm_resolve_live_surface_click")
        current_route = {
            "root_hwnd": 200,
            "target_hwnd": 300,
            "root_rect": (0, 0, 428, 800),
        }
        pre_anchor_route = {
            "root_hwnd": 100,
            "target_hwnd": 101,
            "root_rect": (629, 116, 1271, 1316),
            "coordinate_space": "pre-anchor-logical",
        }
        expected = {
            "root_hwnd": 200,
            "target_hwnd": 300,
            "root_rect": (0, 0, 428, 800),
            "target_rect": (0, 40, 428, 800),
            "client_point": (160, 625),
            "coordinate_space": "stale-screen-remapped",
        }
        calls = []
        namespace.update(
            {
                "_QQFARM_LAST_NATIVE_SURFACE_ROUTE": current_route,
                "_QQFARM_STALE_NATIVE_SURFACE_ROUTE": pre_anchor_route,
                "_qqfarm_collect_live_surface_candidates": (
                    lambda *_args, **_kwargs: [{"hwnd": 200}]
                ),
                "_qqfarm_invalidate_stale_surface_cache": (
                    lambda _candidates: False
                ),
                "_qqfarm_choose_live_surface": (
                    lambda _candidates, _x, _y, **kwargs: calls.append(
                        kwargs.get("previous_route")
                    )
                    or (
                        dict(expected)
                        if kwargs.get("previous_route") is pre_anchor_route
                        else None
                    )
                ),
                "_qqfarm_rect_tuple": lambda value: value,
            }
        )
        fake_win32gui = types.SimpleNamespace(WindowFromPoint=lambda point: 0)

        route = namespace["_qqfarm_resolve_live_surface_click"](
            "click",
            870,
            1166,
            frame_width=428,
            frame_height=800,
            win32gui_module=fake_win32gui,
        )

        self.assertEqual(expected, route)
        self.assertEqual([current_route, pre_anchor_route], calls)

    def test_today_stale_native_click_maps_into_the_top_left_surface(self):
        namespace = load_functions(
            "_qqfarm_rect_tuple",
            "_qqfarm_rect_contains",
            "_qqfarm_remap_stale_screen_point",
            "_qqfarm_choose_live_surface",
        )
        candidates = [
            {
                "hwnd": 200,
                "root_hwnd": 200,
                "is_root": True,
                "class_rank": 3,
                "rect": (0, 0, 428, 800),
                "width": 428,
                "height": 800,
            },
            {
                "hwnd": 300,
                "root_hwnd": 200,
                "is_root": False,
                "class_rank": 0,
                "rect": (0, 40, 428, 800),
                "width": 428,
                "height": 760,
            },
        ]
        route = namespace["_qqfarm_choose_live_surface"](
            candidates,
            870,
            1166,
            frame_width=428,
            frame_height=800,
            previous_route={
                "root_hwnd": 100,
                "target_hwnd": 101,
                "root_rect": (629, 116, 1271, 1316),
                "coordinate_space": "pre-anchor-logical",
            },
        )
        self.assertIsNotNone(route)
        self.assertEqual(200, route["root_hwnd"])
        self.assertEqual(300, route["target_hwnd"])
        self.assertEqual("stale-screen-remapped", route["coordinate_space"])
        x, y = route["client_point"]
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, 428)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, 760)


if __name__ == "__main__":
    unittest.main()
