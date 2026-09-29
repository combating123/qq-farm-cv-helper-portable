import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*wanted):
    tree = ast.parse(HOOK.read_text(encoding="utf-8-sig"), filename=str(HOOK))
    wanted = set(wanted)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError(f"hook.py is missing: {sorted(missing)}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FriendListNonFarmRecovery20260929Tests(unittest.TestCase):
    def test_window_owned_friend_list_survives_business_frame_normalization(self):
        """Raw PrintWindow rows remain authoritative after coordinate normalization."""
        ns = load_functions("_get_frame_from_bot")
        raw_frame = object()
        normalized_frame = object()
        rows = [{"center": (20, 100 + index * 80)} for index in range(5)]
        native_calls = []
        bot = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(
                get_window_frame=lambda: native_calls.append("native") or None
            )
        )
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_capture_visible_farm_frame": lambda: raw_frame,
            "_qqfarm_prepare_visible_frame_for_business": (
                lambda frame: normalized_frame if frame is raw_frame else frame
            ),
            "_qqfarm_visible_capture_frame_is_trusted": lambda _frame: False,
            "_qqfarm_visible_frame_has_farm_scene": lambda _frame: False,
            "_friend_list_visit_button_rows": (
                lambda frame: rows if frame is raw_frame else []
            ),
            "_qqfarm_runtime_friend_list_frame_is_valid": (
                lambda _context, _frame: False
            ),
            "_qqfarm_native_capture_fallback_allowed": lambda: True,
            "_qqfarm_note_native_capture_fallback": lambda: None,
            "_qqfarm_native_capture_frame_is_business_safe": lambda _frame: False,
            "_qqfarm_recent_good_capture_frame": lambda: None,
            "_qqfarm_remember_good_capture_frame": lambda _frame: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = ns["_get_frame_from_bot"](bot)

        self.assertIs(normalized_frame, result)
        self.assertEqual([], native_calls)

    def test_friend_list_cache_keeps_readiness_open_during_transient_capture_gap(self):
        ns = load_functions(
            "_qqfarm_runtime_page_action_label",
            "_qqfarm_note_page_readiness",
            "_qqfarm_runtime_no_frame_diagnostic",
            "_qqfarm_runtime_page_readiness_gate",
            "_qqfarm_persistent_nonfarm_surface_recovery",
            "_qqfarm_runtime_friend_list_frame_is_valid",
            "_qqfarm_resolve_friend_list_frame",
            "_qqfarm_remember_friend_list_frame",
        )
        clock = {"now": 130.0}
        events = []
        rows = [{"center": (20, 100 + index * 80)} for index in range(5)]
        cached_frame = object()
        context = types.SimpleNamespace(
            _qqfarm_friend_list_frame_cache=cached_frame,
            _qqfarm_friend_list_rows_cache=rows,
            _qqfarm_friend_list_frame_cache_ts=100.0,
            _qqfarm_friend_list_surface_seen_ts=100.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_cycle_seen=True,
        )
        ns["time"] = types.SimpleNamespace(
            time=lambda: clock["now"],
            monotonic=lambda: clock["now"],
        )
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_share_find_farm_window_hwnd": lambda: 777,
            "_get_frame_from_bot": lambda _owner: None,
            "_qqfarm_frame_is_usable_for_empty_land_detection": (
                lambda _frame: False
            ),
            "_friend_list_visit_button_rows": lambda frame: rows if frame is cached_frame else [],
            "_qqfarm_visible_frame_has_farm_scene": lambda _frame: False,
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(("close", hwnd)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
            "_write": lambda message: events.append(str(message)),
        })

        allowed = ns["_qqfarm_runtime_page_readiness_gate"](
            context, "FarmBotCV.run_cycle"
        )

        self.assertTrue(allowed)
        self.assertNotIn(("close", 777), events)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)

    def test_blank_owner_frame_uses_active_friend_list_cache(self):
        ns = load_functions("_qqfarm_runtime_friend_list_frame_is_valid")
        rows = [{"center": (20, 100 + index * 80)} for index in range(5)]
        cached_frame = object()
        context = types.SimpleNamespace(
            _qqfarm_friend_list_frame_cache=cached_frame,
            _qqfarm_friend_list_rows_cache=rows,
            _qqfarm_friend_list_frame_cache_ts=100.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_chain_active=True,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 130.0)
        ns.update({
            "_friend_list_visit_button_rows": lambda frame: rows if frame is cached_frame else [],
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(ns["_qqfarm_runtime_friend_list_frame_is_valid"](
            context, object()
        ))

    def test_friend_farm_surface_does_not_reuse_old_list_as_current_list(self):
        ns = load_functions("_qqfarm_runtime_friend_list_frame_is_valid")
        rows = [{"center": (20, 100 + index * 80)} for index in range(5)]
        context = types.SimpleNamespace(
            _qqfarm_friend_list_frame_cache=object(),
            _qqfarm_friend_list_rows_cache=rows,
            _qqfarm_friend_list_frame_cache_ts=100.0,
            _qqfarm_live_scene_hint="friend",
            _qqfarm_native_friend_surface_state="friend-farm",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_chain_active=True,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 130.0)
        ns.update({
            "_friend_list_visit_button_rows": lambda _frame: [],
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertFalse(ns["_qqfarm_runtime_friend_list_frame_is_valid"](
            context, object()
        ))

    def test_active_friend_list_cache_blocks_close_after_one_missed_interval(self):
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        clock = {"now": 130.0}
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[1, 2, 3, 4, 5],
            _qqfarm_friend_list_frame_cache_ts=100.0,
            _qqfarm_friend_list_surface_seen_ts=100.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_cycle_seen=True,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: clock["now"])
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(
                ("close", hwnd)
            ) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "no-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)

    def test_recent_valid_friend_list_cache_blocks_close_and_preserves_route(self):
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        clock = {"now": 100.0}
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[1, 2, 3, 4, 5],
            _qqfarm_friend_list_frame_cache_ts=95.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_list_visit_cursor=1,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: clock["now"])
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(
                ("close", hwnd)
            ) or True,
            "_qqfarm_invalidate_wgc_frame_cache": lambda reason="": events.append(
                ("invalidate", reason)
            ),
            "_qqfarm_stop_wgc_capture": lambda reason="": events.append(
                ("stop", reason)
            ),
            "_qqfarm_restore_hidden_miniapp_taskbar_card": lambda reason="": events.append(
                ("restore", reason)
            ) or True,
            "_qqfarm_start_wgc_capture": lambda: events.append(("start",)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
        })

        result = None
        for _ in range(8):
            result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)
        self.assertNotIn(("invalidate", "no-frame"), events)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(any("friend-list" in item for item in events))

    def test_share_surface_miss_refreshes_current_capture_once(self):
        ns = load_functions("_share_retry_after_surface_miss")
        events = []
        context = types.SimpleNamespace()
        ns.update({
            "_qqfarm_invalidate_wgc_frame_cache": lambda reason="": events.append(
                ("invalidate", reason)
            ),
            "_get_frame_from_bot": lambda owner: events.append(
                ("capture", owner)
            ) or object(),
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
        })

        self.assertTrue(ns["_share_retry_after_surface_miss"](context, "dialog"))
        self.assertFalse(ns["_share_retry_after_surface_miss"](context, "dialog"))
        self.assertEqual(1, len([item for item in events if item[0] == "capture"]))
        self.assertEqual(
            ("invalidate", "share-dialog-surface-miss"),
            next(item for item in events if isinstance(item, tuple) and item[0] == "invalidate"),
        )

    def test_pending_friend_reopen_loading_is_bounded_wait_not_home_close(self):
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        clock = {"now": 110.0}
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_friend_list_visit_cursor=0,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: clock["now"])
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(
                ("close", hwnd)
            ) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "non-farm-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)
        self.assertTrue(context._qqfarm_friend_entry_pending)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)

    def test_pending_friend_list_route_never_closes_when_cache_timestamp_was_lost(self):
        """Native cache cleanup must not turn an active list transition into WM_CLOSE."""
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_timeout_seconds=8.0,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 110.0)
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(("close", hwnd)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(str(args[1]) if len(args) > 1 else str(args)),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "non-farm-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)

    def test_active_friend_list_scene_never_closes_after_native_clears_pending_cache(self):
        """A verified list scene remains a wait state after native flag cleanup."""
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_cycle_seen=True,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 110.0)
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(("close", hwnd)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(str(args[1]) if len(args) > 1 else str(args)),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "non-farm-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)

    def test_pending_verified_friend_entry_survives_blank_scene_hint_without_close(self):
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="",
            _qqfarm_native_friend_surface_state="",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_entry_verified_surface="friend-list",
            _qqfarm_friend_entry_clicked_ts=105.0,
            _qqfarm_friend_entry_transition_marker_surface="friend-list",
            _qqfarm_friend_entry_transition_marker_ts=105.0,
            friend_list_entry_timeout_seconds=8.0,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 110.0)
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(("close", hwnd)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(str(args[1]) if len(args) > 1 else str(args)),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "no-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)

    def test_active_friend_transition_survives_lost_scene_hint_without_close(self):
        """A transient home/blank classifier result must not close an active friend route."""
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="home",
            _qqfarm_native_friend_surface_state="",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_friend_entry_verified_surface="",
            _qqfarm_friend_entry_transition_marker_surface="",
            _qqfarm_friend_entry_clicked_ts=0.0,
            _qqfarm_friend_entry_transition_marker_ts=0.0,
            friend_list_entry_timeout_seconds=8.0,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 110.0, time=lambda: 110.0)
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(
                ("close", hwnd)
            ) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(
                str(args[1]) if len(args) > 1 else str(args)
            ),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "non-farm-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)
        self.assertTrue(context._qqfarm_friend_chain_pending)

    def test_expired_cacheless_friend_hold_releases_scheduler_without_closing_app(self):
        ns = load_functions(
            "_qqfarm_friend_list_nonfarm_recovery_protected",
            "_qqfarm_persistent_nonfarm_surface_recovery",
        )
        events = []
        context = types.SimpleNamespace(
            _qqfarm_friend_list_rows_cache=[],
            _qqfarm_friend_list_frame_cache_ts=0.0,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_native_friend_surface_state="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_verified_surface="friend-list",
            _qqfarm_friend_entry_transition_marker_surface="friend-list",
            _qqfarm_friend_entry_transition_marker_ts=100.0,
            _qqfarm_friend_list_visit_cursor=2,
            _qqfarm_friend_list_pending_cursor=2,
            friend_list_entry_timeout_seconds=8.0,
        )
        ns["time"] = types.SimpleNamespace(monotonic=lambda: 140.0)
        ns.update({
            "_qqfarm_request_farm_window_close": lambda hwnd: events.append(("close", hwnd)) or True,
            "_set_friend_chain_fast_interval": lambda _ctx, enabled: events.append(("fast", enabled)),
            "_qqfarm_reset_persistent_nonfarm_surface_recovery": lambda _ctx, hwnd=0: events.append(("reset", hwnd)) or True,
            "_throttled_write": lambda *args, **kwargs: events.append(str(args[1]) if len(args) > 1 else str(args)),
        })

        result = ns["_qqfarm_persistent_nonfarm_surface_recovery"](
            context, 777, "no-frame"
        )

        self.assertEqual("friend-list-wait", result)
        self.assertNotIn(("close", 777), events)
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertFalse(context._qqfarm_friend_chain_pending)
        self.assertFalse(context._qqfarm_friend_chain_active)
        self.assertTrue(context._qqfarm_friend_list_resume_pending)
        self.assertEqual(2, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(("fast", False), next(item for item in events if isinstance(item, tuple) and item[0] == "fast"))

    def test_same_list_evidence_does_not_reclick_pending_row(self):
        ns = load_functions("_handle_friend_list_surface")
        rows = [{"center": (571, 448 + index * 148)} for index in range(5)]
        clicks = []
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_last_retry_ts=100.0,
            _qqfarm_friend_entry_retry_count=1,
            _qqfarm_friend_entry_last_list_signature="same-list",
            _qqfarm_friend_entry_verified_surface="friend-list",
        )
        frame = types.SimpleNamespace(shape=(1251, 671, 3))
        ns.update({
            "_friend_list_visit_button_rows": lambda _frame: rows,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_watchdog_now": lambda: 101.0,
            "_qqfarm_frame_progress_signature": lambda _frame: "same-list",
            "_friend_guard_post_client_click": lambda *args: clicks.append(args) or True,
            "_write": lambda _message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = ns["_handle_friend_list_surface"](context, frame)

        self.assertEqual("pending-row-backoff", result)
        self.assertEqual([], clicks)

    def test_same_list_pending_row_times_out_into_bounded_reopen(self):
        """An unchanged list must not hold the whole scheduler forever."""
        ns = load_functions("_handle_friend_list_surface")
        rows = [{"center": (571, 448 + index * 148)} for index in range(5)]
        clicks = []
        fast_intervals = []
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_last_retry_ts=100.0,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_last_list_signature="same-list",
            _qqfarm_friend_entry_verified_surface="friend-list",
            friend_list_entry_timeout_seconds=8.0,
        )
        frame = types.SimpleNamespace(shape=(1251, 671, 3))
        ns.update({
            "_friend_list_visit_button_rows": lambda _frame: rows,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_watchdog_now": lambda: 112.0,
            "_qqfarm_frame_progress_signature": lambda _frame: "same-list",
            "_friend_list_blocked_row_visual_hint": lambda *_args: False,
            "_friend_guard_post_client_click": lambda *args: clicks.append(args) or True,
            "_set_friend_chain_fast_interval": lambda _ctx, enabled: fast_intervals.append(enabled),
            "_write": lambda _message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = ns["_handle_friend_list_surface"](context, frame)

        self.assertEqual("pending-row-reopen", result)
        self.assertEqual(1, len(clicks))
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(context._qqfarm_friend_list_resume_pending)
        self.assertEqual([False], fast_intervals)

    def test_terminal_pending_cursor_does_not_wrap_to_first_row(self):
        """A pending cursor at N/N must converge without clicking row zero."""
        ns = load_functions("_handle_friend_list_surface")
        rows = [{"center": (364, 288 + index * 95)} for index in range(3)]
        clicks = []
        fast_intervals = []
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_list_visit_cursor=3,
            _qqfarm_friend_list_pending_cursor=3,
            _qqfarm_friend_list_resume_pending=False,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_last_retry_ts=100.0,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_last_list_signature="same-list",
            _qqfarm_friend_entry_verified_surface="friend-list",
            friend_list_entry_timeout_seconds=8.0,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        ns.update({
            "_friend_list_visit_button_rows": lambda _frame: rows,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_friend_watchdog_now": lambda: 112.0,
            "_qqfarm_frame_progress_signature": lambda _frame: "same-list",
            "_friend_guard_post_client_click": (
                lambda *args: clicks.append(args) or True
            ),
            "_set_friend_chain_fast_interval": (
                lambda _ctx, enabled: fast_intervals.append(enabled)
                or setattr(_ctx, "check_interval", 0.75 if enabled else 12.0)
            ),
            "_write": lambda _message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = ns["_handle_friend_list_surface"](context, frame)

        self.assertIn(result, ("closed", "closed-terminal-latch"))
        self.assertFalse(any(len(args) >= 2 and args[1] in (288, 383, 478) for args in clicks))
        self.assertEqual([False], fast_intervals)
        self.assertEqual(3, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(3, context._qqfarm_friend_list_pending_cursor)
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertTrue(context._qqfarm_friend_chain_exhausted)


    def test_friend_list_frame_is_ready_for_friend_dispatch_even_without_farm_canvas(self):
        ns = load_functions("_qqfarm_runtime_friend_list_frame_is_valid")
        context = types.SimpleNamespace(
            _qqfarm_live_scene_hint="home",
            _qqfarm_cycle_branch_hint="self",
        )
        rows = [{"center": (20, 100 + index * 80)} for index in range(5)]
        ns.update({
            "_friend_list_visit_button_rows": lambda frame: rows,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(ns["_qqfarm_runtime_friend_list_frame_is_valid"](
            context, object()
        ))
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)
        self.assertEqual("friend", context._qqfarm_cycle_branch_hint)


if __name__ == "__main__":
    unittest.main()
