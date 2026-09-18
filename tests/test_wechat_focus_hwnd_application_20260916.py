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
        "_wechat_focus_state_snapshot",
        "_wechat_focus_prepare_call",
        "_wechat_focus_reason_from_call",
        "_wechat_focus_applied_hwnd",
        "_wechat_focus_emit_enabled",
        "_wechat_focus_emit_applied",
        "_wechat_focus_apply_proved",
        "_wechat_focus_should_enumerate_children",
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
        "_wechat_focus_process_identity": (
            lambda _hwnd: (9116, "WeChatAppEx.exe")
        ),
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
    def test_prepare_call_publishes_bound_pid_and_process_name(self):
        ns = load_focus_wrappers(lambda: 0x1234)
        owner = types.SimpleNamespace(
            bound_hwnd=0,
            bound_pid=0,
            bound_process_name="",
            screen_capture=types.SimpleNamespace(
                bound_hwnd=0,
                bound_pid=0,
                bound_process_name="",
            ),
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            return None

        args, kwargs, resolved_owner, hwnd = ns["_wechat_focus_prepare_call"](
            ensure_wechat_focus_guard_for_current_window,
            (owner,),
            {"reason": "开始运行/窗口已存在"},
        )

        self.assertIs(owner, resolved_owner)
        self.assertEqual(0x1234, hwnd)
        self.assertEqual(9116, owner.bound_pid)
        self.assertEqual("WeChatAppEx.exe", owner.bound_process_name)
        self.assertEqual(9116, owner.screen_capture.bound_pid)
        self.assertEqual("WeChatAppEx.exe", owner.screen_capture.bound_process_name)

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

    def test_window_selector_ignores_zero_area_support_window(self):
        """A zero-size helper HWND must not outrank a usable farm surface."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 501,
                "process_name": "WeChatAppEx.exe",
                "title": "QQ经典农场",
                "class_name": "Chrome_WidgetWin_0",
                "visible": False,
                "area": 0,
            },
            {
                "hwnd": 502,
                "process_name": "WeChatAppEx.exe",
                "title": "QQ经典农场",
                "class_name": "Chrome_WidgetWin_0",
                "visible": True,
                "area": 640 * 480,
            },
        ])
        self.assertEqual(502, selected)

    def test_window_selector_returns_zero_when_all_wechat_candidates_have_no_surface(self):
        """Support/helper HWNDs alone are not a capture target."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 601,
                "process_name": "WeChatAppEx.exe",
                "title": "QQ经典农场",
                "class_name": "Chrome_WidgetWin_0",
                "visible": False,
                "area": 0,
            },
            {
                "hwnd": 602,
                "process_name": "Weixin.exe",
                "title": "微信主窗口",
                "class_name": "Qt51514QWindowIcon",
                "visible": True,
                "area": 0,
            },
        ])
        self.assertEqual(0, selected)

    def test_window_selector_prefers_app_surface_over_weixin_tray_message_window(self):
        """A large hidden tray/message surface is not the Weixin app window."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 701,
                "process_name": "Weixin.exe",
                "title": "",
                "class_name": "Qt51514WxTrayIconMessageWindowClass",
                "visible": False,
                "area": 1280 * 781,
            },
            {
                "hwnd": 702,
                "process_name": "Weixin.exe",
                "title": "微信",
                "class_name": "Qt51514QWindowIcon",
                "visible": False,
                "area": 443 * 807,
            },
        ])
        self.assertEqual(702, selected)

    def test_window_selector_prefers_weixin_render_child_over_outer_shell(self):
        """The 428x800 render child is the coordinate/input surface."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 801,
                "process_name": "Weixin.exe",
                "title": "微信",
                "class_name": "Qt51514QWindowIcon",
                "visible": False,
                "area": 443 * 807,
                "width": 443,
                "height": 807,
                "depth": 0,
                "parent_hwnd": 0,
                "root_hwnd": 801,
            },
            {
                "hwnd": 802,
                "process_name": "Weixin.exe",
                "title": "MMUIRenderSubWindowHW",
                "class_name": "MMUIRenderSubWindowHW",
                "visible": False,
                "area": 428 * 800,
                "width": 428,
                "height": 800,
                "depth": 1,
                "parent_hwnd": 801,
                "root_hwnd": 801,
            },
        ], preferred_hwnd=801)
        self.assertEqual(802, selected)

    def test_window_selector_prefers_weixin_render_surface_over_unrelated_wechatappex(self):
        """A Weixin render child must beat a larger unrelated helper process."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 1001,
                "process_name": "Weixin.exe",
                "title": "MMUIRenderSubWindowHW",
                "class_name": "MMUIRenderSubWindowHW",
                "visible": False,
                "area": 440 * 982,
                "width": 440,
                "height": 982,
                "depth": 1,
                "parent_hwnd": 1000,
                "root_hwnd": 1000,
            },
            {
                "hwnd": 2001,
                "process_name": "WeChatAppEx.exe",
                "title": "",
                "class_name": "Chrome_WidgetWin_0",
                "visible": False,
                "area": 1280 * 781,
                "width": 1280,
                "height": 781,
                "depth": 0,
                "parent_hwnd": 0,
                "root_hwnd": 2001,
            },
        ])
        self.assertEqual(1001, selected)

    def test_window_selector_keeps_explicit_farm_title_priority(self):
        """A positively identified farm page still outranks an untitled MMUI shell."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 1101,
                "process_name": "Weixin.exe",
                "title": "MMUIRenderSubWindowHW",
                "class_name": "MMUIRenderSubWindowHW",
                "visible": False,
                "area": 440 * 982,
                "width": 440,
                "height": 982,
                "depth": 1,
                "parent_hwnd": 1100,
                "root_hwnd": 1100,
            },
            {
                "hwnd": 2101,
                "process_name": "WeChatAppEx.exe",
                "title": "QQ经典农场",
                "class_name": "Chrome_WidgetWin_0",
                "visible": False,
                "area": 1280 * 781,
                "width": 1280,
                "height": 781,
                "depth": 0,
                "parent_hwnd": 0,
                "root_hwnd": 2101,
            },
        ])
        self.assertEqual(2101, selected)

    def test_window_selector_does_not_prefer_tiny_render_helper(self):
        """A tiny Chromium/render helper is not the miniapp content surface."""
        ns = load_focus_wrappers(lambda: 0)
        selector = ns["_wechat_focus_select_window_candidate"]
        selected = selector([
            {
                "hwnd": 901,
                "process_name": "Weixin.exe",
                "title": "微信",
                "class_name": "Qt51514QWindowIcon",
                "visible": True,
                "area": 443 * 807,
                "width": 443,
                "height": 807,
                "depth": 0,
                "parent_hwnd": 0,
                "root_hwnd": 901,
            },
            {
                "hwnd": 902,
                "process_name": "WeChatAppEx.exe",
                "title": "Chrome Legacy Window",
                "class_name": "Chrome_RenderWidgetHostHWND",
                "visible": False,
                "area": 100 * 30,
                "width": 100,
                "height": 30,
                "depth": 1,
                "parent_hwnd": 901,
                "root_hwnd": 901,
            },
        ], preferred_hwnd=901)
        self.assertEqual(901, selected)

    def test_child_enumeration_is_limited_to_probable_wechat_roots(self):
        """Do not recursively walk every unrelated desktop window."""
        ns = load_focus_wrappers(lambda: 0)
        gate = ns["_wechat_focus_should_enumerate_children"]
        self.assertTrue(gate({
            "process_name": "C:/Program Files/Weixin/Weixin.exe",
            "title": "",
            "class_name": "Qt51514QWindowIcon",
        }))
        self.assertTrue(gate({
            "process_name": "",
            "title": "微信",
            "class_name": "Qt51514QWindowIcon",
        }))
        self.assertFalse(gate({
            "process_name": "explorer.exe",
            "title": "文件资源管理器",
            "class_name": "CabinetWClass",
        }))
        self.assertFalse(gate({
            "process_name": "chrome.exe",
            "title": "浏览器",
            "class_name": "Chrome_WidgetWin_1",
        }))

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

    def test_none_result_is_applied_when_native_binding_state_proves_target(self):
        """The native v2.3.x path returns None but records its bound target."""
        ns = load_focus_wrappers(lambda: 0x5566)
        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            bound_pid=0,
            bound_process_name="",
            guarded_hwnd=0,
            attempted_hwnd=0,
            existing_window_probe_done=False,
            _wechat_focus_guard_applied_hwnd=0,
            _wechat_focus_guard_attempted_hwnd=0,
            _wechat_focus_guard_existing_window_probe_done=False,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            # Model the target implementation's stateful bind path: it
            # acknowledges through state and returns None.
            target.bound_pid = 9116
            target.bound_process_name = "WeChatAppEx.exe"
            target.guarded_hwnd = target.screen_capture.bound_hwnd
            target.attempted_hwnd = target.screen_capture.bound_hwnd
            target.existing_window_probe_done = True
            return None

        wrapped, _changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )

        self.assertIsNone(wrapped(owner, reason="开始运行/窗口已存在"))
        self.assertTrue(any(
            "微信抢鼠标处理已应用：hwnd=21862" in message
            for _key, message in ns["runtime_messages"]
        ))

    def test_attempted_probe_without_bound_process_is_not_applied(self):
        ns = load_focus_wrappers(lambda: 0x6677)
        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            bound_pid=0,
            bound_process_name="",
            guarded_hwnd=0,
            attempted_hwnd=0x6677,
            existing_window_probe_done=True,
            _wechat_focus_guard_applied_hwnd=0,
            _wechat_focus_guard_attempted_hwnd=0x6677,
            _wechat_focus_guard_existing_window_probe_done=True,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            return None

        wrapped, _changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )

        self.assertIsNone(wrapped(owner, reason="开始运行/窗口已存在"))
        self.assertFalse(any(
            "微信抢鼠标处理已应用" in message
            for _key, message in ns["runtime_messages"]
        ))

    def test_bound_process_and_probe_without_matching_attempt_state_is_not_applied(self):
        ns = load_focus_wrappers(lambda: 0x7788)
        owner = types.SimpleNamespace(
            screen_capture=types.SimpleNamespace(bound_hwnd=0),
            bound_pid=9116,
            bound_process_name="WeChatAppEx.exe",
            guarded_hwnd=0,
            attempted_hwnd=0,
            existing_window_probe_done=True,
            _wechat_focus_guard_applied_hwnd=0,
            _wechat_focus_guard_attempted_hwnd=0,
            _wechat_focus_guard_existing_window_probe_done=True,
        )

        def ensure_wechat_focus_guard_for_current_window(target, reason=""):
            # The process was found, but the native guard did not correlate
            # an attempted/guarded HWND with this invocation.
            return None

        wrapped, _changed = ns["_wrap_wechat_focus_guard"](
            ensure_wechat_focus_guard_for_current_window,
            "bot.ensure_wechat_focus_guard_for_current_window",
        )

        self.assertIsNone(wrapped(owner, reason="开始运行/窗口已存在"))
        self.assertFalse(any(
            "微信抢鼠标处理已应用" in message
            for _key, message in ns["runtime_messages"]
        ))


if __name__ == "__main__":
    unittest.main()
