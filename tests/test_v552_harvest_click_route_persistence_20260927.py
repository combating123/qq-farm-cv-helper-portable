import ast
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*wanted):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted_set = set(wanted)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted_set
    ]
    missing = wanted_set.difference(node.name for node in nodes)
    if missing:
        raise AssertionError(f"hook.py is missing: {sorted(missing)}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class HarvestClickRoutePersistenceTests(unittest.TestCase):
    def test_preserves_pre_anchor_route_after_current_route_is_invalidated(self):
        namespace = load_functions("_qqfarm_invalidate_stale_surface_cache")
        pre_anchor = {
            "root_hwnd": 100,
            "target_hwnd": 101,
            "root_rect": (629, 116, 1271, 1316),
            "coordinate_space": "pre-anchor-logical",
            "anchor_source": True,
        }
        current = {
            "root_hwnd": 200,
            "target_hwnd": 300,
            "root_rect": (1, 1, 672, 1252),
            "coordinate_space": "screen",
        }
        namespace["_QQFARM_LAST_NATIVE_SURFACE_ROUTE"] = current
        namespace["_QQFARM_STALE_NATIVE_SURFACE_ROUTE"] = pre_anchor

        candidates = [{
            "hwnd": 200,
            "root_hwnd": 200,
            "is_root": True,
            "rect": (0, 0, 671, 1251),
        }]

        self.assertTrue(namespace["_qqfarm_invalidate_stale_surface_cache"](candidates))
        self.assertEqual(
            pre_anchor,
            namespace["_QQFARM_PRE_ANCHOR_NATIVE_SURFACE_ROUTE"],
        )

    def test_old_harvest_coordinate_tries_immutable_pre_anchor_route(self):
        namespace = load_functions("_qqfarm_resolve_live_surface_click")
        current = {
            "root_hwnd": 200,
            "target_hwnd": 300,
            "root_rect": (0, 0, 671, 1251),
            "coordinate_space": "screen",
        }
        overwritten_stale = dict(current)
        pre_anchor = {
            "root_hwnd": 100,
            "target_hwnd": 101,
            "root_rect": (629, 116, 1271, 1316),
            "coordinate_space": "pre-anchor-logical",
            "anchor_source": True,
        }
        expected = {
            "root_hwnd": 200,
            "target_hwnd": 301,
            "root_rect": (0, 0, 671, 1251),
            "target_rect": (0, 40, 671, 1251),
            "client_point": (660, 948),
            "coordinate_space": "stale-screen-remapped",
        }
        calls = []
        namespace.update({
            "_QQFARM_LAST_NATIVE_SURFACE_ROUTE": current,
            "_QQFARM_STALE_NATIVE_SURFACE_ROUTE": overwritten_stale,
            "_QQFARM_PRE_ANCHOR_NATIVE_SURFACE_ROUTE": pre_anchor,
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
                or (dict(expected) if kwargs.get("previous_route") is pre_anchor else None)
            ),
            "_qqfarm_rect_tuple": lambda value: value,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })
        fake_win32gui = types.SimpleNamespace(WindowFromPoint=lambda point: 0)

        route = namespace["_qqfarm_resolve_live_surface_click"](
            "click",
            1260,
            1064,
            frame_width=428,
            frame_height=800,
            win32gui_module=fake_win32gui,
        )

        self.assertEqual(expected, route)
        self.assertEqual([current, pre_anchor], calls)


if __name__ == "__main__":
    unittest.main()
