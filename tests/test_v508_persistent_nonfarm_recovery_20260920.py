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
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V508PersistentNonFarmRecoveryTests(unittest.TestCase):
    def test_readiness_gate_counts_same_hwnd_no_frame_and_resets_on_farm_frame(self):
        namespace = load_functions(
            "_qqfarm_runtime_page_action_label",
            "_qqfarm_note_page_readiness",
            "_qqfarm_runtime_page_readiness_gate",
            "_qqfarm_persistent_nonfarm_surface_recovery",
            "_qqfarm_reset_persistent_nonfarm_surface_recovery",
        )
        clock = {"now": 100.0}
        events = []
        recovery_calls = []
        context = types.SimpleNamespace()
        namespace["time"] = types.SimpleNamespace(
            time=lambda: clock["now"],
            monotonic=lambda: clock["now"],
        )
        namespace.update(
            {
                "_active_is_qq_mode": lambda: True,
                "_share_find_farm_window_hwnd": lambda: 777,
                "_get_frame_from_bot": lambda _owner: None,
                "_qqfarm_frame_is_usable_for_empty_land_detection": (
                    lambda _frame: False
                ),
                "_qqfarm_invalidate_wgc_frame_cache": (
                    lambda _reason="": recovery_calls.append("invalidate")
                ),
                "_QQFARM_LAST_FARM_HWND": 777,
                "_qqfarm_stop_wgc_capture": (
                    lambda _reason="": recovery_calls.append("stop")
                ),
                "_qqfarm_restore_hidden_miniapp_taskbar_card": (
                    lambda _reason="": recovery_calls.append("restore") or True
                ),
                "_qqfarm_start_wgc_capture": (
                    lambda: recovery_calls.append("start") or True
                ),
                "_throttled_write": (
                    lambda *args, **kwargs: events.append(str(args[1]))
                ),
                "_write": lambda message: events.append(str(message)),
            }
        )

        for _ in range(3):
            self.assertFalse(
                namespace["_qqfarm_runtime_page_readiness_gate"](
                    context, "FarmBotCV.run_cycle"
                )
            )
        self.assertEqual(["invalidate", "stop", "restore", "start"], recovery_calls)
        self.assertTrue(any("v508 persistent non-farm surface recovery" in item for item in events))

        namespace["_get_frame_from_bot"] = lambda _owner: "farm-frame"
        namespace["_qqfarm_frame_is_usable_for_empty_land_detection"] = (
            lambda frame: frame == "farm-frame"
        )
        namespace["_qqfarm_visible_frame_has_farm_scene"] = (
            lambda frame: frame == "farm-frame"
        )
        self.assertTrue(
            namespace["_qqfarm_runtime_page_readiness_gate"](
                context, "FarmBotCV.run_cycle"
            )
        )
        self.assertEqual(
            0,
            getattr(
                context,
                "_qqfarm_persistent_nonfarm_surface_state",
                {},
            ).get("count"),
        )

    def test_same_hwnd_nonfarm_surface_rebinds_once_then_enters_close_backoff(self):
        namespace = load_functions(
            "_qqfarm_persistent_nonfarm_surface_recovery",
            "_qqfarm_request_farm_window_close",
        )
        clock = {"now": 100.0}
        calls = []
        events = []
        context = types.SimpleNamespace()
        namespace["time"] = types.SimpleNamespace(
            monotonic=lambda: clock["now"],
        )
        namespace.update(
            {
                "_QQFARM_PERSISTENT_NONFARM_THRESHOLD": 3,
                "_QQFARM_PERSISTENT_NONFARM_COOLDOWN_SECONDS": 30.0,
                "_QQFARM_LAST_FARM_HWND": 777,
                "_qqfarm_invalidate_wgc_frame_cache": (
                    lambda reason="": calls.append(("invalidate", reason))
                ),
                "_qqfarm_stop_wgc_capture": (
                    lambda reason="": calls.append(("stop", reason))
                ),
                "_qqfarm_restore_hidden_miniapp_taskbar_card": (
                    lambda reason="": calls.append(("restore", reason)) or True
                ),
                "_qqfarm_start_wgc_capture": (
                    lambda: calls.append(("start",)) or True
                ),
                "_qqfarm_request_farm_window_close": (
                    lambda hwnd: calls.append(("close", hwnd)) or True
                ),
                "_throttled_write": (
                    lambda *args, **kwargs: events.append(str(args[1]))
                ),
            }
        )

        self.assertFalse(
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )
        )
        self.assertFalse(
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )
        )
        self.assertEqual(
            "rebind",
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            ),
        )
        self.assertEqual(
            [
                ("invalidate", "no-frame"),
                ("stop", "persistent-nonfarm"),
                ("restore", "persistent-nonfarm"),
                ("start",),
            ],
            calls,
        )
        self.assertTrue(any("v508 persistent non-farm surface recovery" in item for item in events))

        # A scheduler tick during the recovery cooldown must not repeatedly
        # stop/recreate WGC or close the QQ window.
        clock["now"] = 110.0
        self.assertFalse(
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )
        )
        self.assertNotIn(("close", 777), calls)

        # If the same HWND still produces no farm frame after the first
        # rebind, the next bounded episode closes it and leaves relaunch to
        # the existing protocol guard on a later no-window tick.
        clock["now"] = 140.0
        self.assertEqual(
            "close",
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            ),
        )
        self.assertIn(("close", 777), calls)
        self.assertTrue(
            getattr(
                context,
                "_qqfarm_persistent_nonfarm_surface_state",
                {},
            ).get("relaunch_pending", False)
        )

    def test_lingering_close_request_does_not_leave_a_permanent_relaunch_latch(self):
        namespace = load_functions(
            "_qqfarm_persistent_nonfarm_surface_recovery",
            "_qqfarm_request_farm_window_close",
        )
        clock = {"now": 100.0}
        close_calls = []
        events = []
        context = types.SimpleNamespace()
        namespace["time"] = types.SimpleNamespace(
            monotonic=lambda: clock["now"],
        )
        namespace.update(
            {
                "_QQFARM_PERSISTENT_NONFARM_THRESHOLD": 3,
                "_QQFARM_PERSISTENT_NONFARM_COOLDOWN_SECONDS": 30.0,
                "_QQFARM_PERSISTENT_NONFARM_CLOSE_WAIT_SECONDS": 20.0,
                "_qqfarm_invalidate_wgc_frame_cache": lambda reason="": None,
                "_qqfarm_stop_wgc_capture": lambda reason="": None,
                "_qqfarm_restore_hidden_miniapp_taskbar_card": lambda reason="": True,
                "_qqfarm_start_wgc_capture": lambda: True,
                "_qqfarm_request_farm_window_close": (
                    lambda hwnd: close_calls.append(hwnd) or True
                ),
                "_throttled_write": (
                    lambda *args, **kwargs: events.append(str(args[1]))
                ),
            }
        )

        # Reach the bounded close phase for the first time.
        for now in (100.0, 101.0, 102.0, 140.0):
            clock["now"] = now
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )
        self.assertEqual([777], close_calls)
        self.assertTrue(
            getattr(
                context,
                "_qqfarm_persistent_nonfarm_surface_state",
                {},
            ).get("relaunch_pending", False)
        )

        # The QQ HWND remains enumerable after WM_CLOSE.  Once the bounded wait
        # expires, clear the latch instead of suppressing recovery forever.
        clock["now"] = 161.0
        self.assertFalse(
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            )
        )
        state = getattr(context, "_qqfarm_persistent_nonfarm_surface_state", {})
        self.assertFalse(state.get("relaunch_pending", True))
        self.assertTrue(any("close-timeout" in item for item in events))

        # After the normal cooldown, a still-lingering HWND gets one bounded
        # retry rather than remaining stuck in a no-op start/end loop.
        clock["now"] = 171.0
        self.assertEqual(
            "close",
            namespace["_qqfarm_persistent_nonfarm_surface_recovery"](
                context, 777, "no-frame"
            ),
        )
        self.assertEqual([777, 777], close_calls)

    def test_readiness_log_repeats_after_interval_instead_of_resetting_its_own_clock(self):
        namespace = load_functions("_qqfarm_note_page_readiness")
        clock = {"now": 100.0}
        events = []
        context = types.SimpleNamespace()
        namespace["time"] = types.SimpleNamespace(time=lambda: clock["now"])
        namespace["_throttled_write"] = (
            lambda *args, **kwargs: events.append(str(args[1]))
        )

        namespace["_qqfarm_note_page_readiness"](context, "loading", "waiting")
        clock["now"] = 101.0
        namespace["_qqfarm_note_page_readiness"](context, "loading", "waiting")
        clock["now"] = 116.0
        namespace["_qqfarm_note_page_readiness"](context, "loading", "waiting")

        self.assertEqual(2, len(events))


if __name__ == "__main__":
    unittest.main()
