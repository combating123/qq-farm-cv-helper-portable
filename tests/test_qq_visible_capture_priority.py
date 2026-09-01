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
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class QQVisibleCapturePriorityTests(unittest.TestCase):
    def test_get_frame_prefers_visible_qq_pixels_before_native_printwindow(self):
        namespace = load_functions("_get_frame_from_bot")
        visible = object()
        native = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return native

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: visible,
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(visible, result)
        self.assertEqual([], native_calls)

    def test_get_frame_falls_back_to_native_when_visible_capture_is_missing(self):
        namespace = load_functions("_get_frame_from_bot")
        native = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return native

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(native, result)
        self.assertEqual([True], native_calls)

    def test_runtime_capture_owner_is_patched_once_and_uses_native_as_fallback(self):
        namespace = load_functions("_qqfarm_install_visible_capture_priority")
        install = namespace.get("_qqfarm_install_visible_capture_priority")
        self.assertIsNotNone(install)
        visible_state = {"frame": object()}
        native = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return native

        capture = Capture()
        bot = types.SimpleNamespace(screen_capture=capture)
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: visible_state["frame"],
        })

        self.assertEqual(1, install(bot))
        self.assertEqual(0, install(bot))
        self.assertIs(visible_state["frame"], capture.get_window_frame())
        self.assertEqual([], native_calls)

        visible_state["frame"] = None
        self.assertIs(native, capture.get_window_frame())
        self.assertEqual([True], native_calls)


    def test_get_frame_rejects_occluded_visible_pixels_and_uses_native(self):
        namespace = load_functions("_get_frame_from_bot")
        occluded = object()
        native = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return native

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: occluded,
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: frame is not occluded,
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(native, result)
        self.assertEqual([True], native_calls)


    def test_runtime_capture_owner_uses_cache_while_native_timeout_is_backed_off(self):
        namespace = load_functions("_qqfarm_install_visible_capture_priority")
        install = namespace["_qqfarm_install_visible_capture_priority"]
        cached = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return object()

        capture = Capture()
        bot = types.SimpleNamespace(screen_capture=capture)
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
            "_qqfarm_native_capture_fallback_allowed": lambda: False,
            "_qqfarm_recent_good_capture_frame": lambda: cached,
        })

        self.assertEqual(1, install(bot))
        self.assertIs(cached, capture.get_window_frame())
        self.assertEqual([], native_calls)

    def test_get_frame_accepts_trusted_wgc_overlay_without_sky_signature(self):
        namespace = load_functions("_get_frame_from_bot")
        wgc_overlay = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return object()

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: wgc_overlay,
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: False,
            "_qqfarm_visible_capture_frame_is_trusted": (
                lambda frame: frame is wgc_overlay
            ),
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(wgc_overlay, result)
        self.assertEqual([], native_calls)

    def test_get_frame_uses_recent_safe_frame_when_native_timeout_backoff_is_active(self):
        namespace = load_functions("_get_frame_from_bot")
        cached = object()
        native_calls = []

        class Capture:
            def get_window_frame(self):
                native_calls.append(True)
                return object()

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
            "_qqfarm_native_capture_fallback_allowed": lambda: False,
            "_qqfarm_recent_good_capture_frame": lambda: cached,
        })

        result = namespace["_get_frame_from_bot"](bot)

        self.assertIs(cached, result)
        self.assertEqual([], native_calls)


if __name__ == "__main__":
    unittest.main()
