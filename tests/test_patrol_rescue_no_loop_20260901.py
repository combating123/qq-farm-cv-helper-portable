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
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class PatrolRescueNoLoopTests(unittest.TestCase):
    def test_same_context_repeated_start_logs_only_one_queue(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        events = []
        namespace.update({"_write": lambda message: events.append(message)})
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: "done",
        )

        transition = namespace["_runtime_patrol_rescue_transition"]
        self.assertEqual(
            "queued",
            transition(context, "================ 开始新一轮巡检 ================"),
        )
        # Native logging can emit another start before the pending bit is
        # consumed.  That observation must not create another queue event.
        self.assertEqual(
            "queued",
            transition(context, "================ 开始新一轮巡检 ================"),
        )
        self.assertEqual(
            1,
            sum("rescue queued" in str(item) for item in events),
        )

    def test_real_branch_releases_global_and_context_hold(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_QQFARM_PATROL_RESCUE_GLOBAL_STATE": {
                "pending": False,
                "consumed": True,
                "held": True,
                "episode": 4,
                "last_consumed_ts": time.monotonic(),
                "capture_generation": 8,
            },
        })
        context = types.SimpleNamespace(
            _qqfarm_patrol_rescue_hold=True,
            _qqfarm_patrol_rescue_pending=True,
            _qqfarm_patrol_rescue_cooldown_until=time.monotonic() + 30.0,
        )

        result = namespace["_runtime_patrol_rescue_transition"](
            context, "正在检查好友农场是否有可执行的任务"
        )

        self.assertEqual("branch", result)
        state = namespace["_QQFARM_PATROL_RESCUE_GLOBAL_STATE"]
        self.assertFalse(state["pending"])
        self.assertFalse(state["consumed"])
        self.assertFalse(state["held"])
        self.assertFalse(context._qqfarm_patrol_rescue_hold)
        self.assertFalse(context._qqfarm_patrol_rescue_pending)
        self.assertEqual(0.0, context._qqfarm_patrol_rescue_cooldown_until)

    def test_wgc_generation_change_allows_one_new_queue_only(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        events = []
        namespace.update({
            "_write": lambda message: events.append(message),
            "_QQFARM_WGC_GENERATION": 9,
            "_QQFARM_PATROL_RESCUE_GLOBAL_STATE": {
                "pending": False,
                "consumed": True,
                "held": True,
                "episode": 5,
                "last_consumed_ts": time.monotonic(),
                "capture_generation": 8,
            },
        })
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            _qqfarm_patrol_rescue_hold=True,
            run_cycle=lambda: "done",
        )
        transition = namespace["_runtime_patrol_rescue_transition"]

        self.assertEqual(
            "queued",
            transition(context, "================ 开始新一轮巡检 ================"),
        )
        self.assertEqual(
            "queued",
            transition(context, "================ 开始新一轮巡检 ================"),
        )
        self.assertEqual(
            1,
            sum("rescue queued" in str(item) for item in events),
        )

    def test_consumed_rescue_does_not_requeue_when_logger_and_native_use_different_context_objects(self):
        namespace = load_functions(
            "_runtime_patrol_rescue_transition",
            "_wrap_native_v225_daily_catchup_run_cycle",
        )
        events = []
        namespace.update({
            "_write": lambda message: events.append(message),
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_restore_runtime_business_switches": lambda _context: 0,
            "_native_v225_daily_home_ready": lambda _context: False,
            "_native_v225_daily_any_due": lambda _context: False,
            "_qqfarm_native_friend_idle_home_recovery": lambda _context: False,
        })

        logger_context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: "done",
        )
        native_context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: "done",
        )

        transition = namespace["_runtime_patrol_rescue_transition"]
        self.assertEqual(
            "queued",
            transition(
                logger_context,
                "================ 开始新一轮巡检 ================",
            ),
        )

        wrapped, installed = namespace[
            "_wrap_native_v225_daily_catchup_run_cycle"
        ](
            lambda _owner: "done",
            "FarmBotCV.run_cycle",
        )
        self.assertTrue(installed)
        self.assertEqual("done", wrapped(logger_context))

        # This is the production failure shape: the next logger callback can
        # resolve a fresh/native context object even though it belongs to the
        # same running patrol.  It must not create a second rescue episode.
        result = transition(
            native_context,
            "================ 开始新一轮巡检 ================",
        )

        self.assertIn(result, ("start", "held"))
        self.assertFalse(
            getattr(native_context, "_qqfarm_patrol_rescue_pending", False)
        )
        self.assertEqual(
            1,
            sum("rescue queued" in str(item) for item in events),
        )


if __name__ == "__main__":
    unittest.main()
