import sys
import time
import types
import unittest
from pathlib import Path
from unittest import mock

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    lines = HOOK.read_text(encoding="utf-8-sig").splitlines()
    blocks = []
    for name in names:
        marker = f"def {name}("
        start = next(
            (index for index, line in enumerate(lines) if line.startswith(marker)),
            None,
        )
        if start is None:
            continue
        end = len(lines)
        for index in range(start + 1, len(lines)):
            line = lines[index]
            if line and not line[0].isspace() and not line.startswith("#"):
                end = index
                break
        blocks.append("\n".join(lines[start:end]))
    namespace = {"cv2": cv2, "np": np, "time": time}
    exec(compile("\n\n".join(blocks), str(HOOK), "exec"), namespace)
    return namespace


class NativeCycleReadinessRegressionTests(unittest.TestCase):
    def test_native_v225_cycle_waits_for_page_readiness_before_any_business_work(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        native_calls = []
        readiness_calls = []
        context = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        namespace.update({
            "_qqfarm_runtime_page_readiness_gate": (
                lambda owner, label: readiness_calls.append((owner, label)) or False
            ),
            "_restore_runtime_business_switches": lambda _owner: 0,
            "_native_v225_daily_home_ready": lambda _owner: True,
            "_run_native_v225_daily_catchup": (
                lambda _owner: self.fail("daily catch-up ran before the farm page was ready")
            ),
        })

        wrapped, patched = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            lambda _owner: native_calls.append("native") or True,
            "FarmBotCV.run_cycle",
        )

        self.assertTrue(patched)
        self.assertFalse(wrapped(context))
        self.assertEqual([(context, "FarmBotCV.run_cycle")], readiness_calls)
        self.assertEqual([], native_calls)

    def test_native_v225_cycle_dispatches_original_once_after_page_is_ready(self):
        namespace = load_functions("_wrap_native_v225_daily_catchup_run_cycle")
        native_calls = []
        context = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        namespace.update({
            "_qqfarm_runtime_page_readiness_gate": lambda _owner, _label: True,
            "_restore_runtime_business_switches": lambda _owner: 0,
            "_native_v225_daily_home_ready": lambda _owner: True,
        })

        wrapped, patched = namespace["_wrap_native_v225_daily_catchup_run_cycle"](
            lambda _owner: native_calls.append("native") or "done",
            "FarmBotCV.run_cycle",
        )

        self.assertTrue(patched)
        self.assertEqual("done", wrapped(context))
        self.assertEqual(["native"], native_calls)


class PageSceneReadinessRegressionTests(unittest.TestCase):
    def test_title_only_white_shell_is_not_a_ready_farm_page(self):
        namespace = load_functions(
            "_qqfarm_frame_is_usable_for_empty_land_detection",
            "_qqfarm_login_conflict_visible",
            "_qqfarm_runtime_page_action_label",
            "_qqfarm_note_page_readiness",
            "_qqfarm_runtime_page_readiness_gate",
            "_qqfarm_visible_frame_has_farm_scene",
        )
        shell = np.full((800, 428, 3), 255, dtype=np.uint8)
        shell[:52, :, :] = (245, 245, 245)
        cv2.rectangle(shell, (16, 17), (210, 35), (80, 80, 80), 2)
        context = types.SimpleNamespace()
        events = []
        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_share_find_farm_window_hwnd": lambda: 2468,
            "_get_frame_from_bot": lambda _owner: shell,
            "_write": lambda message: events.append(str(message)),
            "_throttled_write": (
                lambda _key, message, _seconds: events.append(str(message))
            ),
        })

        self.assertTrue(
            namespace["_qqfarm_frame_is_usable_for_empty_land_detection"](shell),
            "the shell intentionally has enough contrast to pass the generic pixel gate",
        )
        self.assertFalse(namespace["_qqfarm_visible_frame_has_farm_scene"](shell))
        self.assertFalse(
            namespace["_qqfarm_runtime_page_readiness_gate"](
                context, "FarmBotCV.run_cycle"
            )
        )
        self.assertEqual("loading", context._qqfarm_page_readiness_state)
        self.assertTrue(any("窗口加载中" in event for event in events))


class BlankWindowRecoveryRegressionTests(unittest.TestCase):
    def test_same_blank_hwnd_consumes_only_one_rebuild_budget_entry(self):
        namespace = load_functions(
            "_qqfarm_wgc_prune_blank_hwnds",
            "_qqfarm_wgc_mark_blank_hwnd_once",
            "_qqfarm_stop_wgc_capture",
        )
        rebuild_notes = []
        namespace.update({
            "_QQFARM_WGC_CAPTURE": None,
            "_QQFARM_WGC_CONTROL": None,
            "_QQFARM_WGC_GENERATION": 1,
            "_QQFARM_WGC_RECENT_BLANK_HWNDS": {},
            "_QQFARM_WGC_BLANK_HWND_TTL_SECONDS": 300.0,
            "_qqfarm_wgc_note_rebuild": (
                lambda reason="", now=None: rebuild_notes.append(str(reason))
            ),
            "_throttled_write": lambda *_args, **_kwargs: None,
        })

        for _ in range(2):
            namespace["_QQFARM_WGC_BOUND_HWND"] = 111
            namespace["_QQFARM_LAST_FARM_HWND"] = 111
            namespace["_qqfarm_stop_wgc_capture"]("blank-surface")

        self.assertEqual(["blank-surface"], rebuild_notes)
        self.assertEqual(0, namespace.get("_QQFARM_LAST_FARM_HWND"))

    def test_recent_blank_visible_hwnd_yields_to_new_farm_window_candidate(self):
        namespace = load_functions(
            "_qqfarm_wgc_prune_blank_hwnds",
            "_qqfarm_wgc_blank_hwnd_recent",
            "_qqfarm_find_farm_capture_hwnd",
        )

        class FakeWin32Gui:
            @staticmethod
            def IsWindow(_hwnd):
                return True

            @staticmethod
            def GetWindowText(_hwnd):
                return "QQ经典农场"

            @staticmethod
            def IsWindowVisible(_hwnd):
                return True

            @staticmethod
            def IsIconic(_hwnd):
                return False

            @staticmethod
            def GetWindowRect(hwnd):
                return (0, 0, 428, 800 if int(hwnd) == 222 else 799)

            @staticmethod
            def EnumWindows(callback, extra):
                callback(111, extra)
                callback(222, extra)

        namespace.update({
            "time": types.SimpleNamespace(monotonic=lambda: 110.0),
            "_active_is_weixin_mode": lambda: False,
            "_share_find_farm_window_hwnd": lambda: 111,
            "_share_is_farm_window_title": (
                lambda title: str(title).strip() == "QQ经典农场"
            ),
            "_QQFARM_WGC_BOUND_HWND": 0,
            "_QQFARM_LAST_FARM_HWND": 111,
            "_QQFARM_WGC_RECENT_BLANK_HWNDS": {111: 100.0},
            "_QQFARM_WGC_BLANK_HWND_TTL_SECONDS": 300.0,
        })

        with mock.patch.dict(sys.modules, {"win32gui": FakeWin32Gui()}):
            selected = namespace["_qqfarm_find_farm_capture_hwnd"]()

        self.assertEqual(222, selected)
        self.assertEqual(222, namespace.get("_QQFARM_LAST_FARM_HWND"))


if __name__ == "__main__":
    unittest.main()
