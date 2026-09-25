import sys
import time
import types
import unittest
from contextlib import contextmanager
from pathlib import Path

import numpy as np

try:
    import hook
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "portable"))
    import hook


@contextmanager
def patched(name, value, *, create=False):
    marker = object()
    previous = getattr(hook, name, marker)
    if previous is marker and not create:
        raise AttributeError(name)
    setattr(hook, name, value)
    try:
        yield
    finally:
        if previous is marker:
            delattr(hook, name)
        else:
            setattr(hook, name, previous)


class NativeFriendCachedListConsumptionTests(unittest.TestCase):
    def test_recent_global_list_cache_survives_lost_friend_flags_after_rebuild(self):
        owner_blank = np.zeros((800, 428, 3), dtype=np.uint8)
        cached_frame = np.full((800, 428, 3), 43, dtype=np.uint8)
        rows = [{"center": (312, 434 + index * 142)} for index in range(4)]
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=False,
            _qqfarm_live_scene_hint="home",
            _qqfarm_cycle_branch_hint="self",
        )
        calls = []

        def original(*args, **kwargs):
            calls.append((args, kwargs))
            return "native-owner"

        wrapped, changed = hook._wrap_native_v225_friend_help_candidate_cache(
            original, "fixture.FarmBotCV.process_friend_farm"
        )
        self.assertTrue(changed)

        with patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE", cached_frame, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_ROWS_CACHE", rows, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE_TS", time.monotonic() - 8.0, create=True
        ), patched(
            "_qqfarm_capture_native_friend_help_frame", lambda _ctx: owner_blank
        ), patched(
            "_get_frame_from_bot", lambda *_args, **_kwargs: None, create=True
        ), patched(
            "_friend_list_visit_button_rows",
            lambda frame: [] if frame is owner_blank else rows, create=True
        ), patched(
            "_friend_guard_friend_ui_state", lambda _frame: False, create=True
        ), patched(
            "_handle_friend_list_surface",
            lambda _ctx, _frame: calls.append(("list",)) or "visited", create=True
        ), patched(
            "_write", lambda *_args, **_kwargs: None
        ), patched(
            "_throttled_write", lambda *_args, **_kwargs: None
        ):
            result = wrapped(context)

        self.assertFalse(result)
        self.assertIn(("list",), calls)

    def test_native_owner_consumes_global_list_cache_when_context_cache_is_missing(self):
        owner_blank = np.zeros((800, 428, 3), dtype=np.uint8)
        cached_frame = np.full((800, 428, 3), 31, dtype=np.uint8)
        rows = [{"center": (312, 434 + index * 142)} for index in range(5)]
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_active=True,
            _qqfarm_live_scene_hint="friend",
        )
        calls = []

        def original(*args, **kwargs):
            calls.append((args, kwargs))
            return "native-owner"

        wrapped, changed = hook._wrap_native_v225_friend_help_candidate_cache(
            original, "fixture.FarmBotCV.process_friend_farm"
        )
        self.assertTrue(changed)

        with patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE", cached_frame, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_ROWS_CACHE", rows, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE_TS", time.monotonic() - 8.0, create=True
        ), patched(
            "_qqfarm_capture_native_friend_help_frame",
            lambda _ctx: owner_blank,
        ), patched(
            "_get_frame_from_bot", lambda *_args, **_kwargs: None, create=True
        ), patched(
            "_friend_list_visit_button_rows",
            lambda frame: [] if frame is owner_blank else rows,
            create=True,
        ), patched(
            "_friend_guard_friend_ui_state", lambda _frame: False, create=True
        ), patched(
            "_handle_friend_list_surface",
            lambda _ctx, _frame: calls.append(("list",)) or "visited",
            create=True,
        ), patched(
            "_write", lambda *_args, **_kwargs: None
        ), patched(
            "_throttled_write", lambda *_args, **_kwargs: None
        ):
            result = wrapped(context)

        self.assertFalse(result)
        self.assertIn(("list",), calls)
        self.assertFalse(any(item[0] != "list" for item in calls))

    def test_native_owner_consumes_global_cache_after_stale_home_hint(self):
        owner_blank = np.zeros((800, 428, 3), dtype=np.uint8)
        cached_frame = np.full((800, 428, 3), 37, dtype=np.uint8)
        rows = [{"center": (312, 434 + index * 142)} for index in range(5)]
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_active=True,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_live_scene_hint="home",
        )
        calls = []

        def original(*args, **kwargs):
            calls.append((args, kwargs))
            return "native-owner"

        wrapped, changed = hook._wrap_native_v225_friend_help_candidate_cache(
            original, "fixture.FarmBotCV.process_friend_farm"
        )
        self.assertTrue(changed)

        with patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE", cached_frame, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_ROWS_CACHE", rows, create=True
        ), patched(
            "_QQFARM_FRIEND_LIST_FRAME_CACHE_TS", time.monotonic() - 8.0, create=True
        ), patched(
            "_qqfarm_capture_native_friend_help_frame", lambda _ctx: owner_blank
        ), patched(
            "_get_frame_from_bot", lambda *_args, **_kwargs: None, create=True
        ), patched(
            "_friend_list_visit_button_rows",
            lambda frame: [] if frame is owner_blank else rows, create=True
        ), patched(
            "_friend_guard_friend_ui_state", lambda _frame: False, create=True
        ), patched(
            "_handle_friend_list_surface",
            lambda _ctx, _frame: calls.append(("list",)) or "visited", create=True
        ), patched(
            "_write", lambda *_args, **_kwargs: None
        ), patched(
            "_throttled_write", lambda *_args, **_kwargs: None
        ):
            result = wrapped(context)

        self.assertFalse(result)
        self.assertIn(("list",), calls)

    def test_recent_list_cache_blocks_blank_self_reconciliation_release(self):
        blank_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        cached_frame = np.full((800, 428, 3), 23, dtype=np.uint8)
        rows = [{"center": (312, 434 + index * 142)} for index in range(5)]
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_list_frame_cache=cached_frame,
            _qqfarm_friend_list_rows_cache=rows,
            _qqfarm_friend_list_frame_cache_ts=time.monotonic() - 8.0,
            _qqfarm_friend_list_surface_seen_ts=time.monotonic() - 8.0,
        )

        with patched(
            "_friend_list_visit_button_rows", lambda _frame: [], create=True
        ), patched(
            "_friend_selected_carousel_card_bounds", lambda _frame: None, create=True
        ), patched(
            "_friend_watchdog_now", lambda: time.time(), create=True
        ), patched(
            "_write", lambda *_args, **_kwargs: None
        ), patched(
            "_throttled_write", lambda *_args, **_kwargs: None
        ):
            released = hook._qqfarm_reconcile_visible_self_surface(
                context, blank_frame, False
            )

        self.assertFalse(released)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)
        self.assertTrue(context._qqfarm_friend_entry_pending)
        self.assertIs(cached_frame, context._qqfarm_friend_list_frame_cache)

    def test_native_owner_consumes_recent_list_cache_across_one_patrol_interval(self):
        owner_blank = np.zeros((800, 428, 3), dtype=np.uint8)
        cached_frame = np.full((800, 428, 3), 17, dtype=np.uint8)
        rows = [{"center": (312, 434 + index * 142)} for index in range(5)]
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_friend_list_frame_cache=cached_frame,
            _qqfarm_friend_list_rows_cache=rows,
            _qqfarm_friend_list_frame_cache_ts=time.monotonic() - 8.0,
            _qqfarm_friend_list_surface_seen_ts=time.monotonic() - 8.0,
        )
        calls = []

        def original(*args, **kwargs):
            calls.append((args, kwargs))
            return "native-owner"

        wrapped, changed = hook._wrap_native_v225_friend_help_candidate_cache(
            original, "fixture.FarmBotCV.process_friend_farm"
        )
        self.assertTrue(changed)

        with patched(
            "_qqfarm_capture_native_friend_help_frame",
            lambda _ctx: owner_blank,
        ), patched(
            "_get_frame_from_bot", lambda *_args, **_kwargs: None, create=True
        ), patched(
            "_friend_list_visit_button_rows",
            lambda frame: [] if frame is owner_blank else rows,
            create=True,
        ), patched(
            "_friend_guard_friend_ui_state", lambda _frame: False, create=True
        ), patched(
            "_handle_friend_list_surface",
            lambda _ctx, _frame: calls.append(("list",)) or "visited",
            create=True,
        ), patched(
            "_write", lambda *_args, **_kwargs: None
        ), patched(
            "_throttled_write", lambda *_args, **_kwargs: None
        ):
            result = wrapped(context)

        self.assertFalse(result)
        self.assertIn(("list",), calls)
        self.assertFalse(any(item[0] != "list" for item in calls))


if __name__ == "__main__":
    unittest.main()
