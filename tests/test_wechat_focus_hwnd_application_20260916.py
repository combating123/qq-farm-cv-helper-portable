import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_focus_wrappers(find_hwnd):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {
        "_wechat_focus_coerce_hwnd",
        "_wechat_focus_owner_from_args",
        "_wechat_focus_hwnd_from_owner",
        "_wechat_focus_set_owner_hwnd",
        "_wechat_focus_prepare_call",
        "_wechat_focus_reason_from_call",
        "_wechat_focus_applied_hwnd",
        "_wechat_focus_emit_enabled",
        "_wechat_focus_emit_applied",
        "_wechat_focus_apply_proved",
        "_wechat_focus_select_window_candidate",
        "_wrap_apply_wechat_focus_after_hwnd",
        "_wrap_wechat_focus_guard",
    }
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    runtime_messages = []
    hook_messages = []
    namespace = {
        "_active_is_weixin_mode": lambda: True,
        "_wechat_focus_enabled": lambda: True,
        "_stop_requested_in_args": lambda _args, _kwargs: False,
        "_stop_gate_return": lambda _name: False,
        "_find_wechat_hwnd": find_hwnd,
        "_runtime_info_once": (
            lambda key, message: runtime_messages.append((key, message))
        ),
        "_write": hook_messages.append,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["runtime_messages"] = runtime_messages
    namespace["hook_messages"] = hook_messages
    return namespace


class WechatFocusHwndApplicationTests(unittest.TestCase):
    def test_window_selector_prefers_known_wechat_process_and_farm_title(self):
        ns = load_focus_wrappers(lambda: 0)
        selector = ns.get("_wechat_focus_select_window_candidate")
        self.assertIsNotNone(selector)
        selected = selector([
            {
                "hwnd": 101,
                "process_name": "chrome.exe",
                "title": "微信",
                "class_name": "Chrome_WidgetWin_1",
                "visible": True,
                "area": 2_000_000,
            },
            {
                "hwnd": 202,
                "process_name": "WeChatAppEx.exe",
                "title": "QQ经典农场",
                "class_name": "Chrome_WidgetWin_1",
                "visible": False,
                "area": 300_000,
            },
            {
                "hwnd": 303,
                "process_name": "Weixin.exe",
                "title": "微信主窗口",
                "class_name": "Chrome_WidgetWin_1",
                "visible": True,
                "area": 5_000_000,
            },
        ])
        self.assertEqual(202, selected)

    def test_window_selector_prefers_bound_capture_hwnd_when_windows_are_ambiguous(self):
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 401,
                "process_name": "WeChatAppEx.exe",
                "title": "微信主窗口",
                "class_name": "Chrome_WidgetWin_1",
                "visible": True,
                "area": 4_000_000,
            },
            {
                "hwnd": 402,
                "process_name": "WeChatAppEx.exe",
                "title": "",
                "class_name": "Chrome_WidgetWin_1",
                "visible": False,
                "area": 120_000,
            },
        ], preferred_hwnd=402)
        self.assertEqual(402, selected)

    def test_ensure_wrapper_binds_discovered_hwnd_before_native_apply(self):
        ns = load_focus_wrappers(lambda: 0x1234)
        observed = []

        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            _wechat_focus_guard_applied_hwnd=0,
            _wechat_focus_guard_attempted_hwnd=0,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            observed.append((target.screen_capture.bound_hwnd, reason))
            target._wechat_focus_guard_attempted_hwnd = (
                target.screen_capture.bound_hwnd
            )
            target._wechat_focus_guard_applied_hwnd = (
                target.screen_capture.bound_hwnd
            )
            return True

        wrapped, changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )
        result = wrapped(owner, reason="开始运行/窗口已存在")

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual([(0x1234, "开始运行/窗口已存在")], observed)
        self.assertEqual(0x1234, owner.screen_capture.bound_hwnd)
        messages = [message for _key, message in ns["runtime_messages"]]
        self.assertTrue(any(
            "微信抢鼠标处理已启用：hwnd=0x00001234" in message
            for message in messages
        ))
        self.assertTrue(any(
            "微信抢鼠标处理已应用：hwnd=4660" in message
            and "reason=开始运行/窗口已存在" in message
            for message in messages
        ))

    def test_apply_wrapper_replaces_zero_hwnd_with_bound_window(self):
        ns = load_focus_wrappers(lambda: 0)
        observed = []
        owner = types.SimpleNamespace(
            bound_hwnd=0x2233,
            _wechat_focus_guard_applied_hwnd=0,
        )

        def apply_after_hwnd_ready(target, hwnd, reason=""):
            observed.append((hwnd, reason))
            target._wechat_focus_guard_applied_hwnd = hwnd
            return True

        wrapped, changed = ns["_wrap_apply_wechat_focus_after_hwnd"](
            apply_after_hwnd_ready,
            "bot._apply_wechat_focus_guard_after_hwnd_ready",
        )
        result = wrapped(owner, 0, "开始运行/窗口已存在")

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual([(0x2233, "开始运行/窗口已存在")], observed)
        self.assertTrue(any(
            "微信抢鼠标处理已应用：hwnd=8755" in message
            for _key, message in ns["runtime_messages"]
        ))

    def test_failed_native_apply_is_not_reported_as_applied(self):
        ns = load_focus_wrappers(lambda: 0x3344)
        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            _wechat_focus_guard_applied_hwnd=0,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            return False

        wrapped, _changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )
        self.assertFalse(wrapped(owner, reason="开始运行/窗口已存在"))
        self.assertFalse(any(
            "微信抢鼠标处理已应用" in message
            for _key, message in ns["runtime_messages"]
        ))

    def test_none_result_is_applied_only_when_native_state_records_hwnd(self):
        ns = load_focus_wrappers(lambda: 0x4455)
        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            _wechat_focus_guard_applied_hwnd=0,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            target._wechat_focus_guard_applied_hwnd = (
                target.screen_capture.bound_hwnd
            )
            return None

        wrapped, _changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )
        self.assertIsNone(wrapped(owner, reason="开始运行/窗口已存在"))
        self.assertTrue(any(
            "微信抢鼠标处理已应用：hwnd=17493" in message
            for _key, message in ns["runtime_messages"]
        ))


if __name__ == "__main__":
    unittest.main()
