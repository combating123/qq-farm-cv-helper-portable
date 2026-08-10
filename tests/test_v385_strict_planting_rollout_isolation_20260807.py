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
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class StrictPlantingRolloutIsolation20260807Tests(unittest.TestCase):
    def test_rollout_fast_skip_does_not_probe_friend_share_or_daily_routes(self):
        """The temporary 12-slot rollout must keep an idle full board inside planting scope."""
        namespace = load_functions("_qqfarm_stable_full_board_run_cycle_fast_skip")
        calls = []
        namespace.update({
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_qqfarm_friend_route_expected": lambda _bot: calls.append("friend") or True,
            "_share_recovery_due": lambda _bot: calls.append("share") or True,
            "_qqfarm_native_daily_cycle_due": lambda _bot: calls.append("daily") or True,
            "_get_frame_from_bot": lambda _bot: object(),
            "_qqfarm_stable_full_board_fast_skip": lambda *_args, **_kwargs: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=100.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
            _qqfarm_force_self_cycle_next=False,
            _qqfarm_friend_list_resume_pending=False,
        )

        result = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"](
            bot, now_ts=110.0
        )

        self.assertTrue(result)
        self.assertEqual([], calls)
        self.assertEqual(1, bot._qqfarm_stable_full_board_run_cycle_skip_count)

    def test_rollout_fast_skip_does_not_run_share_friend_or_periodic_daily_side_effects(self):
        """A run_cycle full-board fast skip may return, but it must not leave planting scope."""
        namespace = load_functions("_wrap_runtime_diag_method")
        effects = []
        namespace.update({
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_qqfarm_install_visible_capture_priority": lambda _bot: None,
            "_daily_flow_log_user_summary": lambda _bot: None,
            "_qqfarm_runtime_page_readiness_gate": lambda *_args: True,
            "_qqfarm_cap_runtime_recovery_waits": lambda _bot: 0,
            "_apply_runtime_go_home_threshold_floor": lambda *_args: 0,
            "_qqfarm_home_priority_active": lambda _bot: False,
            "_run_initial_home_probe": lambda _bot: (False, None),
            "_qqfarm_stable_full_board_run_cycle_fast_skip": lambda _bot: True,
            "_run_share_prompt_recovery": lambda _bot: effects.append("share"),
            "_apply_visual_friend_route_watchdog": (
                lambda *_args: effects.append("friend")
            ),
            "_daily_metrics_sync_runtime": (
                lambda *_args, **_kwargs: effects.append("daily")
            ),
            "_stop_requested_in_args": lambda *_args: False,
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })
        native_calls = []

        def native(bot):
            native_calls.append(bot)
            return "native"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native, "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)

        result = wrapped(types.SimpleNamespace())

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], effects)

    def test_rollout_first_run_routes_to_strict_self_cycle_before_nonplanting_preflight(self):
        """A strict first run must bypass every native/share/friend/daily route.

        This covers the live RED where no pending Lxx had been created yet, so
        the existing home-priority and full-board gates could not protect the
        first native ``run_cycle`` call.
        """
        namespace = load_functions("_wrap_runtime_diag_method")
        effects = []
        strict_calls = []
        bot = types.SimpleNamespace()
        namespace.update({
            "time": __import__("time"),
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_qqfarm_install_visible_capture_priority": lambda _bot: None,
            "_daily_flow_log_user_summary": (
                lambda _bot: effects.append("daily-summary")
            ),
            "_qqfarm_runtime_page_readiness_gate": lambda *_args: True,
            "_qqfarm_run_strict_self_planting_cycle": (
                lambda context: strict_calls.append(context) or "strict-self-result"
            ),
            "_qqfarm_cap_runtime_recovery_waits": lambda _bot: 0,
            "_apply_runtime_go_home_threshold_floor": lambda *_args: 0,
            "_qqfarm_home_priority_active": (
                lambda _bot: effects.append("home-priority") or False
            ),
            "_run_initial_home_probe": (
                lambda _bot: effects.append("initial-home-probe") or (False, None)
            ),
            "_qqfarm_stable_full_board_run_cycle_fast_skip": (
                lambda _bot: effects.append("full-board-fast-skip") or False
            ),
            "_restore_runtime_business_switches": lambda _bot: 0,
            "_run_share_prompt_recovery": lambda _bot: effects.append("share"),
            "_get_frame_from_bot": lambda _bot: object(),
            "_friend_list_visit_button_rows": (
                lambda _frame: effects.append("friend-list-preflight") or []
            ),
            "_handle_friend_list_surface": lambda *_args: False,
            "_friend_guard_clear_prequalification": (
                lambda _bot: effects.append("friend-guard-clear")
            ),
            "_qqfarm_resolve_friend_route_frame": (
                lambda _bot, frame: (frame, None)
            ),
            "_apply_visual_friend_route_watchdog": (
                lambda *_args, **_kwargs: effects.append("friend-watchdog")
            ),
            "_daily_metrics_sync_runtime": (
                lambda *_args, **_kwargs: effects.append("daily-metrics")
            ),
            "_stop_requested_in_args": lambda *_args, **_kwargs: False,
            "_runtime_diag_repr": lambda _value: "",
            "_runtime_diag_state": lambda _bot: "",
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })
        native_calls = []

        def native(owner):
            native_calls.append(owner)
            return "native-result"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native, "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)

        result = wrapped(bot)

        self.assertEqual("strict-self-result", result)
        self.assertEqual([bot], strict_calls)
        self.assertEqual([], native_calls)
        self.assertEqual([], effects)

    def test_strict_self_cycle_uses_one_fresh_home_frame_and_only_processes_self(self):
        """The self-only gate hands one confirmed home frame to the strict transaction."""
        namespace = load_functions("_qqfarm_run_strict_self_planting_cycle")
        frame = object()
        calls = []
        bot = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_allow_home=True,
        )
        friend_state_before = {
            name: getattr(bot, name)
            for name in (
                "_qqfarm_friend_chain_pending",
                "_qqfarm_friend_chain_active",
                "_qqfarm_friend_chain_allow_home",
            )
        }

        def process_self_farm(current_frame):
            calls.append(("legacy-self", current_frame))
            return "legacy-self-result"

        def strict_transaction(owner, initial_frame=None):
            self.assertIs(bot, owner)
            strict_calls.append((owner, initial_frame))
            return "self-planting-result"

        strict_calls = []
        bot.process_self_farm = process_self_farm
        namespace.update({
            "_get_frame_from_bot": lambda current: frame if current is bot else None,
            "_friend_guard_friend_ui_state": (
                lambda current_frame: False if current_frame is frame else None
            ),
            "_invoke_friend_guard_action": (
                lambda action, _target, args, kwargs: action(*args[1:], **kwargs)
            ),
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_qqfarm_run_strict_24slot_harvest_then_replant_transaction": strict_transaction,
        })

        result = namespace["_qqfarm_run_strict_self_planting_cycle"](bot)

        self.assertEqual("self-planting-result", result)
        self.assertEqual([], calls)
        self.assertEqual([(bot, frame)], strict_calls)
        self.assertEqual(
            friend_state_before,
            {name: getattr(bot, name) for name in friend_state_before},
        )
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)
        self.assertTrue(bot._qqfarm_force_self_cycle_next)

    def test_strict_self_cycle_rejects_friend_or_unknown_frames_without_clicking(self):
        """A non-home frame remains a no-click observation during strict sign-off."""
        namespace = load_functions("_qqfarm_run_strict_self_planting_cycle")
        calls = []
        bot = types.SimpleNamespace(
            process_self_farm=lambda *_args, **_kwargs: calls.append("self") or True
        )
        namespace.update({
            "_get_frame_from_bot": lambda _bot: object(),
            "_friend_guard_friend_ui_state": lambda _frame: None,
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        result = namespace["_qqfarm_run_strict_self_planting_cycle"](bot)

        self.assertFalse(result)
        self.assertEqual([], calls)

    def test_rollout_blocks_seed_shop_before_the_native_purchase(self):
        """Existing 1x1 stock must be resolved without a shop fallback during sign-off."""
        namespace = load_functions("_wrap_buy_seed_for_crop_backpack_guard")
        namespace.update({
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_write": lambda *_args, **_kwargs: None,
        })
        native_calls = []

        def native(*args, **kwargs):
            native_calls.append((args, kwargs))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        self.assertTrue(changed)
        bot = types.SimpleNamespace()

        result = wrapped(bot, "FALLBACK_CROP")

        self.assertFalse(result)
        self.assertEqual([], native_calls)

    def test_rollout_pending_slots_make_friend_chain_finalizer_a_noop(self):
        """Any route reaching the finalizer must still preserve strict pending Lxx."""
        namespace = load_functions("_finalize_friend_chain_after_troublemaker")
        side_effects = []
        bot = types.SimpleNamespace(
            _qqfarm_fixed_slot_pending_slot_ids=("L01", "L02"),
            _qqfarm_fixed_slot_pending_lands=[
                {"slot_id": "L01", "center": (185, 454)},
                {"slot_id": "L02", "center": (224, 454)},
            ],
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_troublemaker_retry_scan_active=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_visual_friend_count=7,
            _qqfarm_friend_branch_last_ts=99.0,
            _last_friend_farm_go_home_present=True,
            _qqfarm_friend_action_last_label="help",
        )
        state_before = dict(vars(bot))
        namespace.update({
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_set_friend_chain_fast_interval": (
                lambda *_args: side_effects.append("interval") or True
            ),
            "_friend_guard_clear_prequalification": (
                lambda *_args: side_effects.append("clear") or True
            ),
        })

        result = namespace["_finalize_friend_chain_after_troublemaker"](bot)

        self.assertFalse(result)
        self.assertEqual([], side_effects)
        self.assertEqual(state_before, dict(vars(bot)))

    def test_rollout_home_priority_blocks_friend_route_without_clearing_friend_chain(self):
        """Strict 24-slot sign-off keeps queued Lxx and friend-chain state frozen."""
        namespace = load_functions("_wrap_vip_business_func")
        finalizer_calls = []
        logs = []
        pending_lands = [
            {"slot_id": "L01", "center": (185, 454)},
            {"slot_id": "L02", "center": (224, 454)},
        ]
        bot = types.SimpleNamespace(
            _qqfarm_fixed_slot_pending_slot_ids=("L01", "L02"),
            _qqfarm_fixed_slot_pending_lands=list(pending_lands),
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_troublemaker_retry_scan_active=True,
            _qqfarm_visual_friend_count=7,
            _qqfarm_friend_branch_last_ts=99.0,
            _qqfarm_force_self_cycle_next=False,
            _qqfarm_cycle_branch_hint="friend",
        )
        friend_state_before = {
            name: getattr(bot, name)
            for name in (
                "_qqfarm_friend_chain_pending",
                "_qqfarm_friend_chain_exhausted",
                "_qqfarm_friend_chain_active",
                "_qqfarm_friend_chain_allow_home",
                "_qqfarm_friend_cycle_seen",
                "_qqfarm_troublemaker_retry_scan_active",
                "_qqfarm_visual_friend_count",
                "_qqfarm_friend_branch_last_ts",
            )
        }

        def finalizer(context):
            finalizer_calls.append(context)
            context._qqfarm_friend_chain_pending = False
            context._qqfarm_friend_chain_exhausted = False
            context._qqfarm_friend_chain_active = False
            context._qqfarm_friend_chain_allow_home = False
            context._qqfarm_friend_cycle_seen = False
            return True

        native_calls = []
        def native(owner):
            native_calls.append(owner)
            return True

        namespace.update({
            "_stop_requested_in_args": lambda *_args, **_kwargs: False,
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_qqfarm_home_priority_active": lambda _bot: True,
            "_qqfarm_strict_planting_rollout_active": lambda _bot: True,
            "_finalize_friend_chain_after_troublemaker": finalizer,
            "_write": lambda message: logs.append(str(message)),
        })
        wrapped, changed = namespace["_wrap_vip_business_func"](
            native, "FarmBotCV.process_friend_farm"
        )

        result = wrapped(bot)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], finalizer_calls)
        self.assertEqual(("L01", "L02"), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(pending_lands, bot._qqfarm_fixed_slot_pending_lands)
        self.assertEqual({name: getattr(bot, name) for name in friend_state_before}, friend_state_before)
        self.assertTrue(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)
        self.assertTrue(any("home empty-land priority" in line for line in logs), logs)


if __name__ == "__main__":
    unittest.main()
