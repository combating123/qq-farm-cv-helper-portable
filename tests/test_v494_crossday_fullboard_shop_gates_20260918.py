import ast
import json
import tempfile
import time
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FULL_BOARD_FIXTURE = ROOT / "tests" / "fixtures" / "full-planted-home-20260801.png"
V494_FULL_BOARD_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "live-v494-full-board-seedlings-sanitized-20260918.png"
)


def load_functions(*wanted):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(wanted)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "np": np, "cv2": cv2}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V494CrossdayFriendReset20260918Tests(unittest.TestCase):
    def test_yesterday_terminal_journal_wins_over_runtime_marker_already_set_to_today(self):
        namespace = load_functions(
            "_friend_progress_journal_rearm_for_business_date"
        )
        commits = []
        logs = []
        namespace.update(
            {
                "_friend_progress_journal_record": (
                    lambda owner, today=None: commits.append(
                        {
                            "today": today,
                            "cursor": owner._qqfarm_friend_list_visit_cursor,
                            "phase": owner._qqfarm_friend_progress_journal_phase,
                        }
                    ) or True
                ),
                "_write": lambda message: logs.append(message),
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_pending_cursor=5,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_guard_empty_latched=True,
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_progress_journal_business_date="2026-09-19",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            journal = Path(tmpdir) / "friend_traversal_journal.json"
            journal.write_text(
                json.dumps(
                    {
                        "business_date": "2026-09-18",
                        "phase": "terminal",
                        "cursor": 5,
                    }
                ),
                encoding="utf-8",
            )
            result = namespace[
                "_friend_progress_journal_rearm_for_business_date"
            ](
                context,
                today="2026-09-19",
                journal_path=str(journal),
            )

        self.assertTrue(result)
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(0, context._qqfarm_friend_list_pending_cursor)
        self.assertFalse(context._qqfarm_friend_chain_exhausted)
        self.assertEqual("active", context._qqfarm_friend_progress_journal_phase)
        self.assertEqual(
            [{"today": "2026-09-19", "cursor": 0, "phase": "active"}],
            commits,
        )
        self.assertTrue(any("old=2026-09-18" in message for message in logs))

    def test_actual_crossday_rearm_resets_terminal_cursor_and_records_today(self):
        namespace = load_functions(
            "_friend_progress_journal_rearm_for_business_date"
        )
        commits = []
        logs = []
        namespace.update(
            {
                "_daily_business_date": lambda: "2026-09-18",
                "_friend_progress_journal_record": (
                    lambda owner, today=None: commits.append(
                        {
                            "today": today,
                            "cursor": owner._qqfarm_friend_list_visit_cursor,
                            "phase": owner._qqfarm_friend_progress_journal_phase,
                        }
                    ) or True
                ),
                "_write": lambda message: logs.append(message),
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_pending_cursor=5,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_guard_empty_latched=True,
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_progress_journal_business_date="2026-09-17",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            journal = Path(tmpdir) / "friend_traversal_journal.json"
            journal.write_text(
                json.dumps(
                    {
                        "business_date": "2026-09-17",
                        "phase": "terminal",
                        "cursor": 5,
                    }
                ),
                encoding="utf-8",
            )
            result = namespace[
                "_friend_progress_journal_rearm_for_business_date"
            ](
                context,
                today="2026-09-18",
                journal_path=str(journal),
            )

        self.assertTrue(result)
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(0, context._qqfarm_friend_list_pending_cursor)
        self.assertFalse(context._qqfarm_friend_chain_pending)
        self.assertFalse(context._qqfarm_friend_chain_active)
        self.assertFalse(context._qqfarm_friend_chain_exhausted)
        self.assertFalse(context._qqfarm_friend_chain_allow_home)
        self.assertFalse(context._qqfarm_friend_guard_empty_latched)
        self.assertEqual("active", context._qqfarm_friend_progress_journal_phase)
        self.assertEqual(
            "2026-09-18",
            context._qqfarm_friend_progress_journal_business_date,
        )
        self.assertEqual(
            [{"today": "2026-09-18", "cursor": 0, "phase": "active"}],
            commits,
        )
        self.assertTrue(any("cross-day reset" in message for message in logs))

    def test_same_day_terminal_friend_journal_is_not_replayed(self):
        namespace = load_functions(
            "_friend_progress_journal_rearm_for_business_date"
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_progress_journal_business_date="2026-09-18",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            journal = Path(tmpdir) / "friend_traversal_journal.json"
            journal.write_text(
                json.dumps(
                    {
                        "business_date": "2026-09-18",
                        "phase": "terminal",
                        "cursor": 5,
                    }
                ),
                encoding="utf-8",
            )
            result = namespace[
                "_friend_progress_journal_rearm_for_business_date"
            ](
                context,
                today="2026-09-18",
                journal_path=str(journal),
            )

        self.assertFalse(result)
        self.assertEqual(5, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(context._qqfarm_friend_chain_exhausted)
        self.assertEqual("terminal", context._qqfarm_friend_progress_journal_phase)

    def test_new_business_day_rearms_terminal_friend_list_before_first_row(self):
        namespace = load_functions("_handle_friend_list_surface")
        rows = [
            {
                "center": (365, 289 + (94 * index)),
                "rect": (331, 271 + (94 * index), 399, 307 + (94 * index)),
            }
            for index in range(5)
        ]
        clicks = []
        rearm_calls = []

        def rearm(owner, today=None):
            rearm_calls.append(today)
            owner._qqfarm_friend_list_visit_cursor = 0
            owner._qqfarm_friend_list_pending_cursor = 0
            owner._qqfarm_friend_list_resume_pending = False
            owner._qqfarm_friend_entry_pending = False
            owner._qqfarm_friend_chain_pending = False
            owner._qqfarm_friend_chain_active = False
            owner._qqfarm_friend_chain_exhausted = False
            owner._qqfarm_friend_chain_allow_home = False
            owner._qqfarm_friend_guard_empty_latched = False
            owner._qqfarm_friend_progress_journal_phase = "active"
            owner._qqfarm_friend_progress_journal_business_date = today
            return True

        namespace.update(
            {
                "_daily_business_date": lambda: "2026-09-19",
                "_friend_progress_journal_rearm_for_business_date": rearm,
                "_friend_list_visit_button_rows": lambda _frame: rows,
                "_guard_dog_ui_config_enabled": lambda: False,
                "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
                "_friend_list_blocked_row_visual_hint": lambda *_args: False,
                "_friend_watchdog_now": lambda: 100.0,
                "_friend_progress_journal_commit": lambda *_args, **_kwargs: True,
                "_friend_guard_post_client_click": (
                    lambda *args: clicks.append(args) or True
                ),
                "_set_friend_chain_fast_interval": lambda *_args, **_kwargs: None,
                "_write": lambda _message: None,
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_pending_cursor=5,
            _qqfarm_friend_list_resume_pending=False,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_guard_empty_latched=True,
            _qqfarm_friend_progress_journal_restored=True,
            _qqfarm_friend_progress_journal_restore_attempted=True,
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_progress_journal_business_date="2026-09-18",
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("visited", result)
        self.assertEqual(["2026-09-19"], rearm_calls)
        self.assertEqual(rows[0]["center"], clicks[-1][:2])
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)
        self.assertFalse(context._qqfarm_friend_chain_exhausted)
        self.assertFalse(context._qqfarm_friend_guard_empty_latched)


class V494FullBoardAndShopGate20260918Tests(unittest.TestCase):
    def test_fresh_full_board_proof_clears_false_native_empty_candidates(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        native_candidates = [
            {"center": (150 + (index * 20), 500), "score": 0.91}
            for index in range(6)
        ]
        proof_calls = []
        logs = []
        namespace.update(
            {
                "_qqfarm_full_board_observation_from_frame": (
                    lambda frame: proof_calls.append(frame) or {
                        "full_board_confirmed": True,
                        "occupied_count": 24,
                        "empty_count": 0,
                        "unknown_count": 0,
                        "anchor_count": 24,
                        "capture_status": "aligned",
                    }
                ),
                "_write": lambda message: logs.append(message),
            }
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_lands=list(native_candidates),
            _qqfarm_recent_empty_land_count=6,
            _qqfarm_stable_empty_lands=list(native_candidates),
            _qqfarm_stable_empty_land_count=6,
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=6,
            _qqfarm_force_self_cycle_next=True,
            _qqfarm_cycle_branch_hint="self",
            _qqfarm_post_harvest_pending=False,
            _qqfarm_single_harvest_planting_pending=False,
        )
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _owner, _frame=None: list(native_candidates),
            "fixture.v494-full-board",
        )

        result = wrapped(bot, np.zeros((800, 428, 3), dtype=np.uint8))

        self.assertTrue(changed)
        self.assertEqual([], result)
        self.assertEqual(1, len(proof_calls))
        self.assertEqual(0, bot._qqfarm_recent_empty_land_count)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("confirmed", bot._qqfarm_empty_land_board_gate_state)
        self.assertTrue(any("candidates count=6" in message for message in logs))

    def test_stale_empty_proof_does_not_authorize_seed_purchase(self):
        namespace = load_functions(
            "_backpack_candidate_kind",
            "_qqfarm_fresh_confirmed_backpack_seed_snapshot",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        now = time.time()
        calls = []
        namespace.update(
            {
                "_write": lambda _message: None,
                "_qqfarm_update_home_priority": lambda *_args, **_kwargs: None,
            }
        )
        bot = types.SimpleNamespace(
            backpack_seed_priority=True,
            _qqfarm_recent_empty_land_count=4,
            _qqfarm_recent_empty_lands=[{"center": (210, 510)}],
            _qqfarm_recent_empty_land_ts=now - 600.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_gate_ts=now - 600.0,
            _qqfarm_backpack_candidates_seen_ts=0.0,
            _qqfarm_backpack_candidate_centers=[],
            _qqfarm_backpack_inventory_scan_complete_ts=now,
            _qqfarm_backpack_inventory_scan_complete_reason="native-no-seed-hint",
            _qqfarm_backpack_inventory_scan_pending=False,
        )
        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            lambda *args, **kwargs: calls.append((args, kwargs)) or True,
            "fixture.v494-stale-shop",
        )

        result = wrapped(bot, "LEVEL_CROP")

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], calls)
        self.assertTrue(bot._qqfarm_inventory_empty_land_proof_pending)
        self.assertTrue(bot._qqfarm_block_level_based_shop)
        self.assertTrue(bot._qqfarm_home_visual_recheck_required)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)

    def test_fresh_confirmed_empty_land_and_clean_backpack_scan_allows_shop(self):
        namespace = load_functions(
            "_backpack_candidate_kind",
            "_qqfarm_fresh_confirmed_backpack_seed_snapshot",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        now = time.time()
        calls = []
        namespace.update(
            {
                "_write": lambda _message: None,
                "_qqfarm_update_home_priority": lambda *_args, **_kwargs: None,
            }
        )
        bot = types.SimpleNamespace(
            backpack_seed_priority=True,
            _qqfarm_recent_empty_land_count=2,
            _qqfarm_recent_empty_lands=[
                {"center": (180, 520)},
                {"center": (240, 520)},
            ],
            _qqfarm_recent_empty_land_ts=now,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_gate_ts=now,
            _qqfarm_backpack_candidates_seen_ts=now,
            _qqfarm_backpack_candidate_centers=[],
            _qqfarm_backpack_candidates_exhausted_seen_ts=now,
            _qqfarm_backpack_inventory_scan_complete_ts=now,
            _qqfarm_backpack_inventory_scan_complete_reason="native-no-seed-hint",
            _qqfarm_backpack_inventory_scan_pending=False,
        )
        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            lambda *args, **kwargs: calls.append((args, kwargs)) or True,
            "fixture.v494-fresh-shop",
        )

        result = wrapped(bot, "LEVEL_CROP")

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual(1, len(calls))
        self.assertFalse(getattr(
            bot, "_qqfarm_inventory_empty_land_proof_pending", False
        ))

    def test_fresh_full_board_blocks_shop_without_rearming_self_route(self):
        namespace = load_functions(
            "_backpack_candidate_kind",
            "_qqfarm_fresh_confirmed_backpack_seed_snapshot",
            "_wrap_buy_seed_for_crop_backpack_guard",
        )
        now = time.time()
        calls = []
        namespace["_write"] = lambda _message: None
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_recent_empty_lands=[],
            _qqfarm_recent_empty_land_ts=now,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_empty_land_board_gate_ts=now,
            _qqfarm_empty_land_scene_confirmed_full=True,
            _qqfarm_empty_land_scene_confirmed_full_ts=now,
            _qqfarm_home_visual_recheck_required=True,
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=6,
            _qqfarm_force_self_cycle_next=True,
            _qqfarm_cycle_branch_hint="self",
            _qqfarm_inventory_empty_land_proof_owned_recheck=True,
        )
        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            lambda *args, **kwargs: calls.append((args, kwargs)) or True,
            "fixture.v494-full-shop",
        )

        result = wrapped(bot, "LEVEL_CROP")

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], calls)
        self.assertFalse(bot._qqfarm_home_visual_recheck_required)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertEqual(0, bot._qqfarm_home_empty_land_remaining)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("", bot._qqfarm_cycle_branch_hint)

    def test_current_seedling_board_proves_24_occupied_after_title_crop(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_qqfarm_dynamic_viewport_plot_anchor_candidates",
            "_qqfarm_dynamic_viewport_crop_geometry_anchor_candidates",
            "_qqfarm_fit_dynamic_24_slot_lattice_from_geometry_anchors",
            "_qqfarm_build_24_plot_ledger",
            "_empty_land_candidate_has_seedling_occupancy",
            "_empty_land_candidate_has_crop_cover",
            "_qqfarm_capture_current_frame_24_slot_ledger",
            "_qqfarm_detect_outer_chrome_crop",
            "_qqfarm_normalize_window_owned_frame_for_business",
            "_qqfarm_full_board_observation_from_frame",
        )
        frame = cv2.imread(str(V494_FULL_BOARD_FIXTURE), cv2.IMREAD_COLOR)
        self.assertIsNotNone(frame)

        observed = namespace["_qqfarm_full_board_observation_from_frame"](
            frame,
            now_ts=494.0,
        )

        self.assertIsInstance(observed, dict)
        self.assertTrue(observed["full_board_confirmed"], observed)
        self.assertEqual(24, observed["occupied_count"], observed)
        self.assertEqual(0, observed["empty_count"], observed)
        self.assertEqual(0, observed["unknown_count"], observed)
        self.assertIn(
            observed["_qqfarm_full_board_probe_source"],
            ("content-crop", "content-crop-minus", "content-crop-plus"),
        )

    def test_current_seedling_board_filters_six_native_false_empty_hits(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_qqfarm_dynamic_viewport_plot_anchor_candidates",
            "_qqfarm_dynamic_viewport_crop_geometry_anchor_candidates",
            "_qqfarm_fit_dynamic_24_slot_lattice_from_geometry_anchors",
            "_qqfarm_build_24_plot_ledger",
            "_empty_land_candidate_has_seedling_occupancy",
            "_empty_land_candidate_has_crop_cover",
            "_qqfarm_capture_current_frame_24_slot_ledger",
            "_qqfarm_detect_outer_chrome_crop",
            "_qqfarm_normalize_window_owned_frame_for_business",
            "_qqfarm_full_board_observation_from_frame",
            "_wrap_detect_empty_lands_state",
        )
        frame = cv2.imread(str(V494_FULL_BOARD_FIXTURE), cv2.IMREAD_COLOR)
        self.assertIsNotNone(frame)
        native_false_hits = [
            {"center": (210 + (index * 24), 655), "score": 0.91}
            for index in range(6)
        ]
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_lands=list(native_false_hits),
            _qqfarm_recent_empty_land_count=6,
            _qqfarm_stable_empty_lands=list(native_false_hits),
            _qqfarm_stable_empty_land_count=6,
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=6,
            _qqfarm_force_self_cycle_next=True,
            _qqfarm_cycle_branch_hint="self",
            _qqfarm_post_harvest_pending=False,
            _qqfarm_single_harvest_planting_pending=False,
        )
        namespace["_write"] = lambda _message: None
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _owner, _frame=None: list(native_false_hits),
            "fixture.v494-live-full-board",
        )

        result = wrapped(bot, frame)

        self.assertTrue(changed)
        self.assertEqual([], result)
        self.assertEqual(0, bot._qqfarm_recent_empty_land_count)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)


if __name__ == "__main__":
    unittest.main()
