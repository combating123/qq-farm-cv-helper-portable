import ast
import time
import tempfile
import types
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

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
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class HomeEmptyLandPriorityTests(unittest.TestCase):
    def test_home_empty_land_blocks_friend_route_until_two_zero_observations(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
        )
        self.assertIn("_qqfarm_home_priority_active", namespace)
        self.assertIn("_qqfarm_update_home_priority", namespace)
        namespace["_write"] = lambda _message: None
        context = types.SimpleNamespace()

        namespace["_qqfarm_update_home_priority"](
            context, 4, now_ts=100.0, reason="detected-empty"
        )
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        self.assertEqual(4, context._qqfarm_home_empty_land_remaining)
        self.assertTrue(context._qqfarm_force_self_cycle_next)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)

        namespace["_qqfarm_update_home_priority"](
            context, 0, now_ts=101.0, reason="first-zero"
        )
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        self.assertEqual(1, context._qqfarm_home_empty_zero_confirmations)

        namespace["_qqfarm_update_home_priority"](
            context, 0, now_ts=102.0, reason="second-zero"
        )
        self.assertFalse(namespace["_qqfarm_home_priority_active"](context))
        self.assertEqual(0, context._qqfarm_home_empty_land_remaining)

    def test_home_planting_live_ocr_unavailable_runs_backpack_only_and_restores_shop_guard(self):
        namespace = load_functions("_wrap_home_planting_cooldown")
        logs = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_LAST_SUCCESSFUL_FULL_PLANTING_TS": 0.0,
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_qqfarm_home_priority_active": lambda _context: False,
            "_throttled_write": lambda *args, **kwargs: None,
            "_write": lambda message: logs.append(message),
        })
        native_calls = []
        level_calls = []
        bot = types.SimpleNamespace(
            planting_post_success_cooldown_seconds=180.0,
            _qqfarm_single_harvest_planting_pending=False,
        )

        def no_live_level():
            level_calls.append(True)
            bot._qqfarm_player_level_dynamic_pending = True
            bot._last_player_level_detect_source = "live-ocr-unavailable"
            return 0

        def native(owner, frame=None):
            native_calls.append((
                owner,
                frame,
                getattr(owner, "_qqfarm_block_level_based_shop", False),
            ))
            return True

        bot.get_current_player_level = no_live_level
        wrapped, changed = namespace["_wrap_home_planting_cooldown"](
            native,
            "fixture.handle_home_planting",
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "frame"))
        self.assertEqual([True], level_calls)
        self.assertEqual([(bot, "frame", True)], native_calls)
        self.assertTrue(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)
        self.assertFalse(hasattr(bot, "_qqfarm_block_level_based_shop"))
        self.assertTrue(any("backpack-only" in message for message in logs))

    def test_home_priority_bypasses_post_planting_cooldown_for_verification(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_home_planting_cooldown",
        )
        self.assertIn("_qqfarm_home_priority_active", namespace)
        self.assertIn("_qqfarm_update_home_priority", namespace)
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 150.0),
            "_LAST_SUCCESSFUL_FULL_PLANTING_TS": 100.0,
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_throttled_write": lambda *args, **kwargs: None,
            "_write": lambda _message: None,
        })
        context = types.SimpleNamespace(
            planting_post_success_cooldown_seconds=180.0,
            _qqfarm_single_harvest_planting_pending=False,
        )
        namespace["_qqfarm_update_home_priority"](
            context, 4, now_ts=100.0, reason="detected-empty"
        )
        calls = []
        wrapped, changed = namespace["_wrap_home_planting_cooldown"](
            lambda owner, frame=None: calls.append((owner, frame)) or True,
            "fixture.handle_home_planting",
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(context, "frame"))
        self.assertEqual([(context, "frame")], calls)

    def test_partial_radish_inventory_is_planted_before_opening_seed_shop(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        self.assertIn("_qqfarm_home_priority_active", namespace)
        self.assertIn("_qqfarm_update_home_priority", namespace)
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        now = time.time()
        lands = [
            {"center": (10, 10)},
            {"center": (20, 20)},
            {"center": (30, 30)},
            {"center": (40, 40)},
        ]
        partial_calls = []
        bot = types.SimpleNamespace(
            _qqfarm_radish_inventory_qty=3,
            _qqfarm_radish_inventory_seen_ts=now,
            _qqfarm_recent_empty_land_count=4,
            _qqfarm_recent_empty_lands=lands,
            _try_planting_with_direct_lands=(
                lambda owner, crop_name, selected_lands:
                partial_calls.append((owner, crop_name, selected_lands)) or (True, False)
            ),
        )
        shop_calls = []

        def native(owner, crop_name):
            shop_calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "\u767d\u841d\u535c"))
        self.assertEqual([], shop_calls)
        self.assertEqual(1, len(partial_calls))
        self.assertEqual(lands[:3], partial_calls[0][2])
        self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
        self.assertTrue(any("partial radish inventory planted" in message for message in logs))

        bot._qqfarm_radish_inventory_qty = 0
        self.assertTrue(wrapped(bot, "\u767d\u841d\u535c"))
        self.assertEqual([(bot, "\u767d\u841d\u535c")], shop_calls)
        self.assertEqual(4, bot._qqfarm_radish_inventory_qty)
        self.assertGreater(bot._qqfarm_radish_inventory_seen_ts, 0.0)

    def test_seed_template_miss_uses_native_shovel_drag_before_rebuying(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        now = time.time()
        lands = [{"center": (10, 10)}, {"center": (20, 20)}]
        drag_calls = []
        shop_calls = []
        bot = types.SimpleNamespace(
            _qqfarm_radish_inventory_qty=2,
            _qqfarm_radish_inventory_seen_ts=now,
            _qqfarm_recent_empty_land_count=2,
            _qqfarm_recent_empty_lands=lands,
            _qqfarm_recent_empty_land_ts=now,
            _try_planting_with_direct_lands=(
                lambda _owner, _crop, _lands: (False, False)
            ),
            _execute_planting_by_mode=(
                lambda owner, seed_match, selected_lands, crop_name,
                       run_post_fertilizer=True:
                drag_calls.append((
                    owner, seed_match, selected_lands,
                    crop_name, run_post_fertilizer,
                )) or True
            ),
        )
        namespace["_write"] = lambda _message: None

        def native(owner, crop_name):
            shop_calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "\u767d\u841d\u535c"))
        self.assertEqual([], shop_calls)
        self.assertEqual(1, len(drag_calls))
        self.assertIsNone(drag_calls[0][1])
        self.assertEqual(lands, drag_calls[0][2])
        self.assertTrue(drag_calls[0][4])

    def test_runtime_logs_track_radish_stock_and_keep_home_priority_after_planting(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_note_runtime_planting_outcome",
        )
        self.assertIn("_qqfarm_home_priority_active", namespace)
        self.assertIn("_qqfarm_update_home_priority", namespace)
        context = types.SimpleNamespace()
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_LAST_SUCCESSFUL_FULL_PLANTING_TS": 0.0,
            "_ACTIVE_RUN_CYCLE_CONTEXT": context,
            "_write": lambda _message: None,
        })

        namespace["_note_runtime_planting_outcome"](
            "\u64ad\u79cd\u9762\u677f\u79cd\u5b50\u6570\u91cfOCR\uff1a\u767d\u841d\u535c=8"
        )
        self.assertEqual(8, context._qqfarm_radish_inventory_qty)

        namespace["_qqfarm_update_home_priority"](
            context, 4, now_ts=100.0, reason="detected-empty"
        )
        namespace["_note_runtime_planting_outcome"](
            "\u2714 \u5df2\u5b8c\u6210\u64ad\u79cd\uff1a\u767d\u841d\u535c x 4"
        )
        self.assertEqual(4, context._qqfarm_radish_inventory_qty)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        self.assertTrue(context._qqfarm_force_self_cycle_next)

        namespace["_note_runtime_planting_outcome"]("\u5bb6\u91cc\u5df2\u65e0\u53ef\u6267\u884c\u7684\u4efb\u52a1")
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        namespace["_note_runtime_planting_outcome"]("\u5bb6\u91cc\u5df2\u65e0\u53ef\u6267\u884c\u7684\u4efb\u52a1")
        self.assertFalse(namespace["_qqfarm_home_priority_active"](context))

    def test_home_priority_self_pass_runs_before_native_friend_routing(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_run_home_priority_self_pass",
        )
        self.assertIn("_run_home_priority_self_pass", namespace)
        frame = object()
        calls = []
        fast_interval_calls = []
        namespace.update({
            "_get_frame_from_bot": lambda _context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_invoke_friend_guard_action": (
                lambda action, _target, args, kwargs: action(
                    *(args[1:] if getattr(action, "__self__", None) is args[0] else args),
                    **kwargs
                )
            ),
            "_set_friend_chain_fast_interval": (
                lambda _owner, active: fast_interval_calls.append(active) or True
            ),
            "_write": lambda _message: None,
        })

        class Context:
            def process_self_farm(self, candidate_frame):
                calls.append(candidate_frame)
                return "self-ok"

        context = Context()
        namespace["_qqfarm_update_home_priority"](
            context, 4, now_ts=100.0, reason="detected-empty"
        )
        handled, result = namespace["_run_home_priority_self_pass"](context)

        self.assertTrue(handled)
        self.assertEqual("self-ok", result)
        self.assertEqual([frame], calls)
        self.assertEqual([True], fast_interval_calls)
        self.assertTrue(context._qqfarm_force_self_cycle_next)


    def test_initial_home_probe_returns_from_friend_before_friend_preflight(self):
        namespace = load_functions("_run_initial_home_probe")
        frame = object()
        calls = []
        logs = []
        namespace.update({
            "_get_frame_from_bot": lambda _context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: candidate is frame,
            "_invoke_friend_guard_action": (
                lambda action, _target, args, kwargs: action(
                    *(args[1:] if getattr(action, "__self__", None) is args[0] else args),
                    **kwargs
                )
            ),
            "_write": lambda message: logs.append(message),
        })

        class Context:
            pre_self_maintenance = True

            def check_go_home_icon(self, candidate_frame):
                calls.append(("home", candidate_frame))
                return "home-clicked"

        context = Context()
        handled, result = namespace["_run_initial_home_probe"](context)

        self.assertTrue(handled)
        self.assertEqual("home-clicked", result)
        self.assertEqual([("home", frame)], calls)
        self.assertTrue(context._qqfarm_initial_home_probe_pending)
        self.assertTrue(context._qqfarm_force_self_cycle_next)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)
        self.assertTrue(any("initial home probe return" in item for item in logs))

    def test_initial_home_probe_uses_coordinate_fallback_after_native_home_miss(self):
        namespace = load_functions("_run_initial_home_probe")
        friend_frame = object()
        home_frame = object()
        frames = iter((friend_frame, home_frame))
        native_calls = []
        coordinate_calls = []
        logs = []
        namespace.update({
            "_get_frame_from_bot": lambda _context: next(frames),
            "_friend_guard_friend_ui_state": (
                lambda candidate: True if candidate is friend_frame else False
            ),
            "_invoke_friend_guard_action": (
                lambda action, _target, args, kwargs: action(
                    *(args[1:] if getattr(action, "__self__", None) is args[0] else args),
                    **kwargs
                )
            ),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda owner, frame: coordinate_calls.append((owner, frame)) or True
            ),
            "_write": lambda message: logs.append(message),
        })

        class Context:
            pre_self_maintenance = True

            def check_go_home_icon(self, candidate_frame):
                native_calls.append(candidate_frame)
                return False

        context = Context()
        handled, result = namespace["_run_initial_home_probe"](context)

        self.assertTrue(handled)
        self.assertTrue(result)
        self.assertEqual([friend_frame], native_calls)
        self.assertEqual([(context, friend_frame)], coordinate_calls)
        self.assertTrue(context._qqfarm_initial_home_probe_pending)
        self.assertTrue(context._qqfarm_force_self_cycle_next)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)
        self.assertTrue(any("coordinate" in item for item in logs))

    def test_initial_home_probe_keeps_friend_route_blocked_after_three_missed_returns(self):
        namespace = load_functions("_run_initial_home_probe")
        friend_frame = object()
        coordinate_calls = []
        native_calls = []
        logs = []
        namespace.update({
            "_get_frame_from_bot": lambda _context: friend_frame,
            "_friend_guard_friend_ui_state": lambda _candidate: True,
            "_invoke_friend_guard_home_coordinate_click": (
                lambda owner, frame: coordinate_calls.append((owner, frame)) or False
            ),
            "_write": lambda message: logs.append(message),
        })

        class Context:
            pre_self_maintenance = True

            def check_go_home_icon(self, candidate_frame):
                native_calls.append(candidate_frame)
                return False

        context = Context()
        context._qqfarm_initial_home_probe_attempts = 3
        context._qqfarm_initial_home_probe_last_attempt_ts = 0.0
        handled, result = namespace["_run_initial_home_probe"](context)

        self.assertTrue(handled)
        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([(context, friend_frame)], coordinate_calls)
        self.assertTrue(context._qqfarm_initial_home_probe_pending)
        self.assertTrue(context._qqfarm_force_self_cycle_next)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)
        self.assertTrue(any("keeping friend route blocked" in item for item in logs))

    def test_initial_home_probe_checks_self_once_then_releases_friend_routing(self):
        namespace = load_functions("_run_initial_home_probe")
        frame = object()
        calls = []
        namespace.update({
            "_get_frame_from_bot": lambda _context: frame,
            "_friend_guard_friend_ui_state": lambda _candidate: False,
            "_invoke_friend_guard_action": (
                lambda action, _target, args, kwargs: action(
                    *(args[1:] if getattr(action, "__self__", None) is args[0] else args),
                    **kwargs
                )
            ),
            "_write": lambda _message: None,
        })

        class Context:
            pre_self_maintenance = True

            def process_self_farm(self, candidate_frame):
                calls.append(("self", candidate_frame))
                return "self-checked"

        context = Context()
        handled, result = namespace["_run_initial_home_probe"](context)

        self.assertTrue(handled)
        self.assertEqual("self-checked", result)
        self.assertEqual([("self", frame)], calls)
        self.assertTrue(context._qqfarm_initial_home_probe_complete)
        self.assertFalse(getattr(context, "_qqfarm_initial_home_probe_pending", False))
        self.assertFalse(context._qqfarm_force_self_cycle_next)


    def test_run_cycle_performs_initial_home_probe_before_friend_preflight(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        events = []

        class Scheduler:
            pass

        scheduler = Scheduler()

        def original(_context):
            events.append("native")
            return "native-result"

        def initial_home_probe(context):
            events.append(("initial-home", context))
            return True, "self-first-result"

        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_qqfarm_cap_runtime_recovery_waits": lambda _context: 0,
            "_apply_runtime_go_home_threshold_floor": lambda *_args: 0,
            "_qqfarm_home_priority_active": lambda _context: False,
            "_run_initial_home_probe": initial_home_probe,
            "_write": lambda _message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original, "FarmBotCV.run_cycle"
        )

        self.assertTrue(changed)
        self.assertEqual("self-first-result", wrapped(scheduler))
        self.assertEqual([("initial-home", scheduler)], events)


    def test_planting_flow_uses_bounded_panel_waits_and_restores_configuration(self):
        namespace = load_functions("_wrap_planting_flow_fast")
        self.assertIn("_wrap_planting_flow_fast", namespace)
        observed = []
        bot = types.SimpleNamespace(
            planting_panel_settle_seconds=2.0,
            planting_shovel_anchor_settle_seconds=1.5,
            seed_popup_verify_max_per_page=2,
            seed_page_max_turns=5,
        )

        def native(owner, frame, crop_name, allow_buy, **kwargs):
            observed.append((
                owner.planting_panel_settle_seconds,
                owner.planting_shovel_anchor_settle_seconds,
                owner.seed_popup_verify_max_per_page,
                owner.seed_page_max_turns,
                crop_name,
                allow_buy,
            ))
            return True

        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native, "fixture._run_planting_flow"
        )
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "frame", "\u767d\u841d\u535c", True))
        self.assertEqual(1, len(observed))
        self.assertLessEqual(observed[0][0], 0.65)
        self.assertLessEqual(observed[0][1], 0.40)
        self.assertEqual(0, observed[0][2])
        self.assertEqual(1, observed[0][3])
        self.assertEqual(2.0, bot.planting_panel_settle_seconds)
        self.assertEqual(1.5, bot.planting_shovel_anchor_settle_seconds)
        self.assertEqual(2, bot.seed_popup_verify_max_per_page)
        self.assertEqual(5, bot.seed_page_max_turns)

    def test_empty_land_detector_caches_raw_lands_for_partial_planting(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        lands = [{"center": (11, 22)}, {"center": (33, 44)}]
        bot = types.SimpleNamespace()
        namespace.update({
            "_empty_land_candidate_has_crop_cover": lambda _frame, _center: False,
            "_qqfarm_update_home_priority": lambda *_args, **_kwargs: None,
            "_write": lambda _message: None,
        })
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _owner, _frame: lands, "fixture._detect_empty_lands"
        )

        self.assertTrue(changed)
        self.assertEqual(lands, wrapped(bot, object()))
        self.assertEqual(lands, bot._qqfarm_recent_empty_lands)
        self.assertIsNot(lands, bot._qqfarm_recent_empty_lands)

    def test_known_radish_stock_limits_direct_lands_before_native_flow(self):
        namespace = load_functions("_wrap_planting_flow_fast")
        lands = [
            {"center": (10, 10)},
            {"center": (20, 20)},
            {"center": (30, 30)},
            {"center": (40, 40)},
        ]
        observed = []
        now = time.time()
        bot = types.SimpleNamespace(
            planting_panel_settle_seconds=2.0,
            planting_shovel_anchor_settle_seconds=1.5,
            seed_popup_verify_max_per_page=2,
            seed_page_max_turns=5,
            _qqfarm_radish_inventory_qty=3,
            _qqfarm_radish_inventory_seen_ts=now,
            _qqfarm_recent_empty_lands=lands,
            _qqfarm_recent_empty_land_ts=now,
        )

        def native(owner, frame, crop_name, allow_buy, direct_land_center=None,
                   direct_lands=None, queue_retry_when_not_empty=False):
            observed.append((
                crop_name, allow_buy, direct_land_center,
                direct_lands, queue_retry_when_not_empty,
                owner.seed_popup_verify_max_per_page,
            ))
            return True

        namespace["_write"] = lambda _message: None
        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native, "fixture._run_planting_flow"
        )
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "frame", "\u767d\u841d\u535c", True))
        self.assertEqual(1, len(observed))
        self.assertFalse(observed[0][1])
        self.assertEqual(lands[:3], observed[0][3])
        self.assertTrue(observed[0][4])
        self.assertEqual(0, observed[0][5])

    def test_non_radish_planting_keeps_configured_page_search_depth(self):
        namespace = load_functions("_wrap_planting_flow_fast")
        observed = []
        bot = types.SimpleNamespace(
            planting_panel_settle_seconds=2.0,
            planting_shovel_anchor_settle_seconds=1.5,
            seed_popup_verify_max_per_page=2,
            seed_page_max_turns=5,
        )

        def native(owner, _frame, crop_name, _allow_buy, **_kwargs):
            observed.append((crop_name, owner.seed_page_max_turns))
            return True

        namespace["_write"] = lambda _message: None
        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native, "fixture._run_planting_flow"
        )
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "frame", "\u91d1\u82b1\u8336", True))
        self.assertEqual([("\u91d1\u82b1\u8336", 5)], observed)

    def test_recent_log_restores_latest_radish_inventory_for_fast_restart(self):
        namespace = load_functions("_qqfarm_load_recent_radish_inventory_snapshot")
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "latest.log"
            log_path.write_text(
                "\u64ad\u79cd\u9762\u677f\u79cd\u5b50\u6570\u91cfOCR\uff1a"
                "\u767d\u841d\u535c=24\n"
                "\u5df2\u5b8c\u6210\u64ad\u79cd\uff1a\u767d\u841d\u535c x 6\n"
                "\u64ad\u79cd\u9762\u677f\u79cd\u5b50\u6570\u91cfOCR\uff1a"
                "\u767d\u841d\u535c=14\n"
                "\u5df2\u8bb0\u5f55\u4e70\u79cd\u8fd4\u56de\u7a7a\u5730\u5217\u8868\uff1a"
                "count=10\n"
                "\u5df2\u5b8c\u6210\u4e70\u79cd\uff1a\u767d\u841d\u535c\n",
                encoding="utf-8",
            )
            qty, seen_ts = namespace[
                "_qqfarm_load_recent_radish_inventory_snapshot"
            ](path=str(log_path), now_ts=time.time(), max_age_seconds=60.0)

        self.assertEqual(10, qty)
        self.assertGreater(seen_ts, 0.0)

    def test_radish_seed_count_uses_fresh_cached_inventory(self):
        namespace = load_functions("_wrap_radish_seed_count_fast")
        now = time.time()
        bot = types.SimpleNamespace(
            _qqfarm_radish_inventory_qty=14,
            _qqfarm_radish_inventory_seen_ts=now,
            _qqfarm_fast_radish_inventory_context=True,
        )
        native_calls = []
        namespace["_write"] = lambda _message: None
        wrapped, changed = namespace["_wrap_radish_seed_count_fast"](
            lambda *_args, **_kwargs: native_calls.append(True) or (99, 0.5),
            "fixture._detect_seed_count_ocr",
        )

        self.assertTrue(changed)
        self.assertEqual((14, 1.0), wrapped(bot, object(), (1, 2)))
        self.assertEqual([], native_calls)

    def test_planting_outcome_requires_fresh_empty_land_decrease_before_reporting_success(self):
        namespace = load_functions("_wrap_planting_outcome_verify_func")
        self.assertIn("_wrap_planting_outcome_verify_func", namespace)
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=5,
            _qqfarm_recent_empty_land_ts=time.time() - 5.0,
        )

        def native(owner, lands):
            owner._qqfarm_recent_empty_land_count = 5
            owner._qqfarm_recent_empty_land_ts = time.time()
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, [{"center": (10, 10)} for _ in range(5)]))
        self.assertFalse(bot._qqfarm_last_planting_outcome_verified)
        self.assertTrue(any("no visual empty-land decrease" in message for message in logs))

    def test_planting_outcome_refreshes_empty_lands_before_accepting_success(self):
        namespace = load_functions("_wrap_planting_outcome_verify_func")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        probe_frames = []
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=5,
            _qqfarm_recent_empty_land_ts=time.time() - 5.0,
            planting_visual_verify_delay_seconds=0.0,
        )

        def detect_empty_lands(frame):
            probe_frames.append(frame)
            bot._qqfarm_recent_empty_land_count = 3
            bot._qqfarm_recent_empty_land_ts = time.time()
            return [{"center": (10, 10)} for _ in range(3)]

        bot._detect_empty_lands = detect_empty_lands

        def native(owner, frame, lands):
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "fresh-frame", [{"center": (10, 10)} for _ in range(5)]))
        self.assertEqual(["fresh-frame"], probe_frames)
        self.assertTrue(bot._qqfarm_last_planting_outcome_verified)
        self.assertTrue(any("planting action visually verified" in message for message in logs))

    def test_planting_outcome_confirms_after_second_stable_empty_land_probe(self):
        namespace = load_functions(
            "_wrap_detect_empty_lands_state",
            "_wrap_planting_outcome_verify_func",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        probe_frames = []
        observations = [
            [{"center": (index * 20, 100)} for index in range(5)],
            [{"center": (index * 20, 100)} for index in range(3)],
            [{"center": (index * 20 + 2, 101)} for index in range(3)],
        ]

        def raw_detect_empty_lands(owner, frame):
            probe_frames.append(frame)
            return observations.pop(0)

        stable_detector, detector_changed = namespace["_wrap_detect_empty_lands_state"](
            raw_detect_empty_lands, "fixture._detect_empty_lands"
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=5,
            _qqfarm_recent_empty_land_ts=time.time() - 5.0,
            planting_visual_verify_delay_seconds=0.0,
        )
        bot._detect_empty_lands = types.MethodType(stable_detector, bot)
        bot._detect_empty_lands("pre-plant-frame")
        bot._qqfarm_recent_empty_land_ts = time.time() - 5.0
        probe_frames.clear()

        def native(owner, frame, lands):
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )

        self.assertTrue(detector_changed)
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "fresh-frame", [{"center": (10, 10)} for _ in range(5)]))
        self.assertEqual(["fresh-frame", "fresh-frame"], probe_frames)
        self.assertEqual(3, bot._qqfarm_recent_empty_land_count)
        self.assertTrue(bot._qqfarm_last_planting_outcome_verified)
        self.assertTrue(any("planting action visually verified" in message for message in logs))

    def test_planting_outcome_prefers_latest_bot_frame_over_preplant_frame(self):
        namespace = load_functions("_wrap_planting_outcome_verify_func")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        probe_frames = []
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=5,
            _qqfarm_recent_empty_land_ts=time.time() - 5.0,
            _qqfarm_current_frame="post-plant-frame",
            planting_visual_verify_delay_seconds=0.0,
        )

        def detect_empty_lands(frame):
            probe_frames.append(frame)
            if frame == "post-plant-frame":
                bot._qqfarm_recent_empty_land_count = 3
            else:
                bot._qqfarm_recent_empty_land_count = 5
            bot._qqfarm_recent_empty_land_ts = time.time()
            return [{"center": (10, 10)} for _ in range(bot._qqfarm_recent_empty_land_count)]

        bot._detect_empty_lands = detect_empty_lands

        def native(owner, frame, lands):
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "pre-plant-frame", [{"center": (10, 10)} for _ in range(5)]))
        self.assertEqual(["post-plant-frame"], probe_frames)
        self.assertTrue(bot._qqfarm_last_planting_outcome_verified)
        self.assertTrue(any("planting action visually verified" in message for message in logs))

    def test_composed_drag_planting_wrappers_remain_idempotent_on_repatch(self):
        namespace = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_wrap_planting_crop_context_func",
            "_wrap_planting_outcome_verify_func",
        )

        def native(owner, frame, lands):
            return True

        crop_wrapped, crop_changed = namespace["_wrap_planting_crop_context_func"](
            native, object(), "fixture._plant_seed_over_lands"
        )
        outcome_wrapped, outcome_changed = namespace["_wrap_planting_outcome_verify_func"](
            crop_wrapped, "fixture._plant_seed_over_lands"
        )
        crop_rewrapped, crop_rechanged = namespace["_wrap_planting_crop_context_func"](
            outcome_wrapped, object(), "fixture._plant_seed_over_lands"
        )
        outcome_rewrapped, outcome_rechanged = namespace["_wrap_planting_outcome_verify_func"](
            crop_rewrapped, "fixture._plant_seed_over_lands"
        )

        self.assertTrue(crop_changed)
        self.assertTrue(outcome_changed)
        self.assertFalse(crop_rechanged)
        self.assertFalse(outcome_rechanged)
        self.assertIs(outcome_wrapped, crop_rewrapped)
        self.assertIs(outcome_wrapped, outcome_rewrapped)

    def test_fertilizer_drag_logs_are_relabelled_as_fertilizing(self):
        namespace = load_functions("_rewrite_fertilizer_execution_log_message")
        namespace["_ACTIVE_RUN_CYCLE_CONTEXT"] = types.SimpleNamespace(
            _qqfarm_planting_crop_context="\u666e\u901a\u5316\u80a5"
        )

        message, changed = namespace[
            "_rewrite_fertilizer_execution_log_message"
        ]("\u2714 \u5df2\u5b8c\u6210\u64ad\u79cd\uff1a\u666e\u901a\u5316\u80a5 x 7")

        self.assertTrue(changed)
        self.assertIn("\u5df2\u5b8c\u6210\u65bd\u80a5", message)
        self.assertNotIn("\u5df2\u5b8c\u6210\u64ad\u79cd", message)

    def test_drag_planting_wires_visual_outcome_verification(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("elif n == '_plant_seed_over_lands':", source)
        self.assertIn("elif n == '_execute_planting_by_mode':", source)
        self.assertIn(
            "new, outcome_ok = _wrap_planting_outcome_verify_func(",
            source,
        )

    def test_drag_planting_wires_crop_context_into_radish_fertilizer(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("elif n == '_execute_planting_by_mode':", source)
        self.assertIn(
            "_wrap_planting_crop_context_func(old, m, prefix + '.' + n)",
            source,
        )

    def test_friend_home_button_accepts_stable_low_edge_match_with_carousel(self):
        namespace = load_functions("_friend_guard_friend_ui_state")
        namespace.update({
            "_FRIEND_HOME_TEMPLATE_PATH": "fixture-home.png",
            "_friend_guard_match_template": (
                lambda *_args, **_kwargs: {
                    "matched": False,
                    "gray": 0.7835,
                    "edge": 0.1685,
                    "center": (394, 606),
                }
            ),
            "_friend_selected_carousel_card_bounds": (
                lambda _frame: {"left": 221, "right": 317}
            ),
        })

        self.assertTrue(namespace["_friend_guard_friend_ui_state"](object()))

    def test_runtime_recovery_settings_are_not_mutated(self):
        namespace = load_functions("_qqfarm_cap_runtime_recovery_waits")
        bot = types.SimpleNamespace(
            restart_pause_seconds=60,
            reconnect_pause_seconds=300.0,
            go_restart_pause_seconds=300,
            enable_rest_window=True,
            enable_periodic_restart=True,
        )

        changed = namespace["_qqfarm_cap_runtime_recovery_waits"](bot)

        self.assertEqual(0, changed)
        self.assertEqual(60, bot.restart_pause_seconds)
        self.assertEqual(300.0, bot.reconnect_pause_seconds)
        self.assertEqual(300, bot.go_restart_pause_seconds)
        self.assertTrue(bot.enable_rest_window)
        self.assertTrue(bot.enable_periodic_restart)

    def test_configured_friend_pause_window_is_respected(self):
        namespace = load_functions("_friend_pause_reason_now")
        namespace.update({
            "_active_instance_id": lambda: "1",
            "_truthy": lambda value: str(value).lower() == "true",
            "_cfg_get": lambda sections, key, default="": (
                "True" if key == "enable_rest_window" else "03:00-05:00"
            ),
            "_time_in_window_spec": lambda _spec: True,
            "_write": lambda _message: None,
        })

        self.assertEqual(
            "rest_window=03:00-05:00",
            namespace["_friend_pause_reason_now"](),
        )

    def test_player_level_first_call_probes_live_ocr_and_updates_strategy_level(self):
        namespace = load_functions("_wrap_player_level_fast")
        logs = []
        native_calls = []
        namespace.update({
            "_configured_player_level": lambda default=120: 120,
            "_qqfarm_configured_player_level_floor": lambda default=120: 120,
            "_write": lambda message: logs.append(message),
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: native_calls.append(True) or 121,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _last_player_level_detected=120,
            planting_player_level=40,
        )

        self.assertTrue(changed)
        self.assertEqual(121, wrapped(bot))
        self.assertEqual([True], native_calls)
        self.assertEqual(121, bot._qqfarm_player_level_cache_value)
        self.assertEqual(121, bot._last_player_level_detected)
        self.assertEqual(121, bot.planting_player_level)

    def test_player_level_uses_live_ocr_even_when_configured_value_is_higher(self):
        namespace = load_functions("_wrap_player_level_fast")
        logs = []
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda message: logs.append(message),
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 121,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_next_probe_ts=0.0,
            _qqfarm_player_level_cache_value=125,
            _last_player_level_detected=125,
            planting_player_level=125,
        )

        self.assertTrue(changed)
        self.assertEqual(121, wrapped(bot))
        self.assertEqual(121, bot.planting_player_level)
        self.assertEqual("live-ocr", bot._last_player_level_detect_source)
        self.assertTrue(any("source=live-ocr" in message for message in logs))

    def test_player_level_disables_native_config_fallback_before_ocr_probe(self):
        namespace = load_functions("_wrap_player_level_fast")
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda _message: None,
        })
        calls = []

        def native(bot, game_frame=None, fallback_to_config=True):
            calls.append((bot, game_frame, fallback_to_config))
            return 121

        wrapped, changed = namespace["_wrap_player_level_fast"](
            native, "fixture.get_current_player_level"
        )
        bot = types.SimpleNamespace(_qqfarm_player_level_next_probe_ts=0.0)

        self.assertTrue(changed)
        self.assertEqual(121, wrapped(bot, object(), True))
        self.assertEqual(1, len(calls))
        self.assertFalse(calls[0][2])

    def test_player_level_uses_recent_trusted_value_when_ocr_is_invalid(self):
        namespace = load_functions("_wrap_player_level_fast")
        logs = []
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda message: logs.append(message),
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 0,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_next_probe_ts=0.0,
            _qqfarm_player_level_trusted_value=121,
            _qqfarm_player_level_trusted_ts=time.time(),
            _last_player_level_detected=0,
            planting_player_level=0,
        )

        self.assertTrue(changed)
        self.assertEqual(121, wrapped(bot))
        self.assertEqual(121, bot.planting_player_level)
        self.assertEqual("trusted-level-cache", bot._last_player_level_detect_source)
        self.assertTrue(any("source=trusted-level-cache" in message for message in logs))

    def test_player_level_rejects_stale_trusted_cache_when_live_ocr_is_invalid(self):
        namespace = load_functions("_wrap_player_level_fast")
        logs = []
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda message: logs.append(message),
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 0,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_next_probe_ts=0.0,
            _qqfarm_player_level_trusted_value=121,
            _qqfarm_player_level_trusted_ts=time.time() - 301.0,
            _last_player_level_detected=121,
            planting_player_level=121,
        )

        self.assertTrue(changed)
        self.assertEqual(0, wrapped(bot))
        self.assertTrue(bot._qqfarm_player_level_dynamic_pending)
        self.assertEqual("live-ocr-unavailable", bot._last_player_level_detect_source)
        self.assertTrue(any("source=live-ocr-unavailable" in message for message in logs))

    def test_dynamic_level_pending_runs_backpack_only_crop_flow_and_blocks_buy(self):
        namespace = load_functions("_wrap_planting_flow_fast")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        calls = []

        def native(owner, frame, crop_name, allow_buy, **kwargs):
            calls.append((
                owner,
                frame,
                crop_name,
                allow_buy,
                getattr(owner, "_qqfarm_block_level_based_shop", False),
                kwargs,
            ))
            return True

        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native, "fixture._run_planting_flow"
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_dynamic_pending=True,
            _last_player_level_detect_source="live-ocr-unavailable",
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "frame", "\u91d1\u82b1\u8336", True))
        self.assertEqual(1, len(calls))
        self.assertEqual("\u91d1\u82b1\u8336", calls[0][2])
        self.assertFalse(calls[0][3])
        self.assertTrue(calls[0][4])
        self.assertFalse(hasattr(bot, "_qqfarm_block_level_based_shop"))
        self.assertTrue(any("backpack-only" in message for message in logs))

    def test_dynamic_level_pending_seed_shop_is_never_called(self):
        namespace = load_functions("_wrap_buy_seed_for_crop_backpack_guard")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        calls = []

        def native(owner, crop_name):
            calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_dynamic_pending=True,
            _qqfarm_recent_empty_land_count=4,
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "\u91d1\u82b1\u8336"))
        self.assertEqual([], calls)
        self.assertEqual(1, bot.planting_buy_retry_no_buy_quota)
        self.assertTrue(any("live player level unavailable" in message for message in logs))

    def test_player_level_does_not_force_config_when_live_ocr_is_unavailable(self):
        namespace = load_functions("_wrap_player_level_fast")
        logs = []
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda message: logs.append(message),
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 0,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _qqfarm_player_level_next_probe_ts=0.0,
            _last_player_level_detected=0,
            planting_player_level=40,
        )

        self.assertTrue(changed)
        self.assertEqual(0, wrapped(bot))
        self.assertEqual(40, bot.planting_player_level)
        self.assertEqual("live-ocr-unavailable", bot._last_player_level_detect_source)
        self.assertTrue(bot._qqfarm_player_level_dynamic_pending)
        self.assertTrue(any("source=live-ocr-unavailable" in message for message in logs))

    def test_home_priority_is_wired_into_friend_and_cycle_dispatch(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("_run_home_priority_self_pass", source)
        self.assertIn("v231 blocked friend route while home empty-land priority is active", source)
        self.assertIn("v231 home-priority self pass", source)


    def test_fresh_backpack_candidates_block_repeated_non_target_shop_fallbacks(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        now = time.time()
        bot = types.SimpleNamespace(
            _qqfarm_backpack_candidates_seen_ts=now,
            _qqfarm_backpack_candidate_centers=[(68, 512), (204, 512)],
            _qqfarm_recent_empty_land_count=20,
            _qqfarm_recent_empty_land_ts=now,
            _qqfarm_recent_empty_lands=[
                {"center": (index * 10, 100)} for index in range(20)
            ],
        )
        shop_calls = []

        def native(owner, crop_name):
            shop_calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "\u5929\u5c71\u96ea\u83b2"))
        self.assertFalse(wrapped(bot, "\u5929\u5c71\u96ea\u83b2"))
        self.assertEqual([], shop_calls)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
        self.assertTrue(any("backpack" in message for message in logs))

    def test_empty_land_state_holds_fresh_multi_land_snapshot_across_one_tiny_read(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        observations = [
            [{"center": (index * 10, 100)} for index in range(19)],
            [{"center": (10, 100)}],
            [{"center": (10, 100)}],
        ]

        def native(_bot, _frame=None):
            return observations.pop(0)

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            native, "fixture._detect_empty_lands"
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(19, bot._qqfarm_recent_empty_land_count)
        self.assertEqual(1, len(wrapped(bot, object())))
        self.assertEqual(1, bot._qqfarm_recent_empty_land_count)
        self.assertTrue(any("unstable" in message for message in logs))

    def test_empty_land_state_requires_two_matching_medium_undercounts_before_accepting_drop(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        observations = [
            [{"center": (index * 10, 100)} for index in range(19)],
            [{"center": (index * 10, 100)} for index in range(14)],
            [{"center": (index * 10, 100)} for index in range(14)],
        ]

        def native(_bot, _frame=None):
            return observations.pop(0)

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            native, "fixture._detect_empty_lands"
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(14, len(wrapped(bot, object())))
        self.assertEqual(14, bot._qqfarm_recent_empty_land_count)

    def test_empty_land_state_accepts_confirmed_medium_undercount_when_centers_jitter_slightly(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        namespace["_write"] = lambda _message: None
        observations = [
            [{"center": (index * 20, 100)} for index in range(19)],
            [{"center": (index * 20, 100)} for index in range(14)],
            [{"center": (index * 20 + 3, 102)} for index in range(14)],
        ]

        def native(_bot, _frame=None):
            return observations.pop(0)

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            native, "fixture._detect_empty_lands"
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(14, len(wrapped(bot, object())))
        self.assertEqual(14, bot._qqfarm_recent_empty_land_count)

    def test_empty_land_state_discards_single_medium_undercount_when_next_frame_recovers(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        namespace["_write"] = lambda _message: None
        observations = [
            [{"center": (index * 10, 100)} for index in range(19)],
            [{"center": (index * 10, 100)} for index in range(14)],
            [{"center": (index * 10, 100)} for index in range(20)],
        ]

        def native(_bot, _frame=None):
            return observations.pop(0)

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            native, "fixture._detect_empty_lands"
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(19, len(wrapped(bot, object())))
        self.assertEqual(20, len(wrapped(bot, object())))
        self.assertEqual(20, bot._qqfarm_recent_empty_land_count)

    def test_backpack_result_with_no_stable_empty_land_drop_is_not_reported_as_success(self):
        namespace = load_functions("_wrap_backpack_seed_priority_planting_fast")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        lands = [{"center": (index * 10, 100)} for index in range(19)]

        def native(owner, remain_lands, panel_settle):
            owner._qqfarm_recent_empty_land_count = 20
            owner._qqfarm_recent_empty_lands = [
                {"center": (index * 10, 100)} for index in range(20)
            ]
            return True, [], False, None, True

        wrapped, changed = namespace["_wrap_backpack_seed_priority_planting_fast"](
            native, "fixture._run_backpack_seed_priority_planting"
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=19,
            _qqfarm_recent_empty_lands=list(lands),
        )

        self.assertTrue(changed)
        result = wrapped(bot, lands, 0.2)
        self.assertFalse(result[0])
        self.assertFalse(bot._qqfarm_backpack_last_attempt_progress)
        self.assertTrue(any("no stable empty-land decrease" in message for message in logs))

    def test_no_visual_progress_invalidates_the_backpack_snapshot_before_shop_fallback(self):
        """A click that leaves every plot empty must not keep a 15-minute inventory latch alive."""
        namespace = load_functions("_wrap_backpack_seed_priority_planting_fast")
        namespace["_write"] = lambda _message: None
        lands = [{"center": (index * 10, 100)} for index in range(4)]
        seen_ts = time.time()

        def native(owner, remain_lands, panel_settle):
            owner._qqfarm_recent_empty_land_count = len(remain_lands)
            owner._qqfarm_recent_empty_land_ts = time.time()
            return True, list(remain_lands)

        wrapped, changed = namespace["_wrap_backpack_seed_priority_planting_fast"](
            native, "fixture._run_backpack_seed_priority_planting"
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=len(lands),
            _qqfarm_recent_empty_lands=list(lands),
            _qqfarm_backpack_candidates_seen_ts=seen_ts,
            _qqfarm_backpack_candidate_centers=[(68, 512), (204, 512)],
        )

        self.assertTrue(changed)
        result = wrapped(bot, lands, 0.2)
        self.assertFalse(result[0])
        self.assertEqual(seen_ts, bot._qqfarm_backpack_candidates_exhausted_seen_ts)
        self.assertEqual(0.0, bot._qqfarm_backpack_candidates_seen_ts)
        self.assertEqual([], bot._qqfarm_backpack_candidate_centers)

    def test_empty_rescan_snapshot_allows_bounded_shop_fallback(self):
        """After a fresh scan confirms no ordinary seed remains, buying is no longer blocked."""
        namespace = load_functions("_wrap_buy_seed_for_crop_backpack_guard")
        namespace["_write"] = lambda _message: None
        now = time.time()
        calls = []

        def native(owner, crop_name):
            calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        bot = types.SimpleNamespace(
            _qqfarm_backpack_candidates_seen_ts=now,
            _qqfarm_backpack_candidate_centers=[],
            _qqfarm_backpack_candidates_exhausted_seen_ts=now,
            _qqfarm_backpack_candidates_exhausted_ts=now,
            _qqfarm_recent_empty_land_count=4,
            _qqfarm_recent_empty_lands=list(range(4)),
            _qqfarm_recent_empty_land_ts=now,
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, "???"))
        self.assertEqual([(bot, "???")], calls)

    def test_fresh_badge_scan_replaces_an_exhausted_backpack_snapshot(self):
        """A new visible ordinary-seed badge must clear the prior failed-snapshot marker."""
        namespace = load_functions("_wrap_seed_quantity_badges_fast")
        namespace["_write"] = lambda _message: None
        namespace["_seed_panel_strip_visible"] = lambda _frame: True
        namespace["_fast_seed_badge_candidates_from_frame"] = lambda _frame, capacity_hint=None: [
            {"center": (204, 512), "count": 4, "score": 0.95},
        ]
        wrapped, changed = namespace["_wrap_seed_quantity_badges_fast"](
            lambda _bot, _frame: [], "fixture._detect_seed_quantity_badges_by_ocr"
        )
        bot = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_recent_empty_land_count=4,
            _qqfarm_backpack_candidates_exhausted_seen_ts=time.time() - 1.0,
            _qqfarm_backpack_candidates_exhausted_ts=time.time() - 1.0,
        )

        self.assertTrue(changed)
        self.assertEqual([(204, 512)], [item["center"] for item in wrapped(bot, object())])
        self.assertEqual(0.0, bot._qqfarm_backpack_candidates_exhausted_seen_ts)
        self.assertEqual(0.0, bot._qqfarm_backpack_candidates_exhausted_ts)

    def test_visible_seed_hint_replaces_an_exhausted_backpack_snapshot(self):
        """The no-seed OCR guard must refresh stale failure state when badges are visible."""
        namespace = load_functions("_wrap_backpack_no_seed_hint_fast")
        namespace["_write"] = lambda _message: None
        namespace["_seed_panel_strip_visible"] = lambda _frame: True
        namespace["_fast_seed_badge_candidates_from_frame"] = lambda _frame, capacity_hint=None: [
            {"center": (204, 512), "count": 4, "score": 0.95},
        ]
        wrapped, changed = namespace["_wrap_backpack_no_seed_hint_fast"](
            lambda _bot, _frame: (True, "native-no-seed", 0.0),
            "fixture._detect_no_seed_hint_by_ocr",
        )
        bot = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_recent_empty_land_count=4,
            _qqfarm_backpack_candidates_exhausted_seen_ts=time.time() - 1.0,
            _qqfarm_backpack_candidates_exhausted_ts=time.time() - 1.0,
        )

        self.assertTrue(changed)
        self.assertEqual((False, "hook-visible-seed-inventory", 1.0), wrapped(bot, object()))
        self.assertEqual([(204, 512)], bot._qqfarm_backpack_candidate_centers)
        self.assertEqual(0.0, bot._qqfarm_backpack_candidates_exhausted_seen_ts)
        self.assertEqual(0.0, bot._qqfarm_backpack_candidates_exhausted_ts)

    def test_failed_2x2_seed_is_removed_from_the_next_backpack_candidate_pass(self):
        namespace = load_functions(
            "_wrap_quad_act_seed_transaction",
            "_wrap_seed_quantity_badges_fast",
        )
        namespace["_write"] = lambda _message: None
        namespace["_friend_guard_sleep"] = lambda _seconds: None
        namespace["_seed_panel_strip_visible"] = lambda _frame: True
        namespace["_fast_seed_badge_candidates_from_frame"] = lambda _frame, capacity_hint=None: [
            {"center": (68, 512), "count": 1, "score": 0.9},
            {"center": (204, 512), "count": 1, "score": 0.8},
        ]

        def quad_native(_bot, *, remain_lands, panel_settle, seed_center):
            return False, list(remain_lands)

        wrapped_quad, quad_changed = namespace["_wrap_quad_act_seed_transaction"](
            quad_native, "fixture._try_plant_quad_act_seeds"
        )
        bot = types.SimpleNamespace(
            act_seeds_frame_threshold=0.72,
            _qqfarm_backpack_profile_active=True,
        )
        lands = [{"center": (index * 10, 100)} for index in range(8)]
        wrapped_quad(
            bot,
            remain_lands=lands,
            panel_settle=0.2,
            seed_center=(68, 512),
        )

        wrapped_badges, badges_changed = namespace["_wrap_seed_quantity_badges_fast"](
            lambda _bot, _frame: [], "fixture._detect_seed_quantity_badges_by_ocr"
        )
        candidates = wrapped_badges(bot, object())

        self.assertTrue(quad_changed)
        self.assertTrue(badges_changed)
        self.assertEqual([(204, 512)], [item["center"] for item in candidates])
        self.assertEqual([(204, 512)], bot._qqfarm_backpack_candidate_centers)


    def test_failed_seed_shop_target_is_cooled_down_before_repeating_long_scan(self):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        calls = []

        def native(owner, crop_name):
            calls.append((owner, crop_name))
            return False

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        bot = types.SimpleNamespace(_qqfarm_recent_empty_land_count=19)

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "????"))
        self.assertFalse(wrapped(bot, "????"))
        self.assertEqual([(bot, "????")], calls)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
        self.assertTrue(any("failed seed shop cooldown" in message for message in logs))

    def test_empty_land_state_retains_native_candidates_when_crop_cover_is_only_evidence(self):
        """Green pixels around a template hit must not erase real home empty lands."""
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_detect_empty_lands_state",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        namespace["_empty_land_candidate_has_crop_cover"] = (
            lambda _frame, _center: True
        )
        lands = [
            {"center": (98, 499)},
            {"center": (185, 452)},
            {"center": (243, 422)},
            {"center": (331, 467)},
        ]

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _bot, _frame=None: list(lands),
            "fixture._detect_empty_lands",
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(lands, wrapped(bot, object()))
        self.assertEqual(lands, wrapped(bot, object()))
        self.assertEqual(4, bot._qqfarm_recent_empty_land_count)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
        self.assertEqual(
            [(98, 499), (185, 452), (243, 422), (331, 467)],
            sorted(bot._qqfarm_recent_empty_land_rejected_centers),
        )
        self.assertTrue(any("crop-cover" in message for message in logs))


    def test_true_purple_empty_tiles_adjacent_to_foliage_are_kept(self):
        """Neighboring foliage must not turn true purple empty tiles into a full farm."""
        fixture = ROOT / "tests" / "fixtures" / "empty_land_true_purple_adjacent_foliage.png"
        rgb = np.array(Image.open(fixture).convert("RGB"))
        frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        centers = [(203, 82), (145, 112), (291, 127), (58, 160)]
        lands = [{"center": center} for center in centers]
        namespace = load_functions(
            "_empty_land_candidate_has_crop_cover",
            "_empty_land_candidate_crop_cover_evidence",
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_detect_empty_lands_state",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)

        evidence = [
            namespace["_empty_land_candidate_crop_cover_evidence"](frame, center)
            for center in centers
        ]
        self.assertNotIn("strong", evidence)

        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _bot, _frame=None: list(lands),
            "fixture._detect_empty_lands",
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(lands, wrapped(bot, frame))
        self.assertEqual(4, bot._qqfarm_recent_empty_land_count)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
        self.assertFalse(bot._qqfarm_empty_land_scene_confirmed_full)
        self.assertFalse(any("strong crop-covered candidates cleared" in message for message in logs))


    def test_strong_crop_cover_clears_all_false_empty_candidates_without_stale_hold(self):
        """A full crop canopy must not be retained as a planting target."""
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_wrap_detect_empty_lands_state",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        namespace["_empty_land_candidate_has_crop_cover"] = (
            lambda _frame, _center: True
        )
        namespace["_empty_land_candidate_crop_cover_evidence"] = (
            lambda _frame, _center: "strong"
        )
        lands = [
            {"center": (98, 499)},
            {"center": (185, 452)},
            {"center": (243, 422)},
            {"center": (331, 467)},
        ]
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _bot, _frame=None: list(lands),
            "fixture._detect_empty_lands",
        )
        bot = types.SimpleNamespace(
            _qqfarm_stable_empty_lands=list(lands),
            _qqfarm_stable_empty_land_count=4,
            _qqfarm_stable_empty_land_ts=time.time(),
        )

        self.assertTrue(changed)
        self.assertEqual([], wrapped(bot, object()))
        self.assertEqual(0, bot._qqfarm_recent_empty_land_count)
        self.assertEqual([], bot._qqfarm_stable_empty_lands)
        self.assertFalse(namespace["_qqfarm_home_priority_active"](bot))
        self.assertTrue(bot._qqfarm_empty_land_scene_confirmed_full)
        self.assertTrue(any("strong crop-covered" in message for message in logs))
        self.assertFalse(any("v249" in message for message in logs))

    def test_quad_seed_without_a_local_group_skips_the_special_click(self):
        """Scattered empty plots must fall through to ordinary backpack seeds."""
        namespace = load_functions("_wrap_quad_act_seed_transaction")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        namespace["_qqfarm_find_all_quad_empty_land_groups"] = lambda _lands: []
        calls = []
        lands = [
            {"center": (10, 10)},
            {"center": (90, 20)},
            {"center": (20, 100)},
            {"center": (140, 110)},
        ]

        def native(*_args, **_kwargs):
            calls.append(True)
            return False, list(lands)

        wrapped, changed = namespace["_wrap_quad_act_seed_transaction"](
            native, "fixture._try_plant_quad_act_seeds"
        )
        bot = types.SimpleNamespace(act_seeds_frame_threshold=0.72)

        self.assertTrue(changed)
        self.assertEqual(
            (False, lands),
            wrapped(bot, remain_lands=lands, panel_settle=0.2, seed_center=(68, 512)),
        )
        self.assertEqual([], calls)
        self.assertTrue(bot._qqfarm_quad_skip_and_continue)
        self.assertTrue(any("no local 2x2" in message for message in logs))

    def test_scattered_2x2_seed_is_quarantined_before_the_normal_backpack_retry(self):
        """A special seed that has no valid local 2x2 group must not be retried as a normal seed."""
        namespace = load_functions("_wrap_quad_act_seed_transaction")
        namespace["_write"] = lambda _message: None
        namespace["_qqfarm_find_all_quad_empty_land_groups"] = lambda _lands: []
        calls = []
        lands = [
            {"center": (10, 10)},
            {"center": (90, 20)},
            {"center": (20, 100)},
            {"center": (140, 110)},
        ]

        def native(*_args, **_kwargs):
            calls.append(True)
            return False, list(lands)

        wrapped, changed = namespace["_wrap_quad_act_seed_transaction"](
            native, "fixture._try_plant_quad_act_seeds"
        )
        bot = types.SimpleNamespace(act_seeds_frame_threshold=0.72)

        self.assertTrue(changed)
        self.assertEqual(
            (False, lands),
            wrapped(
                bot,
                remain_lands=lands,
                panel_settle=0.2,
                seed_center=(68, 512),
            ),
        )
        self.assertEqual([], calls)
        skipped = getattr(bot, "_qqfarm_backpack_skip_candidate_until", {})
        self.assertIn((68, 512), skipped)
        self.assertGreater(float(skipped[(68, 512)]), time.time())

    def test_too_few_empty_lands_quarantines_the_2x2_seed_before_normal_seed_retry(self):
        """A 2x2-only seed must be skipped when there are fewer than four true empty plots."""
        namespace = load_functions("_wrap_quad_act_seed_transaction")
        namespace["_write"] = lambda _message: None
        calls = []
        lands = [
            {"center": (10, 10)},
            {"center": (90, 20)},
            {"center": (20, 100)},
        ]

        def native(*_args, **_kwargs):
            calls.append(True)
            return False, list(lands)

        wrapped, changed = namespace["_wrap_quad_act_seed_transaction"](
            native, "fixture._try_plant_quad_act_seeds"
        )
        bot = types.SimpleNamespace(act_seeds_frame_threshold=0.72)

        self.assertTrue(changed)
        self.assertEqual(
            (False, lands),
            wrapped(
                bot,
                remain_lands=lands,
                panel_settle=0.2,
                seed_center=(68, 512),
            ),
        )
        self.assertEqual([], calls)
        skipped = getattr(bot, "_qqfarm_backpack_skip_candidate_until", {})
        self.assertIn((68, 512), skipped)
        self.assertGreater(float(skipped[(68, 512)]), time.time())

    def test_seed_shop_is_deferred_after_strong_full_land_confirmation(self):
        """A stale planting branch must not buy a crop after the board is full."""
        namespace = load_functions("_wrap_buy_seed_for_crop_backpack_guard")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        calls = []

        def native(owner, crop_name):
            calls.append((owner, crop_name))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            native, "fixture._buy_seed_for_crop"
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_empty_land_scene_confirmed_full=True,
            _qqfarm_empty_land_scene_confirmed_full_ts=time.time(),
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, "???"))
        self.assertEqual([], calls)
        self.assertTrue(any("confirmed full-land frame" in message for message in logs))


if __name__ == "__main__":
    unittest.main()
