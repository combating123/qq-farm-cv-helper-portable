import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*wanted):
    tree = ast.parse(HOOK.read_text(encoding="utf-8-sig"), filename=str(HOOK))
    wanted = set(wanted)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError(f"hook.py is missing: {sorted(missing)}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"_write": lambda *_args, **_kwargs: None}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class SamePageFriendRetryTests(unittest.TestCase):
    def test_same_selected_friend_gets_one_alternate_visual_retry(self):
        ns = load_functions("_qqfarm_same_page_recovery_needed", "_qqfarm_arm_same_page_recovery")
        calls = []

        class Context:
            _qqfarm_friend_same_page_recovery_count = 0
            _qqfarm_friend_list_visit_cursor = 1
            _qqfarm_friend_action_confirmation_pending = True
            _qqfarm_friend_action_confirmation_retries = 1
            _qqfarm_friend_action_cooldown_until = 200.0
            _qqfarm_friend_native_action_unverified = True

        context = Context()
        frame = object()
        ns.update({
            "_qqfarm_invalidate_wgc_frame_cache": lambda _reason: None,
            "_get_frame_from_bot": lambda _owner: frame,
            "_qqfarm_native_friend_help_card_signature": lambda _frame: ("friend", 1),
            "_qqfarm_visible_friend_action_recovery": lambda owner, fresh: (calls.append((owner, fresh)) or (False, "no-action")),
        })
        previous = {"unconfirmed": True, "signature": ("friend", 1), "durable_before": 7, "same_page_count": 1}

        self.assertTrue(ns["_qqfarm_arm_same_page_recovery"](
            context, {"_qqfarm_friend_list_visit_cursor": 1}, previous,
            ("friend", 1), 7, threshold=2,
        ))
        self.assertEqual([(context, frame)], calls)
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(context._qqfarm_friend_action_confirmation_pending)
        self.assertTrue(context._qqfarm_friend_native_action_unverified)
        self.assertTrue(context._qqfarm_native_friend_help_no_progress_guard["unconfirmed"])

    def test_same_page_retry_is_not_repeated_for_same_signature(self):
        ns = load_functions("_qqfarm_same_page_recovery_needed", "_qqfarm_arm_same_page_recovery")
        calls = []

        class Context:
            _qqfarm_friend_same_page_recovery_count = 1
            _qqfarm_friend_same_page_retry_signature = ("friend", 1)
            _qqfarm_friend_list_visit_cursor = 1

        context = Context()
        ns.update({
            "_qqfarm_invalidate_wgc_frame_cache": lambda _reason: None,
            "_get_frame_from_bot": lambda _owner: object(),
            "_qqfarm_native_friend_help_card_signature": lambda _frame: ("friend", 1),
            "_qqfarm_visible_friend_action_recovery": lambda *_args: calls.append(True),
        })
        previous = {"unconfirmed": True, "signature": ("friend", 1), "durable_before": 7, "same_page_count": 1}

        self.assertTrue(ns["_qqfarm_arm_same_page_recovery"](
            context, {"_qqfarm_friend_list_visit_cursor": 1}, previous,
            ("friend", 1), 7, threshold=2,
        ))
        self.assertEqual([], calls)
        self.assertTrue(context._qqfarm_native_friend_help_no_progress_guard["unconfirmed"])

    def test_durable_growth_rearms_retry_budget_for_later_action(self):
        ns = load_functions("_qqfarm_same_page_recovery_needed")

        class Context:
            _qqfarm_friend_same_page_retry_signature = ("friend", 1)
            _qqfarm_friend_same_page_recovery_count = 1
            _qqfarm_friend_same_page_count = 4

        context = Context()
        previous = {"unconfirmed": True, "signature": ("friend", 1), "durable_before": 7}

        self.assertFalse(ns["_qqfarm_same_page_recovery_needed"](
            context, previous, ("friend", 1), 8, threshold=2,
        ))
        self.assertIsNone(context._qqfarm_friend_same_page_retry_signature)
        self.assertEqual(0, context._qqfarm_friend_same_page_recovery_count)


if __name__ == "__main__":
    unittest.main()
