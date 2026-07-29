import ast
import time
import tempfile
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
            "播种面板种子数量OCR：白萝卜=8"
        )
        self.assertEqual(8, context._qqfarm_radish_inventory_qty)

        namespace["_qqfarm_update_home_priority"](
            context, 4, now_ts=100.0, reason="detected-empty"
        )
        namespace["_note_runtime_planting_outcome"](
            "✔ 已完成播种：白萝卜 x 4"
        )
        self.assertEqual(4, context._qqfarm_radish_inventory_qty)
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        self.assertTrue(context._qqfarm_force_self_cycle_next)

        namespace["_note_runtime_planting_outcome"]("家里已无可执行的任务")
        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        namespace["_note_runtime_planting_outcome"]("家里已无可执行的任务")
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

    def test_player_level_accepts_same_tens_config_floor_for_ocr_last_digit_miss(self):
        namespace = load_functions("_wrap_player_level_fast")
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda _message: None,
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 120,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _last_player_level_detected=121,
            planting_player_level=121,
        )

        self.assertTrue(changed)
        self.assertEqual(125, wrapped(bot))
        self.assertEqual(125, bot.planting_player_level)

    def test_player_level_accepts_same_decade_config_floor_for_digit_confusion(self):
        namespace = load_functions("_wrap_player_level_fast")
        namespace.update({
            "_configured_player_level": lambda default=120: 125,
            "_qqfarm_configured_player_level_floor": lambda default=120: 125,
            "_write": lambda _message: None,
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 121,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _last_player_level_detected=121,
            planting_player_level=121,
        )

        self.assertTrue(changed)
        self.assertEqual(125, wrapped(bot))
        self.assertEqual(125, bot.planting_player_level)

    def test_player_level_does_not_regress_below_active_configured_level(self):
        namespace = load_functions("_wrap_player_level_fast")
        namespace.update({
            "_configured_player_level": lambda default=120: 121,
            "_qqfarm_configured_player_level_floor": lambda default=120: 121,
            "_write": lambda _message: None,
        })
        wrapped, changed = namespace["_wrap_player_level_fast"](
            lambda _bot: 120,
            "fixture.get_current_player_level",
        )
        bot = types.SimpleNamespace(
            _last_player_level_detected=120,
            planting_player_level=40,
        )

        self.assertTrue(changed)
        self.assertEqual(121, wrapped(bot))
        self.assertEqual(121, bot.planting_player_level)

    def test_home_priority_is_wired_into_friend_and_cycle_dispatch(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("_run_home_priority_self_pass", source)
        self.assertIn("v231 blocked friend route while home empty-land priority is active", source)
        self.assertIn("v231 home-priority self pass", source)


if __name__ == "__main__":
    unittest.main()
