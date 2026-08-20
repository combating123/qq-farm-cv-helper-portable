import ast
import time
import types
import unittest
from pathlib import Path

import numpy as np

from tests.test_vip_business_context import load_vip_business_wrapper


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_nodes(functions=(), assignments=(), namespace=None):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted_functions = set(functions)
    wanted_assignments = set(assignments)
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted_functions:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in wanted_assignments
            for target in node.targets
        ):
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    result = dict(namespace or {})
    exec(compile(module, str(HOOK), "exec"), result)
    return result


class FeatureAlignmentTests(unittest.TestCase):
    def test_public_auto_sell_alias_honors_success_cooldown(self):
        ns = load_vip_business_wrapper()
        calls = []
        ns["_warehouse_recently_done"] = lambda: True
        ns["_warehouse_cooldown_seconds"] = lambda: 21600.0

        def native(_bot):
            calls.append("native")
            return True

        wrapped, changed = ns["_wrap_vip_business_func"](
            native, "bot.fixture.handle_home_auto_sell_fruit"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(types.SimpleNamespace()))
        self.assertEqual([], calls)

    def test_public_warehouse_sequence_alias_updates_parent_result(self):
        ns = load_vip_business_wrapper()
        ns["time"] = types.SimpleNamespace(time=lambda: 1000.0)
        ns["_warehouse_classify_result"] = (
            lambda result: "empty" if result == "warehouse_empty" else "failed"
        )

        wrapped, changed = ns["_wrap_vip_business_func"](
            lambda _bot: "warehouse_empty",
            "bot.fixture.run_warehouse_sell_button_sequence",
        )

        self.assertTrue(changed)
        self.assertEqual("warehouse_empty", wrapped(types.SimpleNamespace()))
        self.assertEqual("empty", ns["_VIP_WAREHOUSE_LAST_SEQUENCE_CLASS"])
        self.assertEqual(1000.0, ns["_VIP_WAREHOUSE_LAST_SEQUENCE_TS"])

    def test_auto_sell_interval_preserves_configured_value(self):
        ns = load_nodes(functions=("_coerce_business_value",))
        ns["_norm_key"] = lambda value: str(value).lower()
        ns["_VIP_BUSINESS_BOOL_TRUE"] = set()
        ns["_VIP_BUSINESS_VALUE_OVERRIDES"] = set()
        ns["_VIP_BUSINESS_RESET_NUMERIC"] = set()
        ns["_VIP_BUSINESS_ZERO_COUNTERS"] = set()

        self.assertEqual(
            6.0,
            ns["_coerce_business_value"]("auto_sell_fruit_interval_hours", 6.0),
        )
        self.assertEqual(
            "6.00",
            ns["_coerce_business_value"]("auto_sell_fruit_interval_hours", "6.00"),
        )

    def test_guard_threshold_setting_controls_runtime_approval(self):
        ns = load_nodes(functions=("_guard_dog_match_threshold",))
        ns.update({
            "_active_friend_sections": lambda: ("instance.1.friend", "friend"),
            "_cfg_get": lambda sections, key, default: {
                "guard_dog_frame_threshold": "0.90",
            }.get(key, default),
        })

        self.assertEqual(0.90, ns["_guard_dog_match_threshold"]("avatar_frame"))
        self.assertEqual(0.90, ns["_guard_dog_match_threshold"]("friend_guard_list"))

    def test_blank_hidden_wgc_restores_taskbar_card_when_compat_enabled(self):
        ns = load_nodes(functions=("_qqfarm_capture_wgc_farm_frame",))
        events = []
        blank = np.full((800, 428, 3), 255, dtype=np.uint8)

        def stop_capture(reason=""):
            events.append(("stop", reason))
            ns["_QQFARM_WGC_CAPTURE"] = None
            ns["_QQFARM_WGC_CONTROL"] = None
            return True

        ns.update({
            "np": np,
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": object(),
            "_QQFARM_WGC_FRAME": blank,
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_BLANK_COUNT": 0,
            "_configured_bool": (
                lambda _sections, key, default=False:
                True if key == "hide_miniapp_compat_mode" else default
            ),
            "_active_bot_sections": lambda: ("instance.1.bot", "bot"),
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_qqfarm_restore_hidden_miniapp_taskbar_card": (
                lambda reason="": events.append(("restore-taskbar", reason)) or True
            ),
            "_qqfarm_start_wgc_capture": lambda: True,
            "_qqfarm_wgc_frame_is_rendered_game_surface": lambda _frame: False,
            "_qqfarm_stop_wgc_capture": stop_capture,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        self.assertIsNone(ns["_qqfarm_capture_wgc_farm_frame"]())
        self.assertIsNone(ns["_qqfarm_capture_wgc_farm_frame"]())
        self.assertIn(("restore-taskbar", "blank-surface"), events)


if __name__ == "__main__":
    unittest.main()
