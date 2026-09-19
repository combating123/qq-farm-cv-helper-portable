import ast
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
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V500TerminalFriendListHomeRecovery20260919Tests(unittest.TestCase):
    def test_terminal_close_dispatches_bounded_home_recovery_before_native_return(self):
        namespace = load_functions(
            "_wrap_native_v225_friend_help_candidate_cache",
        )
        list_frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (365, 289 + (94 * index))}
            for index in range(5)
        ]
        recovery_calls = []
        native_calls = []
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: list_frame
                ),
                "_friend_list_visit_button_rows": lambda _frame: rows,
                "_friend_guard_friend_ui_state": lambda _frame: None,
                "_handle_friend_list_surface": (
                    lambda owner, frame: "closed-terminal-latch"
                ),
                "_recover_home_after_friend_list_terminal": (
                    lambda owner, result, frame, original, args, kwargs: (
                        recovery_calls.append(
                            (owner, result, frame, original, args, kwargs)
                        )
                        or True
                    )
                ),
                "_throttled_write": lambda *_args, **_kwargs: None,
                "_write": lambda _message: None,
            }
        )
        context = types.SimpleNamespace()

        def native_process_friend(owner, *_args, **_kwargs):
            native_calls.append(owner)
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        result = wrapped(context, "ignored-native-argument")

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual(1, len(recovery_calls))
        self.assertIs(context, recovery_calls[0][0])
        self.assertEqual("closed-terminal-latch", recovery_calls[0][1])
        self.assertIs(list_frame, recovery_calls[0][2])
        self.assertIs(native_process_friend, recovery_calls[0][3])
        self.assertEqual(("ignored-native-argument",), recovery_calls[0][4])
        self.assertEqual({}, recovery_calls[0][5])
        self.assertEqual([], native_calls)

    def test_close_releases_latch_only_after_fresh_self_surface(self):
        namespace = load_functions(
            "_recover_home_after_friend_list_terminal",
        )
        frame = object()
        releases = []
        clicks = []
        logs = []
        namespace.update(
            {
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: frame
                ),
                "_friend_guard_friend_ui_state": lambda candidate: (
                    False if candidate is frame else None
                ),
                "_qqfarm_reconcile_visible_self_surface": (
                    lambda owner, candidate, state: (
                        releases.append((owner, candidate, state)) or True
                    )
                ),
                "_invoke_friend_guard_home_coordinate_click": (
                    lambda *_args: clicks.append(True) or True
                ),
                "_write": lambda message: logs.append(str(message)),
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_terminal_home_recovery_attempts=0,
        )

        result = namespace["_recover_home_after_friend_list_terminal"](
            context, "closed-terminal-latch", types.SimpleNamespace(), None, (), {}
        )

        self.assertTrue(result)
        self.assertEqual(1, len(releases))
        self.assertEqual([], clicks)
        self.assertFalse(context._qqfarm_friend_terminal_home_recovery_pending)
        self.assertEqual(0, context._qqfarm_friend_terminal_home_recovery_attempts)
        self.assertTrue(any("already reached verified self" in line for line in logs))

    def test_friend_surface_uses_one_home_click_then_verifies_self(self):
        namespace = load_functions(
            "_recover_home_after_friend_list_terminal",
        )
        friend_frame = object()
        home_frame = object()
        frames = iter((friend_frame, home_frame))
        clicks = []
        releases = []
        namespace.update(
            {
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: next(frames)
                ),
                "_friend_guard_friend_ui_state": lambda candidate: (
                    True if candidate is friend_frame else False
                ),
                "_invoke_friend_guard_home_coordinate_click": (
                    lambda owner, candidate: clicks.append((owner, candidate)) or True
                ),
                "_qqfarm_reconcile_visible_self_surface": (
                    lambda owner, candidate, state: (
                        releases.append((owner, candidate, state)) or True
                    )
                ),
                "_write": lambda _message: None,
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        context = types.SimpleNamespace()

        result = namespace["_recover_home_after_friend_list_terminal"](
            context, "closed", types.SimpleNamespace(), None, (), {}
        )

        self.assertTrue(result)
        self.assertEqual(1, len(clicks))
        self.assertIs(friend_frame, clicks[0][1])
        self.assertEqual(1, len(releases))
        self.assertIs(home_frame, releases[0][1])
        self.assertFalse(context._qqfarm_friend_terminal_home_recovery_pending)

    def test_unconfirmed_home_is_bounded_and_not_clicked_twice_in_one_interval(self):
        namespace = load_functions(
            "_recover_home_after_friend_list_terminal",
        )
        friend_frame = object()
        frames = iter((friend_frame, friend_frame, friend_frame, friend_frame, friend_frame))
        clicks = []
        namespace.update(
            {
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _owner: next(frames)
                ),
                "_friend_guard_friend_ui_state": lambda _candidate: True,
                "_invoke_friend_guard_home_coordinate_click": (
                    lambda *_args: clicks.append(True) or True
                ),
                "_write": lambda _message: None,
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        context = types.SimpleNamespace()

        first = namespace["_recover_home_after_friend_list_terminal"](
            context, "closed-terminal-latch", types.SimpleNamespace(), None, (), {}
        )
        second = namespace["_recover_home_after_friend_list_terminal"](
            context, "closed-terminal-latch", types.SimpleNamespace(), None, (), {}
        )

        self.assertFalse(first)
        self.assertFalse(second)
        self.assertEqual(1, len(clicks))
        self.assertTrue(context._qqfarm_friend_terminal_home_recovery_pending)


if __name__ == "__main__":
    unittest.main()
