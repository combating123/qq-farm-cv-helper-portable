import ast
import types
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
DAY = "2026-08-10"


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
    namespace = {
        "__name__": "v450_native_daily_entry_coordinate_fallback",
        "time": types.SimpleNamespace(
            sleep=lambda seconds: None,
            strftime=lambda fmt: DAY,
        ),
        "_daily_business_date": lambda: DAY,
        "_stop_requested_in_args": lambda args, kwargs: False,
        "_share_action_blocked": lambda context, phase, cfg=None: False,
        "_share_context_from_call": lambda args, kwargs: args[0] if args else None,
        "_daily_flow_context_from_args": lambda args, kwargs: args[0] if args else None,
        "_share_prompt_frame_from_call": lambda args, kwargs: None,
        "_throttled_write": lambda *args, **kwargs: None,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def freebenefits_frame(claimable=True):
    frame = np.zeros((800, 428, 3), dtype=np.uint8)
    frame[255:505, 35:205] = (125, 182, 218)
    frame[458:495, 45:198] = (
        (95, 170, 220) if claimable else (90, 95, 105)
    )
    return frame


class NativeDailyEntryCoordinateFallback20260810Tests(unittest.TestCase):
    def _fallback_click(self, tag, expected):
        names = [
            "_daily_entry_call_kind",
            "_share_click_result_succeeded",
            "_wrap_share_entry_settle_func",
        ]
        if tag == "freebenefits":
            names.extend([
                "_freebenefits_claim_button_center_from_rgb",
                "_freebenefits_claim_transition_verified",
            ])
        namespace = load_functions(*names)
        clicks = []
        context = types.SimpleNamespace()
        if tag == "freebenefits":
            frames = iter((freebenefits_frame(True), freebenefits_frame(False)))
            namespace["_get_frame_from_bot"] = lambda bot: next(frames)
        namespace["_friend_guard_post_client_click"] = (
            lambda x, y, width=428, height=800: clicks.append(
                (x, y, width, height)
            ) or True
        )
        wrapped, changed = namespace["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: False
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(context, tag=tag))
        self.assertEqual([expected], clicks)
        if tag == "freebenefits":
            self.assertEqual(
                DAY, context._qqfarm_freebenefits_claim_verified_day
            )

    def test_share_entry_miss_uses_current_home_fixed_client_point(self):
        self._fallback_click("share_entry", (40, 190, 428, 800))

    def test_marketplace_miss_uses_current_home_fixed_client_point(self):
        self._fallback_click("marketplace", (397, 156, 428, 800))

    def test_freebenefits_miss_uses_current_marketplace_fixed_client_point(self):
        self._fallback_click("freebenefits", (121, 477, 428, 800))

    def test_exit_marketplace_miss_uses_current_marketplace_back_point(self):
        self._fallback_click("exit_marketplace", (51, 127, 428, 800))


if __name__ == "__main__":
    unittest.main()
