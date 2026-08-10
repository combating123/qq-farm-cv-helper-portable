import ast
import time
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


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
        "time": time,
        "_DAILY_FLOW_STATUS_PATCH_LOG_SEEN": set(),
        "_DAILY_TASK_SOFT_RETRY_PATCH_LOG_SEEN": set(),
        "_SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN": set(),
        "_SHARE_RETRY_PATCH_LOG_SEEN": set(),
        "_write": lambda *args, **kwargs: None,
        "_throttled_write": lambda *args, **kwargs: None,
        "_daily_entry_call_kind": lambda args, kwargs: "",
        "_share_click_result_succeeded": bool,
        "_daily_flow_entry_red_dot_state": lambda context, flow: None,
        "_daily_flow_retry_blocked": lambda flow: False,
        "_daily_flow_success_today": lambda flow, target="": False,
        "_daily_flow_mark_status": lambda *args, **kwargs: True,
        "_active_bot_sections": lambda: ("bot",),
        "_cfg_get": lambda *args, **kwargs: "",
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class DailyFlowWrapperIdempotenceTests(unittest.TestCase):
    def test_share_and_daily_flow_patches_do_not_stack_on_each_scan(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_wrap_share_entry_settle_func",
            "_looks_share_entry_module",
            "_patch_share_entry_settle_for_module",
            "_daily_flow_key",
            "_daily_flow_context_from_args",
            "_daily_flow_target",
            "_daily_flow_apply_success_context",
            "_daily_flow_context_success_today",
            "_patch_daily_flow_status_for_module",
        )
        events = []
        module = types.ModuleType("bot.synthetic.freebenefits_flow")
        module.run_daily_freebenefits = (
            lambda bot: events.append("run-freebenefits") or True
        )
        module.should_run_daily_freebenefits = lambda bot: True
        module._mark_daily_flow_success = lambda bot, flow: True
        module._mark_daily_flow_failure = lambda bot, flow: False

        self.assertGreater(
            ns["_patch_share_entry_settle_for_module"](module, "first"), 0
        )
        self.assertGreater(
            ns["_patch_daily_flow_status_for_module"](module, "first"), 0
        )

        self.assertEqual(
            0,
            ns["_patch_share_entry_settle_for_module"](module, "second"),
        )
        self.assertEqual(
            0,
            ns["_patch_daily_flow_status_for_module"](module, "second"),
        )
        self.assertTrue(
            getattr(
                module.run_daily_freebenefits,
                "__qqfarm_share_entry_settle_wrapped__",
                False,
            )
        )
        self.assertTrue(
            getattr(
                module.run_daily_freebenefits,
                "__qqfarm_daily_flow_status_wrapped__",
                False,
            )
        )

        bot = types.SimpleNamespace(
            freebenefits_last_date="",
            daily_flow_retry_counts={"freebenefits": 0},
        )
        self.assertTrue(module.run_daily_freebenefits(bot))
        self.assertEqual(["run-freebenefits"], events)

    def test_freebenefits_retry_cap_hard_stops_should_and_run_even_when_badge_is_clear(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_daily_flow_key",
            "_daily_flow_context_from_args",
            "_daily_flow_target",
            "_daily_flow_apply_success_context",
            "_daily_flow_context_success_today",
            "_patch_daily_flow_status_for_module",
        )
        events = []
        ns["_daily_flow_retry_blocked"] = lambda flow: flow == "freebenefits"
        ns["_daily_flow_entry_red_dot_state"] = (
            lambda context, flow: False if flow == "freebenefits" else None
        )
        module = types.ModuleType("bot.synthetic.freebenefits_flow")
        module.should_run_daily_freebenefits = (
            lambda bot: events.append("should-native") or True
        )
        module.run_daily_freebenefits = (
            lambda bot: events.append("run-native") or False
        )
        bot = types.SimpleNamespace(
            freebenefits_last_date="",
            daily_flow_retry_counts={"freebenefits": 25},
        )

        self.assertGreater(
            ns["_patch_daily_flow_status_for_module"](module, "unit"), 0
        )
        self.assertFalse(module.should_run_daily_freebenefits(bot))
        self.assertTrue(module.run_daily_freebenefits(bot))
        self.assertEqual([], events)

    def test_daily_run_recursion_error_records_backoff_before_reraising(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_daily_flow_key",
            "_daily_flow_context_from_args",
            "_daily_flow_target",
            "_daily_flow_apply_success_context",
            "_daily_flow_context_success_today",
            "_patch_daily_flow_status_for_module",
        )
        failures = []
        blocked = {"value": False}
        ns["_daily_flow_mark_failure"] = (
            lambda flow, reason="": failures.append((flow, reason))
            or blocked.__setitem__("value", True)
            or True
        )
        ns["_daily_flow_retry_blocked"] = lambda flow: blocked["value"]
        module = types.ModuleType("bot.synthetic.freebenefits_flow")
        should_events = []
        module.should_run_daily_freebenefits = (
            lambda bot: should_events.append("should") or True
        )

        def run_freebenefits(bot):
            raise RecursionError("maximum recursion depth exceeded")

        module.run_daily_freebenefits = run_freebenefits
        ns["_patch_daily_flow_status_for_module"](module, "unit")
        bot = types.SimpleNamespace(
            freebenefits_last_date="",
            daily_flow_retry_counts={"freebenefits": 0},
        )

        with self.assertRaises(RecursionError):
            module.run_daily_freebenefits(bot)
        self.assertEqual(1, len(failures))
        self.assertEqual("freebenefits", failures[0][0])
        self.assertIn("recursion", failures[0][1])
        self.assertFalse(module.should_run_daily_freebenefits(bot))
        self.assertEqual([], should_events)

    def test_share_retry_wrapper_preserves_existing_share_entry_marker(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_wrap_share_entry_settle_func",
            "_patch_share_retry_backoff_for_module",
        )
        module = types.ModuleType("bot.synthetic.freebenefits_flow")
        module.run_daily_share, _ = ns["_wrap_share_entry_settle_func"](
            lambda bot: True
        )

        self.assertGreater(
            ns["_patch_share_retry_backoff_for_module"](module, "unit"), 0
        )
        self.assertTrue(
            getattr(
                module.run_daily_share,
                "__qqfarm_share_entry_settle_wrapped__",
                False,
            )
        )
        self.assertTrue(
            getattr(
                module.run_daily_share,
                "__qqfarm_share_retry_backoff_wrapped__",
                False,
            )
        )

    def test_task_retry_wrapper_preserves_existing_share_entry_marker(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_wrap_share_entry_settle_func",
            "_patch_daily_task_soft_retry_for_module",
        )
        module = types.ModuleType("bot.synthetic.freebenefits_flow")
        module.run_daily_task, _ = ns["_wrap_share_entry_settle_func"](
            lambda bot: True
        )

        self.assertGreater(
            ns["_patch_daily_task_soft_retry_for_module"](module, "unit"), 0
        )
        self.assertTrue(
            getattr(
                module.run_daily_task,
                "__qqfarm_share_entry_settle_wrapped__",
                False,
            )
        )
        self.assertTrue(
            getattr(
                module.run_daily_task,
                "__qqfarm_task_soft_retry_wrapped__",
                False,
            )
        )

    def test_wechat_wrapper_preserves_existing_share_patch_marker(self):
        ns = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_wrap_share_entry_settle_func",
            "_wrap_is_qq_launch_protocol",
        )
        original = lambda: True
        share_wrapped, changed = ns["_wrap_share_entry_settle_func"](original)
        self.assertTrue(changed)

        wechat_wrapped = ns["_wrap_is_qq_launch_protocol"](
            share_wrapped, "synthetic.is_qq_launch_protocol"
        )
        self.assertTrue(
            getattr(
                wechat_wrapped,
                "__qqfarm_share_entry_settle_wrapped__",
                False,
            )
        )
        self.assertTrue(
            getattr(
                wechat_wrapped,
                "__qqfarm_wechat_focus_wrapped__",
                False,
            )
        )


if __name__ == "__main__":
    unittest.main()
