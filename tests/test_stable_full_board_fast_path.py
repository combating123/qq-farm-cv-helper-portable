import ast
import types
import unittest
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURES = ROOT / "tests" / "fixtures"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def confirmed_full_ledger():
    return {
        "status": "aligned",
        "unknown_count": 0,
        "empty_count": 0,
        "occupied_count": 24,
        "ui_blocked": False,
        "full_board_confirmed": True,
    }


class StableFullBoardFastPathTests(unittest.TestCase):
    def test_process_self_wrapper_skips_native_heavy_scan_when_fast_gate_is_true(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        calls = []
        frame = object()
        bot = types.SimpleNamespace()
        namespace.update({
            "_stop_requested_in_args": lambda _args, _kwargs: False,
            "_qqfarm_install_visible_capture_priority": lambda _bot: False,
            "_qqfarm_runtime_page_readiness_gate": lambda _bot, _label: True,
            "_qqfarm_cap_runtime_recovery_waits": lambda _bot: 0,
            "_qqfarm_stable_full_board_fast_skip": lambda owner, candidate: (
                owner is bot and candidate is frame
            ),
            "_write": lambda _message: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_runtime_diag_repr": repr,
            "_runtime_diag_state": lambda _owner: "{}",
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        def native(owner, game_frame=None):
            calls.append((owner, game_frame))
            return True

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native, "FarmBotCV.process_self_farm"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, frame))
        self.assertEqual([], calls)

    def test_run_cycle_fast_gate_requires_recent_native_cycle_and_no_friend_route(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_run_cycle_fast_skip",
        )
        gate = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"]
        frame = object()
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=90.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
        )
        calls = []
        namespace.update({
            "_qqfarm_friend_route_expected": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_qqfarm_stable_full_board_fast_skip": (
                lambda owner, candidate, now_ts=None: calls.append(
                    (owner, candidate, now_ts)
                ) or True
            ),
            "_throttled_write": lambda *_args, **_kwargs: None,
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        self.assertTrue(gate(bot, now_ts=100.0))
        self.assertEqual([(bot, frame, 100.0)], calls)

        bot._qqfarm_last_native_run_cycle_ts = 60.0
        calls.clear()
        self.assertFalse(gate(bot, now_ts=100.0))
        self.assertEqual([], calls)

        bot._qqfarm_last_native_run_cycle_ts = 90.0
        namespace["_qqfarm_friend_route_expected"] = lambda owner: True
        self.assertFalse(gate(bot, now_ts=100.0))

    def test_run_cycle_wrapper_skips_native_cycle_when_stable_idle_gate_is_true(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        calls = []
        bot = types.SimpleNamespace(
            _qqfarm_force_self_cycle_next=True,
            process_self_farm=lambda *args, **kwargs: calls.append("forced-self") or True,
        )
        post_calls = []
        namespace.update({
            "_stop_requested_in_args": lambda _args, _kwargs: False,
            "_qqfarm_install_visible_capture_priority": lambda _bot: False,
            "_daily_flow_log_user_summary": lambda _bot: None,
            "_qqfarm_runtime_page_readiness_gate": lambda _bot, _label: True,
            "_qqfarm_cap_runtime_recovery_waits": lambda _bot: 0,
            "_qqfarm_friend_route_expected": lambda _bot: False,
            "_qqfarm_stable_full_board_run_cycle_fast_skip": lambda owner: owner is bot,
            "_get_frame_from_bot": lambda _bot: object(),
            "_friend_guard_friend_ui_state": lambda _frame: False,
            "_set_friend_chain_fast_interval": lambda *_args: None,
            "_invoke_friend_guard_action": (
                lambda action, _identity, args, kwargs: action(*args, **kwargs)
            ),
            "_run_share_prompt_recovery": lambda _bot: post_calls.append("share"),
            "_apply_visual_friend_route_watchdog": (
                lambda *_args, **_kwargs: post_calls.append("watchdog") or False
            ),
            "_daily_metrics_sync_runtime": (
                lambda *_args, **_kwargs: post_calls.append("metrics")
            ),
            "_write": lambda _message: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_runtime_diag_repr": repr,
            "_runtime_diag_state": lambda _owner: "{}",
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        def native(owner):
            calls.append(owner)
            return True

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native, "FarmBotCV.run_cycle"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot))
        self.assertEqual([], calls)
        self.assertEqual(["share", "watchdog", "metrics"], post_calls)
        self.assertFalse(hasattr(bot, "_qqfarm_last_native_run_cycle_ts"))

    def test_real_stable_full_board_matches_but_action_overlay_does_not(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_frame_signature",
            "_qqfarm_stable_full_board_fast_skip",
        )
        self.assertIn("_qqfarm_stable_full_board_frame_signature", namespace)
        self.assertIn("_qqfarm_stable_full_board_fast_skip", namespace)
        stable = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-stable.png"
        ), cv2.IMREAD_COLOR)
        action = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-action-overlay.png"
        ), cv2.IMREAD_COLOR)
        self.assertIsNotNone(stable)
        self.assertIsNotNone(action)
        signature = namespace["_qqfarm_stable_full_board_frame_signature"](stable)
        bot = types.SimpleNamespace(
            _qqfarm_verified_self_no_action_ts=95.0,
            _qqfarm_verified_self_no_action_full_scan_ts=95.0,
            _qqfarm_verified_self_no_action_frame_signature=signature,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_anchor_count=2,
            _qqfarm_recent_empty_land_centers=[],
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_single_harvest_planting_pending=False,
            _qqfarm_24_slot_ledger=confirmed_full_ledger(),
            planting_harvest_quota=0,
        )
        namespace["_qqfarm_home_priority_active"] = lambda _bot: False
        namespace["_throttled_write"] = lambda *_args, **_kwargs: None

        self.assertTrue(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, stable.copy(), now_ts=100.0
        ))
        self.assertFalse(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, action, now_ts=101.0
        ))

    def test_real_empty_board_and_pending_home_work_force_native_scan(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_frame_signature",
            "_qqfarm_stable_full_board_fast_skip",
        )
        stable = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-stable.png"
        ), cv2.IMREAD_COLOR)
        partial = cv2.imread(str(
            FIXTURES / "live-v315-partial-empty-after-harvest-20260803.png"
        ), cv2.IMREAD_COLOR)
        signature = namespace["_qqfarm_stable_full_board_frame_signature"](stable)
        bot = types.SimpleNamespace(
            _qqfarm_verified_self_no_action_ts=95.0,
            _qqfarm_verified_self_no_action_full_scan_ts=95.0,
            _qqfarm_verified_self_no_action_frame_signature=signature,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_anchor_count=2,
            _qqfarm_recent_empty_land_centers=[],
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_single_harvest_planting_pending=False,
            planting_harvest_quota=0,
        )
        namespace["_qqfarm_home_priority_active"] = lambda _bot: False
        namespace["_throttled_write"] = lambda *_args, **_kwargs: None

        self.assertFalse(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, partial, now_ts=100.0
        ))
        bot._qqfarm_home_empty_land_pending = True
        self.assertFalse(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, stable, now_ts=100.0
        ))


    def test_unknown_24_slot_ledger_cannot_enable_full_board_fast_skip(self):
        """A stale zero-empty cache is never enough when L07 is unresolved."""
        namespace = load_functions(
            "_qqfarm_stable_full_board_frame_signature",
            "_qqfarm_stable_full_board_fast_skip",
        )
        stable = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-stable.png"
        ), cv2.IMREAD_COLOR)
        self.assertIsNotNone(stable)
        signature = namespace["_qqfarm_stable_full_board_frame_signature"](stable)
        bot = types.SimpleNamespace(
            _qqfarm_verified_self_no_action_ts=95.0,
            _qqfarm_verified_self_no_action_full_scan_ts=95.0,
            _qqfarm_verified_self_no_action_frame_signature=signature,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_anchor_count=2,
            _qqfarm_recent_empty_land_centers=[],
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_single_harvest_planting_pending=False,
            _qqfarm_24_slot_ledger={
                "status": "unknown",
                "unknown_count": 1,
                "empty_count": 0,
                "occupied_count": 23,
                "ui_blocked": False,
                "full_board_confirmed": False,
            },
            planting_harvest_quota=0,
        )
        namespace["_qqfarm_home_priority_active"] = lambda _bot: False
        namespace["_throttled_write"] = lambda *_args, **_kwargs: None

        self.assertFalse(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, stable, now_ts=100.0
        ))

    def test_periodic_deep_scan_is_forced_after_sixty_seconds(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_frame_signature",
            "_qqfarm_stable_full_board_fast_skip",
        )
        stable = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-stable.png"
        ), cv2.IMREAD_COLOR)
        signature = namespace["_qqfarm_stable_full_board_frame_signature"](stable)
        bot = types.SimpleNamespace(
            _qqfarm_verified_self_no_action_ts=95.0,
            _qqfarm_verified_self_no_action_full_scan_ts=40.0,
            _qqfarm_verified_self_no_action_frame_signature=signature,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_anchor_count=2,
            _qqfarm_recent_empty_land_centers=[],
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_single_harvest_planting_pending=False,
            planting_harvest_quota=0,
        )
        namespace["_qqfarm_home_priority_active"] = lambda _bot: False
        namespace["_throttled_write"] = lambda *_args, **_kwargs: None

        self.assertFalse(namespace["_qqfarm_stable_full_board_fast_skip"](
            bot, stable, now_ts=100.0
        ))


    def test_repeated_stable_patrols_use_one_native_scan_per_sixty_seconds(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_frame_signature",
            "_qqfarm_stable_full_board_fast_skip",
            "_wrap_runtime_diag_method",
        )
        stable = cv2.imread(str(
            FIXTURES / "full-board-merged-purple-crop-stable.png"
        ), cv2.IMREAD_COLOR)
        clock = {"now": 100.0}
        calls = []
        bot = types.SimpleNamespace(
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_single_harvest_planting_pending=False,
            _qqfarm_backpack_inventory_scan_pending=False,
            planting_harvest_quota=0,
        )

        def native(owner, game_frame=None):
            calls.append(clock["now"])
            owner._qqfarm_empty_land_board_gate_state = "confirmed"
            owner._qqfarm_empty_land_board_anchor_count = 2
            owner._qqfarm_recent_empty_land_centers = []
            owner._qqfarm_recent_empty_land_count = 0
            owner._qqfarm_recent_empty_land_rejected_centers = [(276, 467)]
            owner._qqfarm_24_slot_ledger = confirmed_full_ledger()
            return False

        namespace.update({
            "_stop_requested_in_args": lambda _args, _kwargs: False,
            "_qqfarm_install_visible_capture_priority": lambda _bot: False,
            "_qqfarm_runtime_page_readiness_gate": lambda _bot, _label: True,
            "_qqfarm_cap_runtime_recovery_waits": lambda _bot: 0,
            "_qqfarm_home_priority_active": lambda _bot: False,
            "_qqfarm_try_clear_withered_land": lambda *_args: False,
            "_qqfarm_recover_visual_empty_lands_after_self_no_action": (
                lambda *_args: False
            ),
            "_qqfarm_capture_self_farm_diagnostic": lambda *_args, **_kwargs: False,
            "_write": lambda _message: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_runtime_diag_repr": repr,
            "_runtime_diag_state": lambda _owner: "{}",
            "time": types.SimpleNamespace(time=lambda: clock["now"]),
        })
        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native, "FarmBotCV.process_self_farm"
        )
        self.assertTrue(changed)

        for now in (100.0, 112.0, 124.0, 136.0, 148.0, 160.0):
            clock["now"] = now
            self.assertFalse(wrapped(bot, stable.copy()))

        self.assertEqual([100.0, 160.0], calls)
        self.assertEqual(160.0, bot._qqfarm_verified_self_no_action_full_scan_ts)
        self.assertIsNotNone(
            bot._qqfarm_verified_self_no_action_frame_signature
        )


    def test_run_cycle_fast_gate_releases_native_cycle_when_daily_flow_is_due(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_run_cycle_fast_skip",
        )
        gate = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"]
        frame = object()
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=90.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
        )
        namespace.update({
            "_qqfarm_friend_route_expected": lambda _owner: False,
            "_share_recovery_due": lambda _owner: False,
            "_qqfarm_native_daily_cycle_due": lambda owner: owner is bot,
            "_get_frame_from_bot": lambda _owner: frame,
            "_qqfarm_stable_full_board_fast_skip": lambda *_args, **_kwargs: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        self.assertFalse(gate(bot, now_ts=100.0))

    def test_native_daily_due_requires_enabled_unfinished_unblocked_flow(self):
        namespace = load_functions("_qqfarm_native_daily_cycle_due")
        self.assertIn("_qqfarm_native_daily_cycle_due", namespace)
        due = namespace["_qqfarm_native_daily_cycle_due"]
        completed = set()
        blocked = set()
        enabled = {
            "enable_daily_freebenefits": "True",
            "enable_daily_task": "True",
        }
        namespace.update({
            "_active_bot_sections": lambda: ("bot",),
            "_cfg_get": lambda _sections, key, default="False": enabled.get(
                key, default
            ),
            "_truthy": lambda value, default=False: str(value).lower() == "true",
            "_daily_flow_success_today": lambda flow: flow in completed,
            "_daily_flow_retry_blocked": lambda flow: flow in blocked,
        })

        self.assertTrue(due(types.SimpleNamespace()))
        completed.add("freebenefits")
        self.assertTrue(due(types.SimpleNamespace()))
        blocked.add("task")
        self.assertFalse(due(types.SimpleNamespace()))


    def test_run_cycle_fast_gate_rejects_friend_list_resume_pending(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_run_cycle_fast_skip",
        )
        gate = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"]
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=90.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
            _qqfarm_friend_list_resume_pending=True,
            _qqfarm_friend_list_visit_cursor=4,
            _qqfarm_friend_list_visible_candidate_count=5,
        )
        namespace.update({
            "_qqfarm_friend_route_expected": lambda _owner: False,
            "_share_recovery_due": lambda _owner: False,
            "_qqfarm_native_daily_cycle_due": lambda _owner: False,
            "_get_frame_from_bot": lambda _owner: object(),
            "_qqfarm_stable_full_board_fast_skip": lambda *_args, **_kwargs: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        self.assertFalse(gate(bot, now_ts=100.0))

    def test_run_cycle_fast_gate_rejects_visible_friend_list_frame(self):
        """A visible multi-row friend list must reach the friend dispatcher."""
        namespace = load_functions(
            "_qqfarm_stable_full_board_run_cycle_fast_skip",
        )
        gate = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"]
        frame = object()
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=90.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
        )
        rows = [{"center": (312, 300 + index * 100)} for index in range(5)]
        namespace.update({
            "_qqfarm_friend_route_expected": lambda _owner: False,
            "_share_recovery_due": lambda _owner: False,
            "_qqfarm_native_daily_cycle_due": lambda _owner: False,
            "_get_frame_from_bot": lambda _owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: (
                rows if candidate is frame else []
            ),
            "_qqfarm_stable_full_board_fast_skip": lambda *_args, **_kwargs: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        self.assertFalse(gate(bot, now_ts=100.0))

    def test_run_cycle_fast_gate_rejects_explicit_force_self_cycle(self):
        namespace = load_functions(
            "_qqfarm_stable_full_board_run_cycle_fast_skip",
        )
        gate = namespace["_qqfarm_stable_full_board_run_cycle_fast_skip"]
        bot = types.SimpleNamespace(
            _qqfarm_last_native_run_cycle_ts=90.0,
            stable_full_board_native_cycle_interval_seconds=30.0,
            _qqfarm_force_self_cycle_next=True,
        )
        namespace.update({
            "_qqfarm_friend_route_expected": lambda _owner: False,
            "_share_recovery_due": lambda _owner: False,
            "_qqfarm_native_daily_cycle_due": lambda _owner: False,
            "_get_frame_from_bot": lambda _owner: object(),
            "_qqfarm_stable_full_board_fast_skip": lambda *_args, **_kwargs: True,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "time": types.SimpleNamespace(time=lambda: 100.0),
        })

        self.assertFalse(gate(bot, now_ts=100.0))


if __name__ == "__main__":
    unittest.main()

