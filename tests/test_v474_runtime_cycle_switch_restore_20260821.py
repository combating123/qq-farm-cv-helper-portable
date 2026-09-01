import ast
import threading
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_function(name):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace[name]


class RuntimeCycleSwitchRestoreTests(unittest.TestCase):
    def test_restore_includes_primary_self_farm_switches(self):
        restore = load_function("_restore_runtime_business_switches")
        namespace = restore.__globals__
        namespace.update({
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_active_self_sections": lambda: ["instance.1.self", "self"],
            "_active_friend_sections": lambda: ["instance.1.friend", "friend"],
            "_active_planting_sections": lambda: ["instance.1.planting", "planting"],
            "_configured_bool": lambda sections, key, default=False: (
                list(sections) == ["instance.1.self", "self"]
                and key in {"enable_harvest", "enable_farming", "enable_planting"}
            ),
            "_fast_planting_switch_value": lambda _key, desired: bool(desired),
        })
        bot = types.SimpleNamespace(
            enable_harvest=False,
            enable_farming=False,
            enable_planting=False,
        )

        changed = restore(bot)

        self.assertEqual(3, changed)
        self.assertTrue(bot.enable_harvest)
        self.assertTrue(bot.enable_farming)
        self.assertTrue(bot.enable_planting)

    def test_native_cycle_restores_switches_before_dispatch(self):
        wrap = load_function("_wrap_native_v225_daily_catchup_run_cycle")
        events = []
        wrap.__globals__.update({
            "_restore_runtime_business_switches": lambda context: events.append(
                ("restore", context)
            ) or 3,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_native_v225_daily_home_ready": lambda _context: False,
            "_native_v225_daily_any_due": lambda _context: False,
            "_qqfarm_native_friend_idle_home_recovery": lambda _context: False,
        })
        context = object()

        wrapped, installed = wrap(
            lambda owner: events.append(("cycle", owner)) or "done",
            "FarmBotCV.run_cycle",
        )
        result = wrapped(context)

        self.assertTrue(installed)
        self.assertEqual("done", result)
        self.assertEqual([("restore", context), ("cycle", context)], events)

    def test_rescue_run_cycle_bypasses_daily_catchup(self):
        wrap = load_function("_wrap_native_v225_daily_catchup_run_cycle")
        events = []
        wrap.__globals__.update({
            "_restore_runtime_business_switches": lambda _context: 0,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_native_v225_daily_home_ready": lambda _context: True,
            "_run_native_v225_daily_catchup": lambda _context: events.append(
                "daily"
            ) or "freebenefits",
            "_qqfarm_native_friend_idle_home_recovery": lambda _context: False,
        })
        context = types.SimpleNamespace(
            _qqfarm_empty_patrol_rescue_bypass_daily=True,
        )
        wrapped, installed = wrap(
            lambda _owner: events.append("cycle") or "done",
            "FarmBotCV.run_cycle",
        )

        result = wrapped(context)

        self.assertTrue(installed)
        self.assertEqual("done", result)
        self.assertEqual(["cycle"], events)

    def test_runtime_switch_keeper_tick_repairs_post_start_reset(self):
        tick = load_function("_runtime_business_switch_keeper_tick")
        events = []
        context = types.SimpleNamespace(enable_process_self=False)
        tick.__globals__["_restore_runtime_business_switches"] = (
            lambda owner: events.append(owner) or setattr(
                owner, "enable_process_self", True
            ) or 1
        )

        changed = tick(context)

        self.assertEqual(1, changed)
        self.assertTrue(context.enable_process_self)
        self.assertEqual([context], events)

    def test_farmbot_start_installs_runtime_switch_keeper(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(HOOK))
        wrapper = next(
            item for item in tree.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "_wrap_runtime_diag_method"
        )
        rendered = ast.unparse(wrapper)

        self.assertIn("if str(label) == 'FarmBotCV.start':", rendered)
        self.assertIn("_ensure_runtime_business_switch_keeper", rendered)

    def test_runtime_switch_snapshot_reports_primary_routes(self):
        snapshot = load_function("_runtime_business_switch_snapshot")
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            enable_harvest=True,
            running=True,
        )

        rendered = snapshot(context)

        self.assertIn("'enable_process_self': True", rendered)
        self.assertIn("'enable_process_friend': True", rendered)
        self.assertIn("'enable_harvest': True", rendered)
        self.assertIn("'running': True", rendered)

    def test_runtime_log_patch_probes_patrol_stack(self):
        install = load_function("_install_runtime_log_patch")
        rendered = ast.unparse(ast.parse(
            HOOK.read_text(encoding="utf-8-sig"), filename=str(HOOK)
        ))

        self.assertTrue(callable(install))
        self.assertIn("v474 patrol log stack=", rendered)
        self.assertIn("_cycle_stack_probe(msg)", rendered)

    def test_repeated_empty_patrol_dispatches_dormant_run_cycle(self):
        transition = load_function("_runtime_patrol_rescue_transition")
        events = []
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: events.append("cycle") or "done",
        )
        transition.__globals__.update({
            "_write": lambda message: events.append(message),
        })

        result = transition(
            context,
            "================ 开始新一轮巡检 ================",
            scheduler=lambda worker: worker(),
        )

        self.assertEqual("rescue", result)
        self.assertIn("cycle", events)
        self.assertFalse(context._qqfarm_patrol_rescue_running)

    def test_repeated_empty_patrol_queues_without_background_owner(self):
        transition = load_function("_runtime_patrol_rescue_transition")
        events = []
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: events.append("cycle") or "done",
        )
        transition.__globals__.update({
            "_write": lambda message: events.append(("log", message)),
        })

        result = transition(
            context,
            "================ 寮€濮嬫柊涓€杞贰妫€ ================",
        )

        self.assertEqual("queued", result)
        self.assertNotIn("cycle", events)
        self.assertTrue(context._qqfarm_patrol_rescue_pending)
        self.assertFalse(context._qqfarm_patrol_rescue_running)

    def test_real_branch_resets_empty_patrol_streak(self):
        transition = load_function("_runtime_patrol_rescue_transition")
        context = types.SimpleNamespace(_qqfarm_patrol_empty_streak=4)

        result = transition(
            context,
            "正在检查自家农场是否有可执行的任务",
        )

        self.assertEqual("branch", result)
        self.assertEqual(0, context._qqfarm_patrol_empty_streak)
        self.assertTrue(context._qqfarm_patrol_cycle_branch_seen)

    def test_native_freebenefits_counter_hard_blocks_at_three(self):
        cap = load_function("_runtime_freebenefits_retry_cap_reached")
        marks = []
        context = types.SimpleNamespace(
            daily_flow_retry_date="2026-08-21",
            daily_flow_retry_counts={"freebenefits": 7},
        )
        attempts = {"value": 1}
        cap.__globals__.update({
            "_daily_business_date": lambda: "2026-08-21",
            "_daily_retry_max_default": lambda: 3,
            "_daily_flow_retry_blocked": lambda _flow, **_kwargs: (
                attempts["value"] >= 3
            ),
            "_daily_flow_mark_failure": lambda *_args, **_kwargs: (
                marks.append("failure"),
                attempts.__setitem__("value", attempts["value"] + 1),
            )[-1],
        })

        blocked = cap(context)

        self.assertTrue(blocked)
        self.assertEqual(3, attempts["value"])
        self.assertEqual(["failure", "failure"], marks)
        self.assertEqual(
            "2026-08-21", context._qqfarm_freebenefits_hard_block_day
        )

    def test_blocked_share_reward_recovery_does_not_swallow_farm_cycle(self):
        catchup = load_function("_run_native_v225_daily_catchup")
        namespace = catchup.__globals__
        namespace.update({
            "_native_v225_daily_home_ready": lambda _context: True,
            "_daily_flow_success_today": lambda flow, **_kwargs: flow == "share",
            "_daily_flow_attempted_today": lambda *_args, **_kwargs: True,
            "_daily_flow_entry_red_dot_state": lambda *_args, **_kwargs: False,
            "_daily_business_date": lambda: "2026-08-21",
            "_native_v225_daily_flow_module": lambda: types.SimpleNamespace(),
            "_native_v225_daily_flow_due": lambda *_args, **_kwargs: False,
            "_daily_flow_target": lambda _flow: "TARGET",
            "_run_share_prompt_recovery": lambda _context: False,
        })
        context = types.SimpleNamespace()

        result = catchup(context)

        self.assertEqual("", result)

    def test_blocked_due_share_recovery_does_not_claim_the_cycle(self):
        catchup = load_function("_run_native_v225_daily_catchup")
        namespace = catchup.__globals__
        namespace.update({
            "_native_v225_daily_home_ready": lambda _context: True,
            "_daily_flow_success_today": lambda *_args, **_kwargs: False,
            "_daily_flow_attempted_today": lambda *_args, **_kwargs: False,
            "_daily_flow_entry_red_dot_state": lambda *_args, **_kwargs: False,
            "_daily_business_date": lambda: "2026-09-01",
            "_native_v225_daily_flow_module": lambda: types.SimpleNamespace(),
            "_native_v225_daily_flow_due": lambda _context, flow: flow == "share",
            "_daily_flow_target": lambda _flow: "TARGET",
            # The share scheduler is due, but its hard completion gate blocks
            # the action.  That must leave the farm cycle available.
            "_run_share_prompt_recovery": lambda _context: False,
        })
        context = types.SimpleNamespace()

        result = catchup(context)

        self.assertEqual("", result)


if __name__ == "__main__":
    unittest.main()
