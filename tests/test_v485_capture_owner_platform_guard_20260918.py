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
    namespace = {"types": types}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V485CaptureOwnerPlatformGuardTests(unittest.TestCase):
    def test_qq_wgc_start_binds_concrete_hwnd_instead_of_weixin_selector(self):
        ns = load_functions("_qqfarm_start_wgc_capture")
        attempts = []

        class HwndCapture:
            def __init__(self, _callback, _closed, window_hwnd=None, **kwargs):
                attempts.append({"window_hwnd": window_hwnd, **kwargs})

            def start_free_threaded(self):
                return object()

        ns.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_CONTROL": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_QQFARM_WGC_GENERATION": 0,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_REBUILD_COOLDOWN_UNTIL": 0.0,
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0x4321,
            "_qqfarm_kernel_pool_guard": lambda: False,
            "_qqfarm_wgc_rebuild_allowed": lambda now=None: True,
            "_qqfarm_deconflict_assistant_window_titles": lambda *args: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: HwndCapture,
            "_qqfarm_wgc_frame_arrived": lambda *args, **kwargs: None,
            "_qqfarm_wgc_closed": lambda *args, **kwargs: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(ns["_qqfarm_start_wgc_capture"]())
        self.assertEqual(1, len(attempts))
        self.assertEqual(0x4321, attempts[0]["window_hwnd"])
        self.assertNotIn("window_name", attempts[0])

    def test_qq_wgc_start_waits_for_a_real_hwnd_and_never_builds_mmui_selector(self):
        ns = load_functions("_qqfarm_start_wgc_capture")
        attempts = []

        class MustNotConstruct:
            def __init__(self, *_args, **kwargs):
                attempts.append(dict(kwargs))
                raise AssertionError("capture must not start without a QQ HWND")

        ns.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_CONTROL": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_QQFARM_WGC_GENERATION": 0,
            "_QQFARM_WGC_BLANK_TS": 0.0,
            "_QQFARM_WGC_REBUILD_COOLDOWN_UNTIL": 0.0,
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_qqfarm_kernel_pool_guard": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: MustNotConstruct,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertFalse(ns["_qqfarm_start_wgc_capture"]())
        self.assertEqual([], attempts)

    def test_unrepairable_cross_platform_owner_is_not_called_again(self):
        ns = load_functions(
            "_qqfarm_prepare_capture_owner_platform",
            "_qqfarm_install_visible_capture_priority",
        )

        class StaleOwner:
            def __init__(self):
                self.calls = 0

            @property
            def window_name(self):
                return "MMUIRenderSubWindowHW"

            def get_window_frame(self):
                self.calls += 1
                return "stale-native"

        owner = StaleOwner()
        context = types.SimpleNamespace(screen_capture=owner)
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
            "_qqfarm_native_capture_fallback_allowed": lambda: True,
            "_qqfarm_note_native_capture_fallback": lambda: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertEqual(1, ns["_qqfarm_install_visible_capture_priority"](context))
        self.assertIsNone(owner.get_window_frame())
        self.assertEqual(0, owner.calls)

    def test_qq_owner_cannot_keep_weixin_render_selector(self):
        ns = load_functions("_qqfarm_prepare_capture_owner_platform")

        class CaptureOwner:
            def __init__(self):
                self.window_name = "MMUIRenderSubWindowHW"
                self.window_hwnd = 0

            def get_window_frame(self):
                return None

        owner = CaptureOwner()
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 4321,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        state = ns["_qqfarm_prepare_capture_owner_platform"](owner)

        self.assertEqual("QQ", state["platform"])
        self.assertEqual(4321, owner.window_hwnd)
        self.assertEqual("QQ经典农场", owner.window_name)
        self.assertFalse(state["cross_platform_selector"])

    def test_qq_without_hwnd_uses_qq_title_not_weixin_title(self):
        ns = load_functions("_qqfarm_prepare_capture_owner_platform")

        owner = types.SimpleNamespace(
            window_name="MMUIRenderSubWindowHW",
            get_window_frame=lambda: None,
        )
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        state = ns["_qqfarm_prepare_capture_owner_platform"](owner)

        self.assertEqual("QQ", state["platform"])
        self.assertEqual("QQ经典农场", owner.window_name)
        self.assertNotIn("MMUI", owner.window_name)
        self.assertFalse(state["cross_platform_selector"])

    def test_qq_does_not_reuse_stale_weixin_hwnd_when_finder_has_no_window(self):
        ns = load_functions("_qqfarm_prepare_capture_owner_platform")

        owner = types.SimpleNamespace(
            window_name="MMUIRenderSubWindowHW",
            window_hwnd=7654,
            get_window_frame=lambda: None,
        )
        ns.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        state = ns["_qqfarm_prepare_capture_owner_platform"](owner)

        self.assertEqual("QQ", state["platform"])
        self.assertEqual(0, owner.window_hwnd)
        self.assertEqual("QQ经典农场", owner.window_name)
        self.assertFalse(state["cross_platform_selector"])

    def test_weixin_owner_keeps_weixin_selector_and_hwnd(self):
        ns = load_functions("_qqfarm_prepare_capture_owner_platform")

        owner = types.SimpleNamespace(
            window_name="QQ经典农场",
            window_hwnd=0,
            get_window_frame=lambda: None,
        )
        ns.update({
            "_active_is_qq_mode": lambda: False,
            "_active_is_weixin_mode": lambda: True,
            "_qqfarm_find_farm_capture_hwnd": lambda: 9876,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        state = ns["_qqfarm_prepare_capture_owner_platform"](owner)

        self.assertEqual("Weixin", state["platform"])
        self.assertEqual(9876, owner.window_hwnd)
        self.assertEqual("微信", owner.window_name)
        self.assertFalse(state["cross_platform_selector"])

    def test_unknown_platform_does_not_rewrite_capture_owner(self):
        ns = load_functions("_qqfarm_prepare_capture_owner_platform")

        owner = types.SimpleNamespace(
            window_name="MMUIRenderSubWindowHW",
            window_hwnd=0,
            get_window_frame=lambda: None,
        )
        ns.update({
            "_active_is_qq_mode": lambda: False,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 2468,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        state = ns["_qqfarm_prepare_capture_owner_platform"](owner)

        self.assertEqual("unknown", state["platform"])
        self.assertEqual("MMUIRenderSubWindowHW", owner.window_name)
        self.assertEqual(0, owner.window_hwnd)
        self.assertFalse(state["cross_platform_selector"])


if __name__ == "__main__":
    unittest.main()
