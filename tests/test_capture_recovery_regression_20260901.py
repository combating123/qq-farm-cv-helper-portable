import ast
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class CaptureRecoveryRegressionTests(unittest.TestCase):
    def test_hidden_restore_uses_capture_hwnd_when_visible_finder_misses(self):
        namespace = load_functions(
            "_qqfarm_restore_hidden_miniapp_taskbar_card"
        )
        calls = []

        class FakeUser32:
            def GetWindowLongPtrW(self, hwnd, index):
                calls.append(("get-style", int(hwnd), int(index)))
                return 0x00000080

            def SetWindowLongPtrW(self, hwnd, index, value):
                calls.append(("set-style", int(hwnd), int(index), int(value)))
                return 0

            def ShowWindowAsync(self, hwnd, command):
                calls.append(("show-async", int(hwnd), int(command)))
                return True

            def ShowWindow(self, hwnd, command):
                calls.append(("show", int(hwnd), int(command)))
                return True

            def SetWindowPos(self, hwnd, insert_after, x, y, cx, cy, flags):
                calls.append(("pos", int(hwnd), int(flags)))
                return True

        fake_ctypes = types.SimpleNamespace(windll=types.SimpleNamespace(
            user32=FakeUser32()
        ))
        namespace.update({
            "_configured_bool": lambda _sections, key, default=False:
                True if key == "hide_miniapp_compat_mode" else default,
            "_active_bot_sections": lambda: ("instance.1.bot", "bot"),
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_share_find_farm_window_hwnd": lambda: 0,
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_QQFARM_HIDDEN_RESTORE_LOCK": threading.Lock(),
            "_QQFARM_HIDDEN_RESTORE_COOLDOWN_UNTIL": 0.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        with mock.patch.dict(sys.modules, {"ctypes": fake_ctypes}):
            self.assertTrue(
                namespace["_qqfarm_restore_hidden_miniapp_taskbar_card"](
                    "blank-surface"
                )
            )

        self.assertIn(("get-style", 591632, -20), calls)
        self.assertTrue(any(item[0] == "set-style" for item in calls))
        self.assertIn(("show-async", 591632, 9), calls)
        self.assertIn(("pos", 591632, 0x0057), calls)
        self.assertGreater(
            namespace.get("_QQFARM_HIDDEN_RESTORE_COOLDOWN_UNTIL", 0.0),
            time.monotonic(),
        )

    def test_hidden_restore_is_single_flight_during_concurrent_recovery(self):
        namespace = load_functions(
            "_qqfarm_restore_hidden_miniapp_taskbar_card"
        )
        calls = []
        entered = threading.Event()
        release = threading.Event()

        class FakeUser32:
            def GetWindowLongPtrW(self, hwnd, index):
                return 0

            def SetWindowLongPtrW(self, hwnd, index, value):
                return 0

            def ShowWindowAsync(self, hwnd, command):
                calls.append(("show-async", int(hwnd), int(command)))
                entered.set()
                release.wait(1.0)
                return True

            def SetWindowPos(self, hwnd, insert_after, x, y, cx, cy, flags):
                calls.append(("pos", int(hwnd), int(flags)))
                return True

        fake_ctypes = types.SimpleNamespace(windll=types.SimpleNamespace(
            user32=FakeUser32()
        ))
        namespace.update({
            "_configured_bool": lambda _sections, key, default=False:
                True if key == "hide_miniapp_compat_mode" else default,
            "_active_bot_sections": lambda: ("instance.1.bot", "bot"),
            "_qqfarm_farm_window_is_visible": lambda: False,
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_QQFARM_HIDDEN_RESTORE_LOCK": threading.Lock(),
            "_QQFARM_HIDDEN_RESTORE_COOLDOWN_UNTIL": 0.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        results = []

        def invoke():
            results.append(
                namespace["_qqfarm_restore_hidden_miniapp_taskbar_card"](
                    "blank-surface"
                )
            )

        with mock.patch.dict(sys.modules, {"ctypes": fake_ctypes}):
            first = threading.Thread(target=invoke)
            first.start()
            self.assertTrue(entered.wait(1.0))
            second = threading.Thread(target=invoke)
            second.start()
            second.join(1.0)
            release.set()
            first.join(1.0)

        self.assertEqual(2, len(results))
        self.assertEqual(1, len([item for item in calls if item[0] == "show-async"]))
        self.assertIn(False, results)
        self.assertIn(True, results)

    def test_finished_wgc_control_invalidates_every_cross_session_state(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        stop_calls = []

        class FinishedControl:
            def is_finished(self):
                return True

        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": FinishedControl(),
            "_QQFARM_WGC_GENERATION": 7,
            "_QQFARM_WGC_FRAME": object(),
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_QQFARM_WGC_RAW_SIZE": (428, 800),
            "_QQFARM_WGC_BLANK_TS": time.monotonic(),
            "_QQFARM_WGC_BLANK_COUNT": 2,
            "_QQFARM_WGC_BOUND_HWND": 591632,
            "_QQFARM_WGC_STATE": "ready",
            "_QQFARM_WGC_SESSION_READY": True,
            "_QQFARM_WGC_FIRST_VALID_FRAME_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_FRAME": object(),
            "_QQFARM_LAST_WGC_NORMALIZED_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS": time.monotonic(),
            "_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID": 123,
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": object(),
            "_QQFARM_LAST_GOOD_CAPTURE_TS": time.monotonic(),
            "_QQFARM_LAST_GOOD_CAPTURE_GENERATION": 7,
            "_QQFARM_LAST_GOOD_CAPTURE_HWND": 591632,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_qqfarm_stop_wgc_capture": lambda reason="": stop_calls.append(reason),
            "_throttled_write": lambda *args, **kwargs: None,
            "_qqfarm_wgc_note_rebuild": lambda *args, **kwargs: None,
        })

        self.assertFalse(namespace["_qqfarm_start_wgc_capture"]())
        self.assertEqual(["finished-controller"], stop_calls)
        self.assertIsNone(namespace.get("_QQFARM_WGC_CAPTURE"))
        self.assertIsNone(namespace.get("_QQFARM_WGC_CONTROL"))
        self.assertIsNone(namespace.get("_QQFARM_WGC_FRAME"))
        self.assertEqual(0.0, namespace.get("_QQFARM_WGC_FRAME_TS"))
        self.assertIsNone(namespace.get("_QQFARM_LAST_WGC_NORMALIZED_FRAME"))
        self.assertEqual(0.0, namespace.get("_QQFARM_LAST_WGC_NORMALIZED_TS"))
        self.assertEqual(
            0.0, namespace.get("_QQFARM_LAST_WGC_NORMALIZED_SOURCE_TS")
        )
        self.assertEqual(0, namespace.get("_QQFARM_LAST_WGC_NORMALIZED_SOURCE_ID"))
        self.assertIsNone(namespace.get("_QQFARM_LAST_GOOD_CAPTURE_FRAME"))
        self.assertEqual(0.0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_TS"))
        self.assertEqual(0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_GENERATION"))
        self.assertEqual(0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_HWND"))
        self.assertEqual(0, namespace.get("_QQFARM_WGC_BOUND_HWND"))
        self.assertFalse(namespace.get("_QQFARM_WGC_SESSION_READY"))
        self.assertGreater(namespace.get("_QQFARM_WGC_GENERATION", 0), 7)

    def test_window_disappearance_stops_old_capture_before_waiting_for_rebuild(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        events = []

        class LiveControl:
            def is_finished(self):
                return False

        def stop_capture(reason=""):
            events.append(reason)
            namespace["_QQFARM_WGC_CAPTURE"] = None
            namespace["_QQFARM_WGC_CONTROL"] = None
            namespace["_QQFARM_WGC_FRAME"] = None
            namespace["_QQFARM_WGC_FRAME_TS"] = 0.0
            return True

        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": LiveControl(),
            "_QQFARM_WGC_BOUND_HWND": 591632,
            "_QQFARM_WGC_FRAME": object(),
            "_QQFARM_WGC_FRAME_TS": time.monotonic(),
            "_QQFARM_WGC_SESSION_READY": True,
            "_QQFARM_WGC_STATE": "ready",
            "_QQFARM_WGC_FIRST_VALID_FRAME_TS": time.monotonic(),
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_qqfarm_find_farm_capture_hwnd": lambda: 0,
            "_qqfarm_stop_wgc_capture": stop_capture,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertFalse(namespace["_qqfarm_start_wgc_capture"]())
        self.assertEqual(["window-disappeared"], events)
        self.assertIsNone(namespace.get("_QQFARM_WGC_CAPTURE"))
        self.assertIsNone(namespace.get("_QQFARM_WGC_CONTROL"))
        self.assertIsNone(namespace.get("_QQFARM_WGC_FRAME"))
        self.assertEqual(0.0, namespace.get("_QQFARM_WGC_FRAME_TS"))
        self.assertEqual("pending-window", namespace.get("_QQFARM_WGC_STATE"))
        self.assertFalse(namespace.get("_QQFARM_WGC_SESSION_READY"))

    def test_wgc_rebinds_to_hidden_or_minimized_farm_handle_when_visible_rect_is_unusable(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        instances = []

        class HwndCapture:
            def __init__(self, callback, close_callback, window_hwnd=None, **kwargs):
                self.window_hwnd = window_hwnd
                self.kwargs = kwargs
                instances.append(self)

            def start_free_threaded(self):
                return object()

        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_CONTROL": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 0,
            # A hidden/minimized farm can have an off-screen 158x26 rect, so
            # the visible-size finder intentionally returns no result.  The
            # capture-specific finder must still supply the real HWND.
            "_qqfarm_find_farm_capture_hwnd": lambda: 591632,
            "_qqfarm_deconflict_assistant_window_titles": lambda: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: HwndCapture,
            "_qqfarm_wgc_frame_arrived": lambda *args, **kwargs: None,
            "_qqfarm_wgc_closed": lambda *args, **kwargs: None,
            "_qqfarm_wgc_rebuild_allowed": lambda **kwargs: True,
            "_qqfarm_kernel_pool_guard": lambda: False,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(namespace["_qqfarm_start_wgc_capture"]())
        self.assertEqual(1, len(instances))
        self.assertEqual(591632, instances[0].window_hwnd)

    def test_wgc_waits_for_a_real_farm_hwnd_and_never_uses_title_fallback(self):
        namespace = load_functions("_qqfarm_start_wgc_capture")
        instances = []

        class FakeCapture:
            def __init__(self, callback, close_callback, **kwargs):
                instances.append(kwargs)

            def start_free_threaded(self):
                return object()

        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_CONTROL": None,
            "_QQFARM_WGC_START_ATTEMPT_TS": 0.0,
            "_share_find_farm_window_hwnd": lambda: 0,
            "_qqfarm_deconflict_assistant_window_titles": lambda: 0,
            "_qqfarm_wgc_window_title_conflicted": lambda: False,
            "_qqfarm_load_native_windows_capture_class": lambda: FakeCapture,
            "_qqfarm_wgc_frame_arrived": lambda *args, **kwargs: None,
            "_qqfarm_wgc_closed": lambda *args, **kwargs: None,
            "_qqfarm_wgc_rebuild_allowed": lambda **kwargs: True,
            "_qqfarm_kernel_pool_guard": lambda: False,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertFalse(namespace["_qqfarm_start_wgc_capture"]())
        self.assertEqual([], instances)
        self.assertEqual("pending-window", namespace.get("_QQFARM_WGC_STATE"))

    def test_wgc_warmup_does_not_release_an_old_frame_to_business_logic(self):
        namespace = load_functions(
            "_get_frame_from_bot",
            "_qqfarm_recent_good_capture_frame",
        )
        stale = object()

        class Capture:
            def get_window_frame(self):
                self.fail("native capture must not run during WGC warmup")

        bot = types.SimpleNamespace(screen_capture=Capture())
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_qqfarm_capture_visible_farm_frame": lambda: None,
            "_qqfarm_native_capture_fallback_allowed": lambda: False,
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": stale,
            "_QQFARM_LAST_GOOD_CAPTURE_TS": time.monotonic(),
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_SESSION_READY": False,
            "_QQFARM_WGC_FIRST_VALID_FRAME_TS": 0.0,
            "_QQFARM_WGC_STATE": "pending",
        })

        self.assertIsNone(namespace["_get_frame_from_bot"](bot))

    def test_recent_frame_is_invalid_after_wgc_generation_or_hwnd_changes(self):
        namespace = load_functions(
            "_qqfarm_remember_good_capture_frame",
            "_qqfarm_recent_good_capture_frame",
        )
        frame = object()
        namespace.update({
            "_QQFARM_WGC_GENERATION": 7,
            "_QQFARM_WGC_BOUND_HWND": 101,
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": None,
            "_QQFARM_LAST_GOOD_CAPTURE_TS": 0.0,
        })

        namespace["_qqfarm_remember_good_capture_frame"](frame)
        self.assertIs(frame, namespace["_QQFARM_LAST_GOOD_CAPTURE_FRAME"])
        self.assertEqual(7, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_GENERATION"))
        self.assertEqual(101, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_HWND"))

        namespace["_QQFARM_WGC_GENERATION"] = 8
        namespace["_QQFARM_WGC_BOUND_HWND"] = 202
        self.assertIsNone(namespace["_qqfarm_recent_good_capture_frame"]())

    def test_stopping_wgc_clears_the_cross_session_good_frame(self):
        namespace = load_functions("_qqfarm_stop_wgc_capture")
        namespace.update({
            "_QQFARM_WGC_CAPTURE": object(),
            "_QQFARM_WGC_CONTROL": types.SimpleNamespace(stop=lambda: None),
            "_QQFARM_WGC_GENERATION": 7,
            "_QQFARM_LAST_GOOD_CAPTURE_FRAME": object(),
            "_QQFARM_LAST_GOOD_CAPTURE_TS": time.monotonic(),
            "_QQFARM_LAST_GOOD_CAPTURE_GENERATION": 7,
            "_QQFARM_LAST_GOOD_CAPTURE_HWND": 101,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        namespace["_qqfarm_stop_wgc_capture"]("session-transition")

        self.assertIsNone(namespace.get("_QQFARM_LAST_GOOD_CAPTURE_FRAME"))
        self.assertEqual(0.0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_TS"))
        self.assertEqual(0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_GENERATION"))
        self.assertEqual(0, namespace.get("_QQFARM_LAST_GOOD_CAPTURE_HWND"))

    def test_log_rescue_only_queues_when_no_real_scheduler_is_available(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        events = []
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            run_cycle=lambda: events.append("cycle") or "done",
        )
        namespace.update({"_write": lambda message: events.append(message)})

        result = namespace["_runtime_patrol_rescue_transition"](
            context,
            "================ 开始新一轮巡检 ================",
        )

        self.assertEqual("queued", result)
        self.assertFalse(any(item == "cycle" for item in events))
        self.assertTrue(getattr(context, "_qqfarm_patrol_rescue_pending", False))
        self.assertFalse(context._qqfarm_patrol_rescue_running)

    def test_stop_requested_does_not_create_patrol_rescue_pending(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        events = []
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            is_stop_requested=lambda: True,
            run_cycle=lambda: events.append("cycle") or "done",
        )
        namespace.update({"_write": lambda message: events.append(message)})

        result = namespace["_runtime_patrol_rescue_transition"](
            context,
            "================ 开始新一轮巡检 ================",
        )

        self.assertEqual("start", result)
        self.assertFalse(getattr(context, "_qqfarm_patrol_rescue_pending", False))
        self.assertNotIn("cycle", events)

    def test_rescue_cooldown_blocks_requeue_until_real_branch(self):
        namespace = load_functions("_runtime_patrol_rescue_transition")
        now = time.monotonic()
        context = types.SimpleNamespace(
            enable_process_self=True,
            enable_process_friend=True,
            _qqfarm_patrol_empty_streak=2,
            _qqfarm_patrol_rescue_running=False,
            _qqfarm_patrol_rescue_pending=False,
            _qqfarm_patrol_rescue_cooldown_until=now + 60.0,
            run_cycle=lambda: "done",
        )
        namespace.update({"_write": lambda *_args, **_kwargs: None})

        result = namespace["_runtime_patrol_rescue_transition"](
            context,
            "================ 开始新一轮巡检 ================",
        )

        self.assertEqual("start", result)
        self.assertFalse(getattr(context, "_qqfarm_patrol_rescue_pending", False))

        context._qqfarm_patrol_rescue_pending = True
        namespace["_runtime_patrol_rescue_transition"](
            context,
            "正在检查好友农场是否有可执行的任务",
        )
        self.assertFalse(context._qqfarm_patrol_rescue_pending)
        self.assertEqual(0.0, context._qqfarm_patrol_rescue_cooldown_until)

    def test_native_cycle_consuming_rescue_starts_a_cooldown(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        events = []
        namespace.update({
            "_restore_runtime_business_switches": lambda _context: 0,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_native_v225_daily_home_ready": lambda _context: False,
            "_native_v225_daily_any_due": lambda _context: False,
            "_qqfarm_native_friend_idle_home_recovery": lambda _context: False,
        })
        context = types.SimpleNamespace(
            _qqfarm_patrol_rescue_pending=True,
            _qqfarm_patrol_rescue_pending_ts=time.monotonic(),
        )
        wrapped, installed = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            lambda _owner: events.append("cycle") or "done",
            "FarmBotCV.run_cycle",
        )

        result = wrapped(context)

        self.assertTrue(installed)
        self.assertEqual("done", result)
        self.assertEqual(["cycle"], events)
        self.assertFalse(context._qqfarm_patrol_rescue_pending)
        self.assertGreater(
            context._qqfarm_patrol_rescue_cooldown_until,
            time.monotonic(),
        )


if __name__ == "__main__":
    unittest.main()
