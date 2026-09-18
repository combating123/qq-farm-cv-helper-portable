import ast
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


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


class V490FriendListProgressAndChildClick20260918Tests(unittest.TestCase):
    def test_occluded_qq_window_posts_click_to_render_child(self):
        namespace = load_functions(
            "_friend_guard_scale_point_to_client",
            "_friend_guard_post_client_click",
        )
        messages = []
        root_hwnd = 100
        render_hwnd = 200
        overlay_hwnd = 999

        fake_win32gui = types.SimpleNamespace()
        fake_win32gui.EnumWindows = lambda callback, extra: callback(root_hwnd, extra)
        fake_win32gui.EnumChildWindows = (
            lambda hwnd, callback, extra: callback(render_hwnd, extra)
        )
        fake_win32gui.IsWindowVisible = lambda hwnd: hwnd in (root_hwnd, render_hwnd)
        fake_win32gui.GetWindowText = (
            lambda hwnd: "QQ经典农场" if hwnd == root_hwnd else "Chrome Legacy Window"
        )
        fake_win32gui.GetClassName = (
            lambda hwnd: "Chrome_RenderWidgetHostHWND" if hwnd == render_hwnd else ""
        )
        fake_win32gui.GetClientRect = lambda _hwnd: (0, 0, 428, 800)
        fake_win32gui.ClientToScreen = (
            lambda _hwnd, point: (int(point[0]) + 5, int(point[1]) + 5)
        )
        fake_win32gui.WindowFromPoint = lambda _point: overlay_hwnd
        fake_win32gui.IsChild = lambda parent, child: (
            parent == root_hwnd and child == render_hwnd
        )
        fake_win32gui.ScreenToClient = (
            lambda hwnd, point: (
                int(point[0]) - 5,
                int(point[1]) - 5,
            ) if hwnd in (root_hwnd, render_hwnd) else point
        )
        fake_win32gui.PostMessage = (
            lambda hwnd, msg, wparam, lparam: messages.append(
                (int(hwnd), int(msg), int(wparam), int(lparam))
            ) or True
        )

        with mock.patch.dict(sys.modules, {"win32gui": fake_win32gui}):
            clicked = namespace["_friend_guard_post_client_click"](
                365, 289, 428, 800
            )

        self.assertTrue(clicked)
        self.assertEqual(3, len(messages))
        self.assertEqual({render_hwnd}, {item[0] for item in messages})

    def test_non_guard_friend_list_resumes_saved_cursor_instead_of_first_row(self):
        namespace = load_functions("_handle_friend_list_surface")
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
                "_friend_watchdog_now": lambda: 100.0,
                "_friend_progress_journal_commit": lambda *_args, **_kwargs: True,
                "_friend_guard_post_client_click": (
                    lambda *args: clicks.append(args) or True
                ),
                "_set_friend_chain_fast_interval": lambda *_args, **_kwargs: None,
                "_write": lambda message: logs.append(str(message)),
                "_throttled_write": lambda *_args, **_kwargs: None,
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=2,
            _qqfarm_friend_list_pending_cursor=2,
            _qqfarm_friend_list_resume_pending=True,
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_progress_journal_restore_attempted=True,
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("visited", result)
        self.assertEqual(rows[2]["center"], clicks[0][:2])
        self.assertEqual(5, context._qqfarm_friend_list_visible_candidate_count)
        self.assertEqual(2, context._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, context._qqfarm_friend_list_pending_cursor)
        self.assertTrue(context._qqfarm_friend_entry_pending)
        self.assertTrue(context._qqfarm_friend_chain_pending)

    def test_native_friend_owner_commits_pending_list_cursor_on_friend_farm(self):
        namespace = load_functions(
            "_wrap_native_v225_friend_help_candidate_cache",
        )
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        calls = []

        def commit(owner):
            calls.append("commit")
            owner._qqfarm_friend_list_visit_cursor = (
                owner._qqfarm_friend_list_pending_cursor + 1
            )
            return True

        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": lambda _owner: frame,
                "_friend_list_visit_button_rows": lambda _frame: [],
                "_friend_guard_friend_ui_state": lambda _frame: True,
                "_commit_friend_list_entry_transition": commit,
                "_qqfarm_native_friend_help_durable_snapshot": lambda _owner: 10,
                "_qqfarm_native_friend_help_quorum_baseline": lambda _owner: 10,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
                "_qqfarm_cache_native_v225_friend_help_candidate": (
                    lambda *_args, **_kwargs: None
                ),
                "_throttled_write": lambda *_args, **_kwargs: None,
                "_write": lambda message: calls.append(str(message)),
            }
        )
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=99.0,
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
        )

        def native(owner, *_args, **_kwargs):
            calls.append("native")
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](native, "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm")
        result = wrapped(context)

        self.assertTrue(changed)
        self.assertEqual("native-result", result)
        self.assertEqual(["commit", "native"], [
            item for item in calls if item in ("commit", "native")
        ])
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertEqual(0.0, context._qqfarm_friend_entry_clicked_ts)


if __name__ == "__main__":
    unittest.main()
