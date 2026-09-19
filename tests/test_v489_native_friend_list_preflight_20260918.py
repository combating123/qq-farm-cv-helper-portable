import ast
import hashlib
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURE = ROOT / "tests" / "fixtures" / "live-v488-current-friend-list-20260918.png"
FIXTURE_SHA256 = "4A22A48E4B27E01250D60ECC6044958BACF3B9E5BA3A629DBC3F89D86CA0652B"


def load_functions(*wanted):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(wanted)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V489NativeFriendListPreflight20260918Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest().upper()
        if actual != FIXTURE_SHA256:
            raise AssertionError(f"fixture hash changed: {actual}")
        cls.namespace = load_functions(
            "_wrap_native_v225_friend_help_candidate_cache",
            "_qqfarm_native_friend_surface_cache_fresh",
            "_friend_list_card_rows",
            "_friend_list_visit_button_rows",
        )
        cls.frame = cv2.imdecode(
            np.fromfile(str(FIXTURE), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if cls.frame is None:
            raise AssertionError("live friend-list fixture cannot be decoded")

    def test_native_owner_bridge_visits_visible_friend_card_before_native_noop(self):
        namespace = self.namespace
        frame = self.frame
        calls = []
        rows_fn = namespace["_friend_list_visit_button_rows"]
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": lambda _owner: frame,
                "_friend_list_visit_button_rows": rows_fn,
                "_handle_friend_list_surface": (
                    lambda owner, candidate: calls.append(
                        ("list", owner, candidate)
                    )
                    or "visited"
                ),
                "_throttled_write": lambda *_args, **_kwargs: None,
                "_write": lambda message: calls.append(("log", message)),
            }
        )
        context = types.SimpleNamespace()

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        result = wrapped(context)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertTrue(any(item[0] == "list" for item in calls))
        self.assertFalse(any(item[0] == "original" for item in calls))

    def test_same_day_terminal_latch_blocks_native_owner_before_list_reopen(self):
        namespace = self.namespace
        calls = []
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": lambda _owner: None,
                "_friend_list_visit_button_rows": lambda _frame: [],
                "_daily_business_date": lambda: "2026-09-19",
                "_friend_progress_journal_rearm_for_business_date": (
                    lambda owner, today=None: calls.append(("rearm", today))
                    or False
                ),
                "_friend_guard_poll_dispatch_allowed": lambda _owner: False,
                "_throttled_write": lambda *args, **_kwargs: calls.append(
                    ("throttled",) + args
                ),
                "_write": lambda message: calls.append(("log", message)),
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_progress_journal_business_date="2026-09-19",
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_visible_candidate_count=5,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_guard_empty_latched=True,
        )

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        result = wrapped(context)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([("rearm", "2026-09-19")], [
            item for item in calls if item[0] == "rearm"
        ])
        self.assertFalse(any(item[0] == "original" for item in calls))
        self.assertTrue(any(
            item[0] == "throttled" and "terminal" in str(item).lower()
            for item in calls
        ))

    def test_terminal_latch_does_not_block_already_visible_friend_farm_surface(self):
        """A farm page with the home button is not a friend-list reopen."""
        namespace = self.namespace
        calls = []
        frame = types.SimpleNamespace(shape=(1200, 641, 3))
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": lambda _owner: frame,
                # The single detected row is the bottom friend-card residue on
                # the farm page; a real list has at least three rows here.
                "_friend_list_visit_button_rows": lambda _frame: [
                    {"center": (326, 646)}
                ],
                "_friend_guard_friend_ui_state": lambda _frame: True,
                "_daily_business_date": lambda: "2026-09-19",
                "_friend_progress_journal_rearm_for_business_date": (
                    lambda owner, today=None: calls.append(("rearm", today))
                    or False
                ),
                "_friend_guard_poll_dispatch_allowed": lambda _owner: False,
                "_throttled_write": lambda *args, **_kwargs: calls.append(
                    ("throttled",) + args
                ),
                "_write": lambda message: calls.append(("log", message)),
                "_qqfarm_native_friend_help_durable_snapshot": lambda _owner: 0,
                "_qqfarm_native_friend_help_quorum_baseline": lambda _owner: 0,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_progress_journal_business_date="2026-09-19",
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_visible_candidate_count=5,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_guard_empty_latched=True,
        )

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        wrapped(context)

        self.assertTrue(changed)
        self.assertTrue(any(item[0] == "original" for item in calls))
        self.assertFalse(any(
            item[0] == "throttled" and "terminal/empty latch" in str(item)
            for item in calls
        ))

    def test_native_owner_prefers_fresh_friend_frame_over_non_frame_argument(self):
        """A compiled owner may pass a crop-like ndarray before the live frame."""
        actual_frame = types.SimpleNamespace(shape=(1199, 641, 3))

        namespace = self.namespace
        calls = []
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: actual_frame
                ),
                "_friend_list_visit_button_rows": lambda _frame: [],
                "_friend_guard_friend_ui_state": (
                    lambda frame: True if frame is actual_frame else False
                ),
                "_daily_business_date": lambda: "2026-09-19",
                "_friend_progress_journal_rearm_for_business_date": (
                    lambda owner, today=None: calls.append(("rearm", today))
                    or False
                ),
                "_friend_guard_poll_dispatch_allowed": lambda _owner: False,
                "_throttled_write": lambda *args, **_kwargs: calls.append(
                    ("throttled",) + args
                ),
                "_write": lambda message: calls.append(("log", message)),
                "_qqfarm_native_friend_help_durable_snapshot": lambda _owner: 0,
                "_qqfarm_native_friend_help_quorum_baseline": lambda _owner: 0,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_progress_journal_business_date="2026-09-19",
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_list_visit_cursor=4,
            _qqfarm_friend_list_visible_candidate_count=4,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_guard_empty_latched=True,
        )
        misleading_argument = np.zeros((16, 16, 3), dtype=np.uint8)

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        result = wrapped(context, misleading_argument)

        self.assertTrue(changed)
        self.assertEqual("native-result", result)
        self.assertTrue(any(item[0] == "original" for item in calls))
        self.assertFalse(any(
            item[0] == "throttled" and "terminal/empty latch" in str(item)
            for item in calls
        ))

    def test_recent_friend_surface_survives_one_bad_capture_without_reopening_list(self):
        """A transient non-farm capture must not re-enter the terminal latch."""
        namespace = self.namespace
        calls = []
        good_frame = types.SimpleNamespace(shape=(800, 428, 3))
        bad_frame = types.SimpleNamespace(shape=(800, 428, 3))
        captures = iter((good_frame, bad_frame))
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: next(captures)
                ),
                "_friend_list_visit_button_rows": lambda _frame: [],
                "_friend_guard_friend_ui_state": (
                    lambda frame: True if frame is good_frame else False
                ),
                "_daily_business_date": lambda: "2026-09-19",
                "_friend_progress_journal_rearm_for_business_date": (
                    lambda owner, today=None: calls.append(("rearm", today))
                    or False
                ),
                "_friend_guard_poll_dispatch_allowed": lambda _owner: False,
                "_throttled_write": lambda *args, **_kwargs: calls.append(
                    ("throttled",) + args
                ),
                "_write": lambda message: calls.append(("log", message)),
                "_qqfarm_native_friend_help_durable_snapshot": lambda _owner: 0,
                "_qqfarm_native_friend_help_quorum_baseline": lambda _owner: 0,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_progress_journal_business_date="2026-09-19",
            _qqfarm_friend_progress_journal_phase="terminal",
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_visible_candidate_count=5,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_guard_empty_latched=True,
        )

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        wrapped(context)
        wrapped(context)

        self.assertTrue(changed)
        self.assertEqual(2, len([item for item in calls if item[0] == "original"]))
        self.assertFalse(any(
            item[0] == "throttled" and "terminal/empty latch" in str(item)
            for item in calls
        ))


if __name__ == "__main__":
    unittest.main()
