import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in set(names)
    ]
    missing = set(names) - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v481_friend_no_progress"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_wrapper():
    return load_functions(
        "_wrap_native_v225_friend_help_candidate_cache"
    )["_wrap_native_v225_friend_help_candidate_cache"]


class FriendNoProgressGuard20260906Tests(unittest.TestCase):
    def test_runtime_info_rewrites_optimistic_friend_progress_log(self):
        namespace = load_functions(
            "_rewrite_pending_friend_help_log_message",
            "_rewrite_verified_share_failure_log_message",
            "_rewrite_fertilizer_execution_log_message",
            "_rewrite_unverified_planting_log_message",
            "_rewrite_entitlement_log_message",
            "_install_runtime_log_patch",
        )
        emitted = []

        class Logger:
            def info(self, message, *args, **kwargs):
                emitted.append(str(message))

            def warning(self, message, *args, **kwargs):
                emitted.append(str(message))

        class FarmBotCV:
            _qqfarm_native_friend_help_action_pending = True

            def emit(self):
                Logger().info(
                    "好友农场快捷帮忙：已在底部入口目标好友页执行一键务农，累计处理 3/12"
                )

        fake_logging = types.SimpleNamespace(Logger=Logger)
        namespace.update({
            "sys": types.SimpleNamespace(modules={"logging": fake_logging}),
            "_RUNTIME_LOG_PATCHED": False,
            "_write": lambda _message: None,
            "_runtime_patrol_rescue_transition": lambda *_args: None,
            "_note_runtime_cycle_branch": lambda *_args: None,
            "_note_runtime_daily_task_outcome": lambda *_args: None,
            "_note_runtime_single_harvest_outcome": lambda *_args: None,
            "_note_runtime_planting_outcome": lambda *_args: None,
            "_runtime_business_switch_snapshot": lambda _context: "",
            "__import__": __import__,
        })
        self.assertTrue(namespace["_install_runtime_log_patch"]())

        FarmBotCV().emit()
        self.assertEqual(1, len(emitted))
        self.assertIn("等待新画面确认", emitted[0])
        self.assertNotIn("累计处理 3/12", emitted[0])

    def test_same_friend_without_page_change_is_not_reinvoked_or_advanced(self):
        wrapper_factory = load_wrapper()
        frame = types.SimpleNamespace(identity="friend-A", shape=(800, 428, 3))
        events = []

        class FarmBotCV:
            def __init__(self):
                self._qqfarm_friend_list_visit_cursor = 2
                self._qqfarm_friend_list_pending_cursor = 2
                self._qqfarm_friend_chain_count = 2

        def native_process(bot):
            events.append("native-process")
            bot._qqfarm_friend_list_visit_cursor = 3
            bot._qqfarm_friend_list_pending_cursor = 3
            bot._qqfarm_friend_chain_count = 3
            return "native-result"

        wrapper_factory.__globals__.update({
            "_qqfarm_native_friend_help_durable_snapshot": (
                lambda _bot: 687
            ),
            "_qqfarm_capture_native_friend_help_frame": (
                lambda _bot: frame
            ),
            "_friend_guard_help_button_match": (
                lambda _frame: {"matched": True}
            ),
            "_qqfarm_native_friend_help_card_signature": (
                lambda current: current.identity
            ),
            "_write": events.append,
        })
        wrapped, changed = wrapper_factory(
            native_process,
            "FarmBotCV.process_friend_farm",
        )
        self.assertTrue(changed)

        bot = FarmBotCV()
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(["native-process"], events[:1])
        self.assertEqual(2, bot._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, bot._qqfarm_friend_list_pending_cursor)
        self.assertEqual(2, bot._qqfarm_friend_chain_count)

        self.assertFalse(wrapped(bot))
        self.assertEqual(["native-process"], [
            item for item in events if item == "native-process"
        ])
        self.assertEqual(2, bot._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, bot._qqfarm_friend_list_pending_cursor)
        self.assertEqual(2, bot._qqfarm_friend_chain_count)
        self.assertTrue(any(
            "same-page unconfirmed" in str(item)
            for item in events
        ))

    def test_new_friend_signature_releases_same_page_guard(self):
        wrapper_factory = load_wrapper()
        frames = [
            types.SimpleNamespace(identity="friend-A", shape=(800, 428, 3))
        ]
        events = []

        class FarmBotCV:
            def __init__(self):
                self._qqfarm_friend_list_visit_cursor = 2
                self._qqfarm_friend_list_pending_cursor = 2

        def native_process(bot):
            events.append("native-process")
            bot._qqfarm_friend_list_visit_cursor += 1
            return "native-result"

        wrapper_factory.__globals__.update({
            "_qqfarm_native_friend_help_durable_snapshot": (
                lambda _bot: 687
            ),
            "_qqfarm_capture_native_friend_help_frame": (
                lambda _bot: frames[0]
            ),
            "_friend_guard_help_button_match": (
                lambda _frame: {"matched": True}
            ),
            "_qqfarm_native_friend_help_card_signature": (
                lambda current: current.identity
            ),
            "_write": events.append,
        })
        wrapped, _ = wrapper_factory(
            native_process,
            "FarmBotCV.process_friend_farm",
        )
        bot = FarmBotCV()
        self.assertEqual("native-result", wrapped(bot))
        self.assertFalse(wrapped(bot))
        self.assertEqual(1, events.count("native-process"))

        frames[0] = types.SimpleNamespace(
            identity="friend-B", shape=(800, 428, 3)
        )
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(2, events.count("native-process"))

    def test_pending_native_logs_are_rewritten_until_page_proof_arrives(self):
        namespace = load_functions(
            "_rewrite_pending_friend_help_log_message"
        )
        rewrite = namespace["_rewrite_pending_friend_help_log_message"]
        context = types.SimpleNamespace(
            _qqfarm_native_friend_help_action_pending=True
        )

        message, changed = rewrite(
            "好友农场快捷帮忙：已在底部入口目标好友页执行一键务农，累计处理 3/12",
            context,
        )
        self.assertTrue(changed)
        self.assertIn("等待新画面确认", message)
        self.assertNotIn("累计处理 3/12", message)

    def test_friend_poll_rolls_back_claimed_progress_when_frame_is_unchanged(self):
        namespace = load_functions(
            "_friend_guard_visual_stability_signature",
            "_wrap_friend_guard_continuous_poll_func",
        )
        namespace["_friend_guard_visual_stability_signature"] = (
            lambda frame: getattr(frame, "identity", None)
        )
        frames = [
            types.SimpleNamespace(identity="friend-A"),
            types.SimpleNamespace(identity="friend-A"),
        ]
        events = []

        class FarmBotCV:
            def __init__(self):
                self._qqfarm_friend_list_visit_cursor = 2
                self._qqfarm_friend_list_pending_cursor = 2
                self._qqfarm_friend_chain_count = 2
                self._qqfarm_friend_action_last_ts = 10.0
                self._qqfarm_friend_action_last_label = ""
                self._qqfarm_friend_chain_last_nav_label = ""
                self._qqfarm_friend_entry_clicked_ts = 10.0
                self._qqfarm_friend_entry_pending = False
                self._qqfarm_friend_chain_pending = False
                self._qqfarm_friend_chain_active = False
                self._qqfarm_friend_chain_exhausted = False
                self._qqfarm_friend_chain_allow_home = False

        def native_process(bot):
            events.append("native-process")
            bot._qqfarm_friend_list_visit_cursor = 3
            bot._qqfarm_friend_list_pending_cursor = 3
            bot._qqfarm_friend_chain_count = 3
            bot._qqfarm_friend_action_last_ts = 11.0
            bot._qqfarm_friend_entry_clicked_ts = 11.0
            return True

        namespace.update({
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_get_frame_from_bot": lambda _bot: frames.pop(0),
            "_qqfarm_native_friend_help_durable_snapshot": lambda _bot: 687,
            "_friend_guard_poll_dispatch_allowed": lambda _context: True,
            "_qqfarm_home_priority_active": lambda _context: False,
            "_throttled_write": events.append,
            "_write": events.append,
            "_friend_guard_sleep": lambda _seconds: None,
        })
        wrapped, changed = namespace["_wrap_friend_guard_continuous_poll_func"](
            native_process,
            "fixture.process_friend_farm",
        )
        bot = FarmBotCV()

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot))
        self.assertEqual(["native-process"], [
            item for item in events if item == "native-process"
        ])
        self.assertEqual(2, bot._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, bot._qqfarm_friend_list_pending_cursor)
        self.assertEqual(2, bot._qqfarm_friend_chain_count)
        self.assertTrue(any(
            "v482 friend dispatch visual unconfirmed" in str(item)
            for item in events
        ))

    def test_friend_poll_rolls_back_claimed_progress_when_capture_has_no_proof(self):
        namespace = load_functions(
            "_friend_guard_visual_stability_signature",
            "_wrap_friend_guard_continuous_poll_func",
        )
        namespace["_friend_guard_visual_stability_signature"] = lambda _frame: None
        events = []

        class FarmBotCV:
            def __init__(self):
                self._qqfarm_friend_list_visit_cursor = 2
                self._qqfarm_friend_list_pending_cursor = 2
                self._qqfarm_friend_chain_count = 2

        def native_process(bot):
            events.append("native-process")
            bot._qqfarm_friend_list_visit_cursor = 3
            bot._qqfarm_friend_list_pending_cursor = 3
            bot._qqfarm_friend_chain_count = 3
            return True

        namespace.update({
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_get_frame_from_bot": lambda _bot: None,
            "_qqfarm_native_friend_help_durable_snapshot": lambda _bot: 687,
            "_friend_guard_poll_dispatch_allowed": lambda _context: True,
            "_qqfarm_home_priority_active": lambda _context: False,
            "_write": events.append,
        })
        wrapped, changed = namespace["_wrap_friend_guard_continuous_poll_func"](
            native_process,
            "fixture.process_friend_farm",
        )
        bot = FarmBotCV()

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot))
        self.assertEqual(["native-process"], [
            item for item in events if item == "native-process"
        ])
        self.assertEqual(2, bot._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, bot._qqfarm_friend_list_pending_cursor)
        self.assertEqual(2, bot._qqfarm_friend_chain_count)
        self.assertTrue(any(
            "v482 friend dispatch visual unconfirmed" in str(item)
            for item in events
        ))

    def test_runtime_info_uses_active_cycle_context_when_stack_has_no_bot(self):
        namespace = load_functions(
            "_rewrite_pending_friend_help_log_message",
            "_rewrite_verified_share_failure_log_message",
            "_rewrite_fertilizer_execution_log_message",
            "_rewrite_unverified_planting_log_message",
            "_rewrite_entitlement_log_message",
            "_install_runtime_log_patch",
        )
        emitted = []

        class Logger:
            def info(self, message, *args, **kwargs):
                emitted.append(str(message))

            def warning(self, message, *args, **kwargs):
                emitted.append(str(message))

        context = type("FarmBotCV", (), {
            "_qqfarm_native_friend_help_action_pending": True,
        })()
        fake_logging = types.SimpleNamespace(Logger=Logger)
        namespace.update({
            "sys": types.SimpleNamespace(modules={"logging": fake_logging}),
            "_RUNTIME_LOG_PATCHED": False,
            "_ACTIVE_RUN_CYCLE_CONTEXT": context,
            "_write": lambda _message: None,
            "_runtime_patrol_rescue_transition": lambda *_args: None,
            "_note_runtime_cycle_branch": lambda *_args: None,
            "_note_runtime_daily_task_outcome": lambda *_args: None,
            "_note_runtime_single_harvest_outcome": lambda *_args: None,
            "_note_runtime_planting_outcome": lambda *_args: None,
            "_runtime_business_switch_snapshot": lambda _context: "",
            "__import__": __import__,
        })
        self.assertTrue(namespace["_install_runtime_log_patch"]())

        Logger().info(
            "好友农场快捷帮忙：已在底部入口目标好友页执行一键务农，累计处理 3/12"
        )
        self.assertEqual(1, len(emitted))
        self.assertIn("等待新画面确认", emitted[0])
        self.assertNotIn("累计处理 3/12", emitted[0])


if __name__ == "__main__":
    unittest.main()
