import ast
import os
import types
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HOOK = Path(os.environ.get("QQFARM_HOOK_UNDER_TEST", ROOT / "portable" / "hook.py"))
FIXTURE = ROOT / "tests" / "fixtures" / "live-v463-quad-confirm-enabled-20260811.png"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V463QuadOverlayResolutionTests(unittest.TestCase):
    def test_real_confirm_layer_is_clicked_and_closed_before_fallback(self):
        namespace = load_functions(
            "_qqfarm_quad_overlay_observation",
            "_qqfarm_resolve_quad_overlay_before_fallback",
        )
        observe = namespace["_qqfarm_quad_overlay_observation"]
        resolve = namespace["_qqfarm_resolve_quad_overlay_before_fallback"]
        initial = cv2.imread(str(FIXTURE))
        self.assertIsNotNone(initial)
        closed = np.zeros_like(initial)
        clicks = []
        frames = iter((closed,))
        bot = types.SimpleNamespace()
        namespace["_get_frame_from_bot"] = lambda _bot: next(frames, closed)
        namespace["_friend_guard_post_client_click"] = (
            lambda x, y, width, height: clicks.append((x, y, width, height)) or True
        )
        namespace["_qqfarm_quad_overlay_observation"] = observe
        namespace["_write"] = lambda *_args, **_kwargs: None
        namespace["time"] = types.SimpleNamespace(
            sleep=lambda _seconds: None,
            time=lambda: 1000.0,
        )
        result = resolve(bot, initial_frame=initial, name="v463-real-fixture")
        self.assertTrue(result)
        self.assertEqual(1, len(clicks), clicks)
        x, y, width, height = clicks[0]
        self.assertLess(abs(x - 448), 18, clicks)
        self.assertLess(abs(y - 497), 18, clicks)
        self.assertEqual((672, 1193), (width, height))
        self.assertFalse(hasattr(bot, "_qqfarm_quad_overlay_block_fallback"))


if __name__ == "__main__":
    unittest.main()
