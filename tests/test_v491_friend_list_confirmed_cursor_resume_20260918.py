import ast
import json
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


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
        raise AssertionError(f"hook.py is missing: {sorted(missing)}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V491FriendListConfirmedCursorResume20260918Tests(unittest.TestCase):
    def _namespace(self):
        namespace = load_functions(
            "_commit_friend_list_entry_transition",
            "_handle_friend_list_surface",
        )
        rows = [
            {
                "center": (365, 289 + (94 * index)),
                "rect": (331, 271 + (94 * index), 399, 307 + (94 * index)),
            }
            for index in range(5)
        ]
        clicks = []
        logs = []
        namespace.update(
            {
                "_friend_list_visit_button_rows": lambda _frame: rows,
                "_guard_dog_ui_config_enabled": lambda: False,
                "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
                "_friend_list_blocked_row_visual_hint": lambda *_args: False,
                "_friend_watchdog_now": lambda: 100.0 + len(clicks),
                "_friend_progress_journal_commit": lambda *_args, **_kwargs: True,
                "_friend_progress_journal_record": lambda _owner: True,
                "_friend_guard_post_client_click": (
                    lambda *args: clicks.append(args) or True
                ),
                "_set_friend_chain_fast_interval": lambda *_args, **_kwargs: None,
                "_write": lambda message: logs.append(str(message)),
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        return namespace, rows, clicks, logs

    def test_confirmed_first_row_resumes_at_second_row_when_list_reopens(self):
        namespace, rows, clicks, logs = self._namespace()
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_list_resume_pending=False,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_progress_journal_restore_attempted=True,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        self.assertEqual(
            "visited",
            namespace["_handle_friend_list_surface"](context, frame),
        )
        self.assertEqual(rows[0]["center"], clicks[-1][:2])
        self.assertTrue(
            namespace["_commit_friend_list_entry_transition"](context)
        )

        # The native friend processor clears the in-flight entry once the
        # friend farm is confirmed, then returns to the same visible list.
        context._qqfarm_friend_entry_pending = False
        context._qqfarm_friend_entry_clicked_ts = 0.0
        context._qqfarm_friend_chain_pending = False
        context._qqfarm_friend_chain_active = False

        self.assertTrue(context._qqfarm_friend_list_resume_pending)
        self.assertEqual(
            "visited",
            namespace["_handle_friend_list_surface"](context, frame),
        )
        self.assertEqual(rows[1]["center"], clicks[-1][:2])
        self.assertNotEqual(rows[0]["center"], clicks[-1][:2])
        self.assertFalse(any("reset stale cursor=1" in line for line in logs))

    def test_failed_cursor_journal_does_not_arm_list_resume(self):
        namespace, _rows, _clicks, _logs = self._namespace()
        namespace["_friend_progress_journal_record"] = lambda _owner: False
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_resume_pending=False,
            _qqfarm_friend_entry_retry_count=2,
            _qqfarm_friend_entry_last_retry_ts=99.0,
            _qqfarm_friend_last_row_card_fallback_tried=True,
        )

        self.assertFalse(
            namespace["_commit_friend_list_entry_transition"](context)
        )
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)
        self.assertFalse(context._qqfarm_friend_list_resume_pending)

    def test_confirmed_last_row_closes_list_instead_of_starting_second_pass(self):
        namespace, _rows, clicks, logs = self._namespace()
        schedules = []
        namespace["_friend_guard_schedule_empty_poll"] = (
            lambda _owner, reason="", now_ts=0.0:
            schedules.append((reason, now_ts)) or 0.0
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=5,
            _qqfarm_friend_list_pending_cursor=4,
            _qqfarm_friend_list_resume_pending=True,
            _qqfarm_friend_list_visible_candidate_count=5,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_progress_journal_restore_attempted=True,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("closed", result)
        self.assertEqual((405, 94), clicks[-1][:2])
        self.assertNotEqual((365, 289), clicks[-1][:2])
        self.assertEqual(5, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(5, context._qqfarm_friend_list_pending_cursor)
        self.assertFalse(context._qqfarm_friend_list_resume_pending)
        self.assertTrue(context._qqfarm_friend_chain_exhausted)
        self.assertTrue(any(
            "confirmed last row complete" in line for line in logs
        ))
        self.assertEqual(
            "friend-list-confirmed-last-row-complete",
            schedules[-1][0],
        )

    def test_terminal_latch_closes_reopened_list_without_resetting_first_row(self):
        namespace, _rows, clicks, logs = self._namespace()
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
            _qqfarm_friend_progress_journal_restore_attempted=True,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("closed-terminal-latch", result)
        self.assertEqual((405, 94), clicks[-1][:2])
        self.assertNotEqual((365, 289), clicks[-1][:2])
        self.assertEqual(5, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(context._qqfarm_friend_chain_exhausted)
        self.assertTrue(any("terminal latch" in line for line in logs))

    def test_terminal_journal_restore_reinstates_exhausted_latch(self):
        namespace = load_functions("_friend_progress_journal_restore")
        payload = {
            "business_date": "2026-09-18",
            "instances": {
                "1": {
                    "cursor": 5,
                    "pending_cursor": 5,
                    "resume_pending": False,
                    "entry_pending": False,
                    "chain_pending": False,
                    "visible_count": 5,
                    "entry_retry_count": 0,
                    "last_row_fallback_tried": False,
                    "phase": "terminal",
                }
            },
            "version": 1,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            journal = Path(temp_dir) / "friend_traversal_journal.json"
            journal.write_text(json.dumps(payload), encoding="utf-8")
            context = types.SimpleNamespace(instance_id="1")

            restored = namespace["_friend_progress_journal_restore"](
                context,
                row_count=5,
                journal_path=str(journal),
                today="2026-09-18",
            )

        self.assertTrue(restored)
        self.assertEqual(5, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(context._qqfarm_friend_chain_exhausted)
        self.assertTrue(context._qqfarm_friend_guard_empty_latched)

    def test_visible_list_restores_terminal_journal_even_after_empty_attempt(self):
        namespace, _rows, clicks, logs = self._namespace()
        restore_calls = []

        def restore_terminal(owner, row_count=None):
            restore_calls.append(row_count)
            owner._qqfarm_friend_list_visit_cursor = 5
            owner._qqfarm_friend_list_pending_cursor = 5
            owner._qqfarm_friend_list_resume_pending = False
            owner._qqfarm_friend_chain_exhausted = True
            owner._qqfarm_friend_chain_allow_home = True
            owner._qqfarm_friend_guard_empty_latched = True
            owner._qqfarm_friend_progress_journal_restored = True
            owner._qqfarm_friend_progress_journal_phase = "terminal"
            return True

        namespace["_friend_progress_journal_restore"] = restore_terminal
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=4,
            _qqfarm_friend_list_pending_cursor=4,
            _qqfarm_friend_list_resume_pending=False,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_progress_journal_restore_attempted=True,
            _qqfarm_friend_progress_journal_restored=False,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual([5], restore_calls)
        self.assertEqual("closed-terminal-latch", result)
        self.assertEqual((405, 94), clicks[-1][:2])
        self.assertFalse(any(
            "visit row=(365, 289)" in line for line in logs
        ))


if __name__ == "__main__":
    unittest.main()
