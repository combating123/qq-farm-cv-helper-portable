import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_reconciler():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef)
        and item.name == "_qqfarm_reconcile_visible_self_surface"
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_qqfarm_reconcile_visible_self_surface"], namespace


class FriendTransitionGrace20260923Tests(unittest.TestCase):
    def test_transient_nonfarm_frame_keeps_pending_friend_entry(self):
        reconcile, namespace = load_reconciler()
        logs = []
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_verified_surface="friend-list",
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_live_scene_hint="friend-list",
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
        )

        namespace.update({
            "_friend_guard_friend_ui_state": lambda _frame: False,
            "_friend_list_visit_button_rows": lambda _frame: [],
            "_friend_selected_carousel_card_bounds": lambda _frame: None,
            "_friend_watchdog_now": lambda: 101.0,
            "_write": lambda message: logs.append(str(message)),
            "_throttled_write": lambda *args, **kwargs: logs.append(
                str(args[1] if len(args) > 1 else args)
            ),
            "_qqfarm_clear_friend_list_frame_cache": lambda: logs.append(
                "cache-cleared"
            ),
            "_qqfarm_set_live_scene_hint": lambda owner, scene_hint: setattr(
                owner, "_qqfarm_live_scene_hint", scene_hint
            ),
        })

        released = reconcile(context, object(), False)

        self.assertFalse(released)
        self.assertTrue(context._qqfarm_friend_entry_pending)
        self.assertTrue(context._qqfarm_friend_chain_pending)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)
        self.assertEqual("friend", context._qqfarm_cycle_branch_hint)
        self.assertFalse(any("v499 visible self surface released" in line for line in logs))
        self.assertNotIn("cache-cleared", logs)

    def test_click_transition_marker_survives_an_intermediate_legacy_clear(self):
        """A legacy route may clear pending before the next self-surface probe.

        The click itself is still the strongest local evidence that the current
        frame is an asynchronous friend transition.  The reconciler must keep
        the route bounded instead of immediately reopening home and row zero.
        """
        reconcile, namespace = load_reconciler()
        logs = []
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_entry_clicked_ts=100.0,
            _qqfarm_friend_entry_verified_surface="",
            _qqfarm_friend_entry_transition_marker_ts=100.0,
            _qqfarm_friend_entry_transition_marker_surface="friend-list",
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_live_scene_hint="home",
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
        )

        namespace.update({
            "_friend_guard_friend_ui_state": lambda _frame: False,
            "_friend_list_visit_button_rows": lambda _frame: [],
            "_friend_selected_carousel_card_bounds": lambda _frame: None,
            "_friend_watchdog_now": lambda: 101.0,
            "_write": lambda message: logs.append(str(message)),
            "_throttled_write": lambda *args, **kwargs: logs.append(
                str(args[1] if len(args) > 1 else args)
            ),
            "_qqfarm_clear_friend_list_frame_cache": lambda: logs.append(
                "cache-cleared"
            ),
            "_qqfarm_set_live_scene_hint": lambda owner, scene_hint: setattr(
                owner, "_qqfarm_live_scene_hint", scene_hint
            ),
        })

        released = reconcile(context, object(), False)

        self.assertFalse(released)
        self.assertEqual("friend-list", context._qqfarm_live_scene_hint)
        self.assertTrue(context._qqfarm_friend_entry_pending)
        self.assertFalse(any("v499 visible self surface released" in line for line in logs))
        self.assertNotIn("cache-cleared", logs)


if __name__ == "__main__":
    unittest.main()
