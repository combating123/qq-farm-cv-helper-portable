import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError("missing hook functions: " + repr(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class HiddenStaleSelfActionAndFriendLoopTests(unittest.TestCase):
    def test_recent_self_action_without_signature_is_deferred(self):
        namespace = load_functions("_qqfarm_self_action_should_defer")
        bot = types.SimpleNamespace(
            self_action_confirmation_cooldown_seconds=18.0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_post_harvest_pending=False,
            _qqfarm_single_harvest_planting_pending=False,
            _qqfarm_self_action_last_ts=100.0,
            _qqfarm_self_action_last_frame_signature=None,
        )
        self.assertTrue(
            namespace["_qqfarm_self_action_should_defer"](
                bot, None, now_ts=110.0
            )
        )

    def test_hidden_restore_or_missing_frame_is_not_action_ready(self):
        namespace = load_functions("_qqfarm_self_action_capture_ready")
        ready = namespace["_qqfarm_self_action_capture_ready"]
        bot = types.SimpleNamespace()
        namespace.update({
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_LEASE_UNTIL": 0.0,
            "_QQFARM_WGC_STATE": "ready",
            "_QQFARM_WGC_SESSION_READY": True,
        })
        self.assertFalse(ready(bot, object(), now_ts=100.0))

        namespace["_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME"] = False
        namespace["_QQFARM_WGC_STATE"] = "pending"
        namespace["_QQFARM_WGC_SESSION_READY"] = False
        self.assertFalse(ready(bot, None, now_ts=100.0))

        namespace["_QQFARM_WGC_STATE"] = "ready"
        namespace["_QQFARM_WGC_SESSION_READY"] = True
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        self.assertTrue(ready(bot, frame, now_ts=100.0))

    def test_qq_self_action_rejects_passed_frame_not_owned_by_latest_capture(self):
        namespace = load_functions("_qqfarm_self_action_capture_ready")
        ready = namespace["_qqfarm_self_action_capture_ready"]
        bot = types.SimpleNamespace()
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_QQFARM_WGC_STATE": "ready",
            "_QQFARM_WGC_SESSION_READY": True,
            "_QQFARM_LAST_VISIBLE_CAPTURE_FRAME_ID": id(object()),
            "_QQFARM_LAST_PHYSICAL_PRINTWINDOW_FRAME_ID": 0,
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": None,
            "_qqfarm_capture_frame_has_rendered_pixels": lambda _frame: True,
        })
        self.assertFalse(ready(bot, frame, now_ts=100.0, fresh_capture=True))

    def test_self_wrapper_does_not_call_native_during_hidden_restore(self):
        namespace = load_functions(
            "_wrap_vip_business_func",
            "_qqfarm_self_action_capture_ready",
            "_qqfarm_self_action_should_defer",
            "_qqfarm_record_self_action_frame",
        )
        calls = []
        logs = []
        context = types.SimpleNamespace()

        def native(*_args, **_kwargs):
            calls.append("native")
            return True

        namespace.update({
            "_friend_guard_context": lambda _args, _kwargs: context,
            "_stop_requested_in_args": lambda _args, _kwargs: False,
            "_force_vip_business_args": lambda _args, _kwargs: 0,
            "_enter_vip_entitlement_context": lambda *_args: [],
            "_restore_vip_entitlement_context": lambda *_args: 0,
            "_get_frame_from_bot": lambda _context: None,
            "_QQFARM_HIDDEN_RESTORE_WAITING_FOR_FRESH_FRAME": True,
            "_QQFARM_HIDDEN_RESTORE_LEASE_UNTIL": 0.0,
            "_QQFARM_WGC_STATE": "ready",
            "_QQFARM_WGC_SESSION_READY": True,
            "_write": logs.append,
            "_throttled_write": lambda *args: logs.append(str(args)),
        })
        wrapped, changed = namespace["_wrap_vip_business_func"](
            native, "bot.process_self_farm"
        )
        self.assertTrue(changed)
        self.assertFalse(wrapped(context))
        self.assertEqual([], calls)

    def test_friend_next_entry_keeps_cooldown_across_same_frame_dispatches(self):
        namespace = load_functions(
            "_invoke_friend_next_actionable_entry",
            "_qqfarm_friend_next_entry_dispatch_allowed",
            "_qqfarm_record_friend_next_entry_dispatch",
        )
        calls = []
        frame = types.SimpleNamespace(shape=(800, 428, 3), identity="friend-A")
        context = types.SimpleNamespace(
            enable_friend_help=True,
            enable_friend_steal=False,
            check_friend_farm_bottom_help_all_entry=lambda *_args: calls.append(
                "help"
            ) or True,
            _qqfarm_friend_next_entry_pending_identity=None,
            _qqfarm_friend_next_entry_cooldown_until=0.0,
            _qqfarm_friend_next_entry_retry_count=0,
            _qqfarm_friend_next_entry_last_dispatch_ts=0.0,
        )
        namespace.update({
            "_friend_navigation_frame_without_selected_card": lambda value: value,
            "_invoke_friend_guard_action": (
                lambda action, target, original_args, original_kwargs:
                action(*original_args, **(original_kwargs or {}))
            ),
            "_qqfarm_friend_navigation_identity": (
                lambda value: {"card": value.identity, "page": value.identity}
            ),
            "_friend_guard_poll_now": lambda: 100.0,
            "_write": lambda _message: None,
        })

        first = namespace["_invoke_friend_next_actionable_entry"](
            context, frame, ""
        )
        second = namespace["_invoke_friend_next_actionable_entry"](
            context, frame, ""
        )
        self.assertEqual((True, "method.check_friend_farm_bottom_help_all_entry"), first)
        self.assertEqual((False, ""), second)
        self.assertEqual(["help"], calls)

    def test_new_friend_chain_only_clears_exhausted_navigation_budget(self):
        namespace = load_functions("_friend_chain_begin_dispatch")
        context = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_dispatch_depth=0,
            _qqfarm_friend_next_entry_pending_identity={"card": "friend-A"},
            _qqfarm_friend_next_entry_cooldown_until=999.0,
            _qqfarm_friend_next_entry_retry_count=1,
        )
        self.assertTrue(namespace["_friend_chain_begin_dispatch"](context))
        self.assertEqual(
            {"card": "friend-A"},
            context._qqfarm_friend_next_entry_pending_identity,
        )
        self.assertEqual(999.0, context._qqfarm_friend_next_entry_cooldown_until)
        self.assertEqual(1, context._qqfarm_friend_next_entry_retry_count)


if __name__ == "__main__":
    unittest.main()
