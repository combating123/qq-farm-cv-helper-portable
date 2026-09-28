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
    namespace = {"__file__": str(HOOK), "__name__": "v553_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class NativeEmptyClaimHardStop20260928Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(
            "_qqfarm_friend_route_expected",
            "_qqfarm_home_visual_recheck_step",
            "_qqfarm_native_empty_claim_requires_hard_stop",
            "_qqfarm_release_false_native_empty_claim",
            "_wrap_backpack_seed_priority_planting_fast",
        )
        self.logs = []
        self.namespace.update({
            "time": types.SimpleNamespace(time=lambda: 105.0),
            "_write": lambda message: self.logs.append(str(message)),
        })

    @staticmethod
    def false_claim_context(**overrides):
        values = {
            "_qqfarm_native_empty_log_claim_pending": True,
            "_qqfarm_native_empty_log_claim_count": 22,
            "_qqfarm_native_empty_log_claim_ts": 100.0,
            "_qqfarm_recent_empty_land_count": 0,
            "_qqfarm_recent_empty_lands": [],
            "_qqfarm_recent_empty_land_centers": [],
            "_qqfarm_recent_empty_land_ts": 104.0,
            "_qqfarm_empty_land_board_gate_state": "unknown",
            "_qqfarm_empty_land_board_gate_ts": 104.0,
            "_qqfarm_empty_land_scene_confirmed_full": False,
            "_qqfarm_empty_land_scene_confirmed_full_ts": 0.0,
            "_qqfarm_post_harvest_pending": False,
            "_qqfarm_single_harvest_planting_pending": False,
            "_qqfarm_home_empty_land_pending": True,
            "_qqfarm_home_empty_land_remaining": 22,
            "_qqfarm_force_self_cycle_next": True,
            "_qqfarm_cycle_branch_hint": "self",
            "_qqfarm_backpack_inventory_scan_pending": True,
            "_qqfarm_inventory_empty_land_proof_pending": True,
            "_qqfarm_home_visual_recheck_required": True,
            "_qqfarm_home_visual_recheck_attempts": 0,
            "_qqfarm_home_visual_recheck_started_ts": 0.0,
            "_qqfarm_home_visual_recheck_max_attempts": 3,
            "_qqfarm_home_visual_recheck_timeout_seconds": 30.0,
            "_qqfarm_friend_list_visit_cursor": 4,
            "_qqfarm_friend_list_pending_cursor": 4,
            "_qqfarm_friend_list_resume_pending": True,
            "_qqfarm_friend_chain_pending": True,
            "_qqfarm_friend_chain_active": True,
            "_qqfarm_friend_action_ledger": {"friend-a": {"steal": True}},
            "_qqfarm_friend_help_daily_count": 7,
        }
        values.update(overrides)
        return types.SimpleNamespace(**values)

    def confirmed_full_context(self, **overrides):
        values = {
            "_qqfarm_empty_land_board_gate_state": "confirmed",
            "_qqfarm_empty_land_board_gate_ts": 104.0,
            "_qqfarm_empty_land_scene_confirmed_full": True,
            "_qqfarm_empty_land_scene_confirmed_full_ts": 104.0,
            "_qqfarm_home_visual_recheck_attempts": 2,
            "_qqfarm_home_visual_recheck_started_ts": 100.0,
        }
        values.update(overrides)
        return self.false_claim_context(**values)

    def test_claimed_22_with_confirmed_full_visual_zero_skips_native_backpack_and_releases_friend_route(self):
        """The production 22/0 conflict must make zero land, backpack, or shop calls."""
        bot = self.confirmed_full_context()
        events = []

        def native_backpack(owner, remain_lands, panel_settle=1.5):
            events.append(("native-backpack", len(remain_lands), panel_settle))
            owner.click_at_position(381, 661)
            owner.open_seed_shop()
            return False, list(remain_lands), False, None, False

        bot.click_at_position = lambda x, y: events.append(("land-click", x, y))
        bot.open_seed_shop = lambda: events.append(("seed-shop",))
        wrapped, changed = self.namespace[
            "_wrap_backpack_seed_priority_planting_fast"
        ](native_backpack, "native._run_backpack_seed_priority_planting")

        result = wrapped(bot, [{"center": (100 + index, 400)} for index in range(22)], 1.5)

        self.assertTrue(changed)
        self.assertEqual((False, [], False, None, False), result)
        self.assertEqual([], events)
        self.assertFalse(bot._qqfarm_native_empty_log_claim_pending)
        self.assertEqual(0, bot._qqfarm_home_empty_land_remaining)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("friend", bot._qqfarm_cycle_branch_hint)
        self.assertFalse(bot._qqfarm_backpack_inventory_scan_pending)
        self.assertFalse(bot._qqfarm_inventory_empty_land_proof_pending)
        self.assertFalse(bot._qqfarm_home_visual_recheck_required)
        self.assertEqual(0, bot._qqfarm_home_visual_recheck_attempts)
        self.assertEqual(0.0, bot._qqfarm_home_visual_recheck_started_ts)
        self.assertEqual(105.0, bot._qqfarm_false_native_empty_hard_stop_ts)
        self.assertTrue(self.namespace["_qqfarm_friend_route_expected"](bot))
        self.assertEqual(4, bot._qqfarm_friend_list_visit_cursor)
        self.assertEqual(4, bot._qqfarm_friend_list_pending_cursor)
        self.assertTrue(bot._qqfarm_friend_list_resume_pending)
        self.assertTrue(bot._qqfarm_friend_chain_pending)
        self.assertTrue(bot._qqfarm_friend_chain_active)
        self.assertEqual({"friend-a": {"steal": True}}, bot._qqfarm_friend_action_ledger)
        self.assertEqual(7, bot._qqfarm_friend_help_daily_count)
        self.assertTrue(any(
            "claimed=22" in line and "current=0" in line and "hard-stop" in line
            for line in self.logs
        ), self.logs)

    def test_unknown_visual_zero_blocks_actions_but_keeps_one_bounded_home_recheck(self):
        bot = self.false_claim_context()

        self.assertTrue(self.namespace[
            "_qqfarm_native_empty_claim_requires_hard_stop"
        ](bot, now_ts=105.0))
        self.assertTrue(self.namespace[
            "_qqfarm_release_false_native_empty_claim"
        ](bot, now_ts=105.0, reason="unknown-zero"))

        self.assertFalse(bot._qqfarm_native_empty_log_claim_pending)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)
        self.assertTrue(bot._qqfarm_home_visual_recheck_required)
        self.assertTrue(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)
        self.assertEqual(1, bot._qqfarm_home_visual_recheck_attempts)
        self.assertEqual(105.0, bot._qqfarm_home_visual_recheck_started_ts)
        self.assertEqual(4, bot._qqfarm_friend_list_visit_cursor)
        self.assertTrue(bot._qqfarm_friend_chain_active)

    def test_unknown_visual_zero_releases_friend_route_after_bounded_recheck_exhaustion(self):
        bot = self.false_claim_context(
            _qqfarm_home_visual_recheck_attempts=2,
            _qqfarm_home_visual_recheck_started_ts=100.0,
        )

        self.assertTrue(self.namespace[
            "_qqfarm_release_false_native_empty_claim"
        ](bot, now_ts=105.0, reason="unknown-zero-exhausted"))

        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertFalse(bot._qqfarm_home_visual_recheck_required)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("friend", bot._qqfarm_cycle_branch_hint)
        self.assertEqual(0, bot._qqfarm_home_visual_recheck_attempts)
        self.assertEqual(0.0, bot._qqfarm_home_visual_recheck_started_ts)
        self.assertTrue(self.namespace["_qqfarm_friend_route_expected"](bot))

    def test_fresh_confirmed_visual_empty_lands_keep_real_planting_eligible(self):
        bot = self.false_claim_context(
            _qqfarm_recent_empty_land_count=2,
            _qqfarm_recent_empty_lands=[
                {"center": (180, 420), "_qqfarm_visual_soil_proof": True},
                {"center": (220, 440), "_qqfarm_post_harvest_confirmed": True},
            ],
            _qqfarm_empty_land_board_gate_state="confirmed",
        )

        self.assertFalse(self.namespace[
            "_qqfarm_native_empty_claim_requires_hard_stop"
        ](bot, now_ts=105.0))

    def test_post_harvest_zero_still_blocks_native_candidates_but_preserves_harvest_state(self):
        pending_land = {
            "center": (180, 420),
            "_qqfarm_post_harvest_confirmed": True,
        }
        bot = self.false_claim_context(
            _qqfarm_post_harvest_pending=True,
            _qqfarm_single_harvest_planting_pending=True,
            planting_harvest_quota=2,
            _qqfarm_post_harvest_snapshot_locked=True,
            _qqfarm_post_harvest_pending_lands=[pending_land],
            _qqfarm_post_harvest_pending_centers=[(180, 420)],
            _qqfarm_post_harvest_rescan_remaining=2,
            _qqfarm_post_harvest_rescan_deadline_ts=120.0,
            _qqfarm_post_harvest_capture_frames=["frame-a"],
            _qqfarm_post_harvest_event_ts=100.0,
            _qqfarm_post_harvest_deadline_ts=120.0,
        )
        events = []

        def native_backpack(owner, remain_lands, panel_settle=1.5):
            events.append(("native-backpack", len(remain_lands)))
            return False, list(remain_lands), False, None, False

        wrapped, _changed = self.namespace[
            "_wrap_backpack_seed_priority_planting_fast"
        ](native_backpack, "native._run_backpack_seed_priority_planting")
        result = wrapped(bot, [{"center": (100 + index, 400)} for index in range(22)], 1.5)

        self.assertEqual((False, [], False, None, False), result)
        self.assertEqual([], events)
        self.assertTrue(bot._qqfarm_post_harvest_pending)
        self.assertTrue(bot._qqfarm_single_harvest_planting_pending)
        self.assertEqual(2, bot.planting_harvest_quota)
        self.assertTrue(bot._qqfarm_post_harvest_snapshot_locked)
        self.assertEqual([pending_land], bot._qqfarm_post_harvest_pending_lands)
        self.assertEqual([(180, 420)], bot._qqfarm_post_harvest_pending_centers)
        self.assertEqual(2, bot._qqfarm_post_harvest_rescan_remaining)
        self.assertEqual(["frame-a"], bot._qqfarm_post_harvest_capture_frames)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)

    def test_fixed_slot_transaction_zero_blocks_native_candidates_without_clearing_queue(self):
        pending_lands = [{
            "center": (180, 420),
            "slot_id": "L05",
            "_qqfarm_strict_ledger_verified": True,
            "_qqfarm_visual_soil_proof": True,
        }]
        pending_quads = (("L01", "L02", "L05", "L06"),)
        bot = self.false_claim_context(
            _qqfarm_strict_24slot_transaction_active=True,
            _qqfarm_fixed_slot_chain_active=True,
            _qqfarm_fixed_slot_pending_slot_ids=("L05",),
            _qqfarm_fixed_slot_pending_lands=pending_lands,
            _qqfarm_fixed_slot_pending_quad_groups=pending_quads,
        )

        self.assertTrue(self.namespace[
            "_qqfarm_native_empty_claim_requires_hard_stop"
        ](bot, now_ts=105.0))
        self.assertTrue(self.namespace[
            "_qqfarm_release_false_native_empty_claim"
        ](bot, now_ts=105.0, reason="fixed-slot-active"))

        self.assertTrue(bot._qqfarm_strict_24slot_transaction_active)
        self.assertTrue(bot._qqfarm_fixed_slot_chain_active)
        self.assertEqual(("L05",), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(pending_lands, bot._qqfarm_fixed_slot_pending_lands)
        self.assertEqual(pending_quads, bot._qqfarm_fixed_slot_pending_quad_groups)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)

    def test_unverified_fixed_slot_cache_does_not_hold_a_confirmed_full_board(self):
        bot = self.confirmed_full_context(
            _qqfarm_fixed_slot_chain_active=False,
            _qqfarm_fixed_slot_pending_slot_ids=(5,),
            _qqfarm_fixed_slot_pending_lands=[
                {"center": (180, 420), "slot_id": 5}
            ],
            _qqfarm_fixed_slot_pending_quad_groups=((1, 2, 5, 6),),
        )

        self.assertTrue(self.namespace[
            "_qqfarm_release_false_native_empty_claim"
        ](bot, now_ts=105.0, reason="stale-unverified-fixed-slot"))

        self.assertEqual((), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual([], bot._qqfarm_fixed_slot_pending_lands)
        self.assertEqual((), bot._qqfarm_fixed_slot_pending_quad_groups)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertEqual("friend", bot._qqfarm_cycle_branch_hint)


class NativeV237OverlayCoverage20260928Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(
            "_qqfarm_preserve_wrapper_metadata",
            "_qqfarm_home_visual_recheck_step",
            "_qqfarm_native_empty_claim_requires_hard_stop",
            "_qqfarm_release_false_native_empty_claim",
            "_wrap_detect_empty_lands_state",
            "_wrap_buy_seed_for_crop_backpack_guard",
            "_wrap_native_v225_crop_catalog_planting_flow",
            "_wrap_planting_flow_fast",
            "_wrap_backpack_seed_priority_planting_fast",
            "_wrap_native_false_empty_planting_action_guard",
            "_patch_native_v237_business_overlay_for_module",
        )
        self.logs = []
        self.namespace.update({
            "time": types.SimpleNamespace(time=lambda: 105.0, perf_counter=lambda: 105.0),
            "_write": lambda message: self.logs.append(str(message)),
            "_NATIVE_V237_OVERLAY_SEEN": set(),
        })

    @staticmethod
    def make_bot_class(events):
        class SyntheticFarmBot:
            def _detect_empty_lands(self, frame):
                events.append(("native-detector", frame))
                return [{"center": (100 + index, 400)} for index in range(22)]

            def _run_planting_flow(self, *args, **kwargs):
                events.append(("native-flow", args, kwargs))
                return "native-flow-result"

            def _run_backpack_seed_priority_planting(
                    self, remain_lands, panel_settle=1.5):
                events.append(("native-backpack", len(remain_lands)))
                return False, list(remain_lands), False, None, False

            def _execute_planting_by_mode(self, *args, **kwargs):
                events.append(("native-execute", args, kwargs))
                return True

            def _buy_seed_for_crop(self, *args, **kwargs):
                events.append(("native-shop", args, kwargs))
                return True

        return SyntheticFarmBot

    @staticmethod
    def prepare_confirmed_full(bot, **overrides):
        values = {
            "_qqfarm_native_empty_log_claim_pending": True,
            "_qqfarm_native_empty_log_claim_count": 22,
            "_qqfarm_native_empty_log_claim_ts": 100.0,
            "_qqfarm_recent_empty_land_count": 0,
            "_qqfarm_recent_empty_lands": [],
            "_qqfarm_recent_empty_land_centers": [],
            "_qqfarm_recent_empty_land_ts": 104.0,
            "_qqfarm_empty_land_board_gate_state": "confirmed",
            "_qqfarm_empty_land_board_gate_ts": 104.0,
            "_qqfarm_empty_land_scene_confirmed_full": True,
            "_qqfarm_empty_land_scene_confirmed_full_ts": 104.0,
            "_qqfarm_home_empty_land_pending": True,
            "_qqfarm_home_empty_land_remaining": 22,
            "_qqfarm_home_visual_recheck_required": True,
            "_qqfarm_home_visual_recheck_attempts": 1,
            "_qqfarm_home_visual_recheck_started_ts": 100.0,
            "_qqfarm_force_self_cycle_next": True,
            "_qqfarm_cycle_branch_hint": "self",
            "_qqfarm_backpack_inventory_scan_pending": True,
            "_qqfarm_inventory_empty_land_proof_pending": True,
            "_qqfarm_post_harvest_pending": False,
            "_qqfarm_single_harvest_planting_pending": False,
        }
        values.update(overrides)
        for name, value in values.items():
            setattr(bot, name, value)
        return bot

    def build_module(self, events):
        module = types.ModuleType("bot.synthetic_v237")
        module.FarmBot = self.make_bot_class(events)
        return module

    def test_overlay_installs_every_native_empty_land_and_planting_guard_once(self):
        events = []
        module = self.build_module(events)

        first_count = self.namespace[
            "_patch_native_v237_business_overlay_for_module"
        ](module, "red-overlay")
        second_count = self.namespace[
            "_patch_native_v237_business_overlay_for_module"
        ](module, "red-overlay-repeat")

        cls = module.FarmBot
        self.assertGreaterEqual(first_count, 5)
        self.assertEqual(0, second_count)
        self.assertTrue(getattr(
            cls._detect_empty_lands, "__qqfarm_empty_land_state_wrapped__", False
        ))
        self.assertTrue(getattr(
            cls._run_planting_flow,
            "__qqfarm_native_v225_crop_catalog_wrapped__",
            False,
        ))
        self.assertTrue(getattr(
            cls._run_planting_flow,
            "__qqfarm_planting_flow_fast_wrapped__",
            False,
        ))
        self.assertTrue(getattr(
            cls._run_backpack_seed_priority_planting,
            "__qqfarm_backpack_fast_wrapped__",
            False,
        ))
        self.assertTrue(getattr(
            cls._buy_seed_for_crop,
            "__qqfarm_backpack_buy_guard_wrapped__",
            False,
        ))
        self.assertTrue(getattr(
            cls._execute_planting_by_mode,
            "__qqfarm_native_false_empty_action_guard_wrapped__",
            False,
        ))

    def test_all_native_planting_branches_hard_stop_before_destructive_action(self):
        branch_overrides = {
            "backpack_no_seed": {
                "backpack_seed_priority": True,
                "_qqfarm_backpack_inventory_scan_pending": False,
            },
            "backpack_remaining": {
                "backpack_seed_priority": True,
                "_qqfarm_backpack_inventory_scan_pending": True,
            },
            "daily_radish": {
                "backpack_seed_priority": True,
                "enable_daily_radish_exp": True,
            },
            "backpack_disabled": {
                "backpack_seed_priority": False,
            },
        }
        for label, overrides in branch_overrides.items():
            with self.subTest(label=label):
                events = []
                module = self.build_module(events)
                self.namespace[
                    "_patch_native_v237_business_overlay_for_module"
                ](module, label)
                bot = self.prepare_confirmed_full(module.FarmBot(), **overrides)

                result = bot._run_planting_flow(
                    object(), "似血杜鹃", True, False, [], False
                )

                self.assertFalse(result)
                self.assertEqual([], events)
                self.assertFalse(bot._qqfarm_native_empty_log_claim_pending)
                self.assertEqual("friend", bot._qqfarm_cycle_branch_hint)
                self.assertFalse(bot._qqfarm_home_empty_land_pending)

    def test_execute_backpack_and_shop_entry_points_share_the_same_hard_stop(self):
        events = []
        module = self.build_module(events)
        self.namespace[
            "_patch_native_v237_business_overlay_for_module"
        ](module, "all-entry-points")

        execute_bot = self.prepare_confirmed_full(module.FarmBot())
        self.assertFalse(execute_bot._execute_planting_by_mode(
            "似血杜鹃", [{"center": (100, 400)}]
        ))

        backpack_bot = self.prepare_confirmed_full(module.FarmBot())
        self.assertEqual(
            (False, [], False, None, False),
            backpack_bot._run_backpack_seed_priority_planting(
                [{"center": (100, 400)}], 1.5
            ),
        )

        shop_bot = self.prepare_confirmed_full(module.FarmBot())
        self.assertFalse(shop_bot._buy_seed_for_crop("似血杜鹃", 1))

        self.assertEqual([], events)
        self.assertEqual("friend", execute_bot._qqfarm_cycle_branch_hint)
        self.assertEqual("friend", backpack_bot._qqfarm_cycle_branch_hint)
        self.assertEqual("friend", shop_bot._qqfarm_cycle_branch_hint)


if __name__ == "__main__":
    unittest.main()
