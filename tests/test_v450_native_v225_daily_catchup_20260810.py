import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    assignments = {"_NATIVE_V225_DAILY_CATCHUP_PATCH_LOG_SEEN"}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in assignments
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    messages = []
    namespace = {
        "__name__": "v450_native_v225_daily_catchup",
        "_write": messages.append,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["_messages"] = messages
    return namespace


class NativeV225DailyCatchup20260810Tests(unittest.TestCase):
    def test_home_cycle_runs_one_due_daily_flow_before_native_farm_work(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        self.assertIn("_wrap_native_v225_daily_catchup_run_cycle", namespace)
        events = []

        def native_cycle(bot):
            events.append("native-cycle")
            return "native-result"

        namespace["_run_native_v225_daily_catchup"] = (
            lambda bot: events.append("freebenefits-catchup") or "freebenefits"
        )
        wrapped, changed = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            native_cycle, "bot.fixture.FarmBotCV.run_cycle"
        )

        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot))
        self.assertEqual(["freebenefits-catchup"], events)

    def test_due_daily_flow_on_friend_scene_requests_home_before_native_work(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        self.assertIn("_wrap_native_v225_daily_catchup_run_cycle", namespace)
        events = []

        def native_cycle(bot):
            events.append("native-cycle")
            return "native-result"

        namespace["_native_v225_daily_any_due"] = lambda bot: True
        namespace["_native_v225_request_home_for_daily"] = (
            lambda bot: events.append("return-home") or True
        )
        namespace["_run_native_v225_daily_catchup"] = lambda bot: ""
        wrapped, changed = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            native_cycle, "bot.fixture.FarmBotCV.run_cycle"
        )

        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="friend")
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot))
        self.assertEqual(["return-home"], events)

    def test_non_home_cycle_keeps_native_work_and_does_not_click_daily_entries(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        self.assertIn("_wrap_native_v225_daily_catchup_run_cycle", namespace)
        events = []

        def native_cycle(bot):
            events.append("native-cycle")
            return "native-result"

        namespace["_run_native_v225_daily_catchup"] = (
            lambda bot: events.append("daily-catchup") or ""
        )
        wrapped, changed = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            native_cycle, "bot.fixture.FarmBotCV.run_cycle"
        )

        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="friend")
        self.assertTrue(changed)
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(["native-cycle"], events)

    def test_home_ready_recovers_stale_friend_hint_from_fresh_self_frame(self):
        namespace = load_functions("_native_v225_daily_home_ready")
        frame = object()
        namespace["_native_v225_daily_any_due"] = lambda bot: True
        namespace["_get_frame_from_bot"] = lambda bot: frame
        namespace["_qqfarm_strict_self_scene_state"] = (
            lambda current: False if current is frame else None
        )

        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="friend")

        self.assertTrue(namespace["_native_v225_daily_home_ready"](bot))
        self.assertEqual("home", bot._qqfarm_live_scene_hint)
        self.assertEqual("home", bot._qqfarm_cycle_branch_hint)

    def test_terminal_freebenefits_failure_requests_home_before_visible_recovery(self):
        namespace = load_functions("_native_v225_daily_candidate_due")
        namespace["_native_v225_daily_schedule_due"] = lambda *args, **kwargs: True
        namespace["_daily_flow_success_today"] = lambda *args, **kwargs: False
        namespace["_daily_flow_retry_blocked"] = lambda flow: True
        namespace["_daily_business_date"] = lambda: "2026-08-10"
        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="friend")

        self.assertTrue(namespace["_native_v225_daily_candidate_due"](
            bot, "freebenefits", require_home=False
        ))

        bot._qqfarm_native_v225_daily_coordinate_override_day_freebenefits = (
            "2026-08-10"
        )
        self.assertFalse(namespace["_native_v225_daily_candidate_due"](
            bot, "freebenefits", require_home=False
        ))

    def test_terminal_share_failure_gets_one_visible_coordinate_recovery_lease(self):
        namespace = load_functions("_native_v225_daily_candidate_due")
        namespace["_native_v225_daily_home_ready"] = lambda bot: True
        namespace["_native_v225_daily_schedule_due"] = lambda *args, **kwargs: True
        namespace["_share_target_guard_config"] = lambda: {
            "enabled": True, "target_name": "1000000001"
        }
        namespace["_daily_flow_target"] = lambda flow: "1000000001"
        namespace["_daily_flow_success_today"] = lambda *args, **kwargs: False
        namespace["_daily_flow_retry_blocked"] = lambda flow: True
        namespace["_daily_flow_entry_red_dot_state"] = lambda bot, flow: True
        namespace["_daily_business_date"] = lambda: "2026-08-10"
        bot = types.SimpleNamespace()

        self.assertTrue(namespace["_native_v225_daily_candidate_due"](
            bot, "share", require_home=True
        ))

        bot._qqfarm_native_v225_daily_coordinate_override_day_share = (
            "2026-08-10"
        )
        self.assertFalse(namespace["_native_v225_daily_candidate_due"](
            bot, "share", require_home=True
        ))

    def test_terminal_freebenefits_failure_gets_one_visible_coordinate_recovery_lease(self):
        namespace = load_functions("_native_v225_daily_candidate_due")
        namespace["_native_v225_daily_home_ready"] = lambda bot: True
        namespace["_native_v225_daily_schedule_due"] = lambda *args, **kwargs: True
        namespace["_daily_flow_success_today"] = lambda *args, **kwargs: False
        namespace["_daily_flow_retry_blocked"] = lambda flow: True
        namespace["_daily_flow_entry_red_dot_state"] = lambda bot, flow: True
        namespace["_daily_business_date"] = lambda: "2026-08-10"
        bot = types.SimpleNamespace()

        self.assertTrue(namespace["_native_v225_daily_candidate_due"](
            bot, "freebenefits", require_home=True
        ))

        bot._qqfarm_native_v225_daily_coordinate_override_day_freebenefits = (
            "2026-08-10"
        )
        self.assertFalse(namespace["_native_v225_daily_candidate_due"](
            bot, "freebenefits", require_home=True
        ))

    def test_home_catchup_does_not_promote_persisted_attempt_without_current_dispatch(self):
        namespace = load_functions(
            "_native_v225_daily_home_ready", "_run_native_v225_daily_catchup"
        )
        events = []
        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        namespace["_daily_flow_success_today"] = lambda *args, **kwargs: False
        namespace["_daily_flow_attempted_today"] = lambda context, flow: True
        namespace["_daily_flow_entry_red_dot_state"] = (
            lambda context, flow: False
        )
        namespace["_daily_flow_mark_status"] = (
            lambda *args, **kwargs: events.append((args, kwargs)) or True
        )
        namespace["_native_v225_daily_flow_module"] = lambda: None
        namespace["_native_v225_daily_flow_due"] = lambda context, flow: False

        self.assertEqual("", namespace["_run_native_v225_daily_catchup"](bot))
        self.assertEqual([], events)

    def test_home_catchup_promotes_attempted_freebenefits_when_red_dot_cleared(self):
        namespace = load_functions(
            "_native_v225_daily_home_ready", "_run_native_v225_daily_catchup"
        )
        events = []
        bot = types.SimpleNamespace(
            _qqfarm_live_scene_hint="home",
            _qqfarm_native_v225_daily_dispatch_day_freebenefits="2026-08-10",
            _qqfarm_freebenefits_claim_verified_day="2026-08-10",
        )
        namespace["_daily_business_date"] = lambda: "2026-08-10"
        namespace["_daily_flow_success_today"] = lambda *args, **kwargs: False
        namespace["_daily_flow_attempted_today"] = lambda context, flow: True
        namespace["_daily_flow_entry_red_dot_state"] = (
            lambda context, flow: False
        )
        namespace["_daily_flow_mark_status"] = (
            lambda flow, status, **kwargs: events.append(
                (flow, status, kwargs.get("reason"))
            ) or True
        )
        namespace["_daily_flow_apply_success_context"] = (
            lambda context, flow, *args: setattr(
                context, "freebenefits_last_date", "2026-08-10"
            ) or True
        )
        namespace["_native_v225_daily_flow_module"] = lambda: None
        namespace["_native_v225_daily_flow_due"] = lambda context, flow: False

        self.assertEqual(
            "freebenefits-confirmed",
            namespace["_run_native_v225_daily_catchup"](bot),
        )
        self.assertEqual(
            [("freebenefits", "success",
              "verified-freebenefits-claim-v2")], events
        )
        self.assertEqual("2026-08-10", bot.freebenefits_last_date)

    def test_native_daily_call_retries_with_required_game_frame(self):
        namespace = load_functions("_native_v225_call_daily")
        frame = object()
        events = []

        class OpaqueDaily:
            __signature__ = __import__("inspect").Signature([
                __import__("inspect").Parameter(
                    "context", __import__("inspect").Parameter.POSITIONAL_OR_KEYWORD
                )
            ])

            def __call__(self, context, game_frame):
                events.append((context, game_frame))
                return "daily-result"

        bot = types.SimpleNamespace()
        namespace["_get_frame_from_bot"] = lambda context: frame

        self.assertEqual(
            "daily-result", namespace["_native_v225_call_daily"](OpaqueDaily(), bot)
        )
        self.assertEqual([(bot, frame)], events)

    def test_daily_catchup_serializes_freebenefits_before_exact_target_share(self):
        namespace = load_functions("_native_v225_daily_home_ready", "_run_native_v225_daily_catchup")
        self.assertIn("_run_native_v225_daily_catchup", namespace)
        events = []
        bot = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        daily_module = types.SimpleNamespace(
            run_daily_freebenefits=lambda context: events.append("freebenefits") or True,
        )
        namespace["_native_v225_daily_flow_module"] = lambda: daily_module
        namespace["_native_v225_daily_flow_due"] = (
            lambda context, flow: flow in ("freebenefits", "share")
        )
        namespace["_native_v225_call_daily"] = (
            lambda fn, context: fn(context)
        )
        namespace["_run_share_prompt_recovery"] = (
            lambda context: events.append("share") or True
        )

        self.assertEqual(
            "freebenefits",
            namespace["_run_native_v225_daily_catchup"](bot),
        )
        self.assertEqual(["freebenefits"], events)

        namespace["_native_v225_daily_flow_due"] = (
            lambda context, flow: flow == "share"
        )
        self.assertEqual(
            "share",
            namespace["_run_native_v225_daily_catchup"](bot),
        )
        self.assertEqual(["freebenefits", "share"], events)

    def test_loaded_patcher_guards_native_self_processor_before_farm_work(self):
        namespace = load_functions(
            "_wrap_native_v225_daily_catchup_run_cycle",
            "_patch_native_v225_daily_catchup_for_module",
            "_patch_native_v225_daily_catchup_loaded",
        )
        events = []

        class FarmBotCV:
            def process_self_farm(self):
                events.append("native-self")
                return "self-result"

        module = types.SimpleNamespace(FarmBotCV=FarmBotCV)
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.infrastructure.legacy_bot_engine": module}
        )
        namespace["_run_native_v225_daily_catchup"] = (
            lambda bot: events.append("freebenefits-catchup") or "freebenefits"
        )

        changed = namespace["_patch_native_v225_daily_catchup_loaded"]("test")
        bot = FarmBotCV()
        bot._qqfarm_live_scene_hint = "home"

        self.assertEqual(["bot.infrastructure.legacy_bot_engine:1"], changed)
        self.assertTrue(bot.process_self_farm())
        self.assertEqual(["freebenefits-catchup"], events)

    def test_loaded_patcher_also_guards_native_friend_processor_for_due_daily_work(self):
        namespace = load_functions(
            "_wrap_native_v225_daily_catchup_run_cycle",
            "_patch_native_v225_daily_catchup_for_module",
            "_patch_native_v225_daily_catchup_loaded",
        )
        events = []

        class FarmBotCV:
            def process_friend_farm(self):
                events.append("native-friend")
                return "friend-result"

        module = types.SimpleNamespace(FarmBotCV=FarmBotCV)
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.infrastructure.legacy_bot_engine": module}
        )
        namespace["_native_v225_daily_any_due"] = lambda bot: True
        namespace["_native_v225_request_home_for_daily"] = (
            lambda bot: events.append("return-home") or True
        )
        namespace["_run_native_v225_daily_catchup"] = lambda bot: ""

        changed = namespace["_patch_native_v225_daily_catchup_loaded"]("test")
        bot = FarmBotCV()
        bot._qqfarm_live_scene_hint = "friend"

        self.assertEqual(["bot.infrastructure.legacy_bot_engine:1"], changed)
        self.assertTrue(bot.process_friend_farm())
        self.assertEqual(["return-home"], events)

    def test_loaded_patcher_installs_narrow_run_cycle_bridge_in_native_owner_mode(self):
        namespace = load_functions(
            "_wrap_native_v225_daily_catchup_run_cycle",
            "_patch_native_v225_daily_catchup_for_module",
            "_patch_native_v225_daily_catchup_loaded",
        )
        self.assertIn("_patch_native_v225_daily_catchup_loaded", namespace)

        class FarmBotCV:
            def run_cycle(self):
                return "native"

        module = types.SimpleNamespace(FarmBotCV=FarmBotCV)
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.infrastructure.legacy_bot_engine": module}
        )
        namespace["_run_native_v225_daily_catchup"] = lambda bot: ""

        changed = namespace["_patch_native_v225_daily_catchup_loaded"]("test")
        bot = FarmBotCV()

        self.assertEqual(["bot.infrastructure.legacy_bot_engine:1"], changed)
        self.assertEqual("native", bot.run_cycle())
        self.assertTrue(getattr(
            FarmBotCV.run_cycle,
            "__qqfarm_native_v225_daily_catchup_wrapped__",
            False,
        ))
        self.assertEqual([], namespace["_patch_native_v225_daily_catchup_loaded"]("again"))


if __name__ == "__main__":
    unittest.main()
