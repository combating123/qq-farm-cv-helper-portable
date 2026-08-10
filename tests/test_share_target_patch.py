import ast
import base64
import os
import subprocess
import sys
import time
import types
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_share_patch_functions():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {
        "_looks_share_target_module",
        "_wrap_share_target_guard_func",
        "_patch_share_target_guard_for_module",
        "_patch_share_target_guard_loaded",
    }
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    calls = []
    namespace = {
        "_stop_requested_in_args": lambda a, k: False,
        "_stop_gate_return": lambda name: False,
        "_share_target_guard_config": lambda: {
            "enabled": True,
            "target_name": "指定好友",
            "dry_run": False,
            "allow_group": False,
        },
        "_share_log_runtime": lambda *a, **k: None,
        "_share_close_dialog": lambda *a, **k: None,
        "_share_search_and_maybe_confirm": lambda mod, cfg: calls.append((mod, cfg)) or True,
        "_write": lambda *a, **k: None,
        "_SHARE_TARGET_PATCH_LOG_SEEN": set(),
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["calls"] = calls
    return namespace


def load_share_fast_path_functions():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {
        "_share_wait_exact_uia_target",
        "_share_wait_dialog_closed",
        "_share_prompt_button_center_from_rgb",
        "_wrap_share_entry_settle_func",
    }
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)

    class FakeTime:
        def __init__(self):
            self.now = 0.0
        def monotonic(self):
            return self.now
        def sleep(self, seconds):
            self.now += seconds

    fake_time = FakeTime()
    namespace = {
        "time": fake_time,
        "_share_int_cfg": lambda key, default: default,
        "_daily_entry_call_kind": lambda a, k: next((str(x) for x in a if str(x) in ("share_entry", "task_entry", "share_prompt", "share_btn_click")), ""),
        "_share_click_result_succeeded": lambda result: bool(result),
        "_share_find_exact_uia_target": lambda *a, **k: None,
        "_share_find_dialog_hwnd": lambda *a, **k: 1,
        "_share_find_prompt_button_center": lambda *a, **k: None,
        "_share_click_abs": lambda *a, **k: True,
        "_throttled_write": lambda *a, **k: None,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["fake_time"] = fake_time
    return namespace


def load_share_entry_patch_functions():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {
        "_looks_share_entry_module",
        "_patch_share_entry_settle_for_module",
        "_patch_share_entry_settle_loaded",
    }
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "_wrap_share_entry_settle_func": lambda fn: ((lambda *a, **k: "wrapped"), True),
        "_SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN": set(),
        "_write": lambda *a, **k: None,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_named_hook_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace



def configure_strict_share_namespace(
    namespace, *, uia_available=True, matched=True, proof_ok=True,
    dialog_closes=True, ensure_rect=True
):
    state = {
        "events": [],
        "logs": [],
        "recorded": [],
        "target": object(),
        "confirm": object(),
    }

    def click_uia(element):
        label = "target" if element is state["target"] else "confirm"
        state["events"].append(("uia", label))
        return True

    def wait_exact(*args, **kwargs):
        state["events"].append(("wait-exact",))
        return state["target"] if matched else None

    def ensure(hwnd):
        state["events"].append(("ensure", hwnd))
        return (0, 0, 900, 900)

    namespace.update({
        "_share_direct_success_recent": lambda *args, **kwargs: False,
        "_share_record_direct_success": lambda target, evidence=None: state["recorded"].append((target, evidence)) or True,
        "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 77,
        "_share_find_dialog_hwnd": lambda mod=None: 77,
        "_share_activate_dialog": lambda mod, hwnd: True,
        "_share_ensure_dialog_on_screen": ensure if ensure_rect else None,
        "_share_get_rect": lambda hwnd: (0, 0, 900, 900),
        "_share_ratio_cfg": lambda key, default: default,
        "_share_int_cfg": lambda key, default: default,
        "_share_point": lambda rect, xr, yr: (round(float(xr), 3), round(float(yr), 3)),
        "_share_enter_target_exact": lambda *args, **kwargs: True,
        "_share_type_target": lambda target: True,
        "_share_uia_backend_available": lambda: bool(uia_available),
        "_share_wait_exact_uia_target": wait_exact,
        "_share_uia_candidate_is_group": lambda element: False,
        "_share_click_uia_element": click_uia,
        "_share_single_target_selection_proof": lambda *args, **kwargs: {
            "ok": bool(proof_ok),
            "reason": "single-target" if proof_ok else "selected-count-2",
            "selected_count": 1 if proof_ok else 2,
            "confirm": state["confirm"] if proof_ok else None,
        },
        "_share_confirm_label_is_direct_send": lambda element: element is state["confirm"],
        "_share_wait_dialog_closed": lambda mod=None, timeout_ms=0: bool(dialog_closes),
        "_share_close_dialog": lambda mod=None, hwnd=0: state["events"].append(("close", hwnd)) or True,
        "_share_log_runtime": lambda key, msg, warning=False: state["logs"].append((key, msg, warning)),
        "_share_click_abs": lambda x, y: state["events"].append(("coord", (x, y))) or True,
        "_share_click_dialog_point": lambda hwnd, x, y, repeat=False: state["events"].append(("dialog", (x, y, repeat))) or True,
        "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
    })
    return state


class ShareTargetPatchTests(unittest.TestCase):
    def test_obfuscated_module_with_first_friend_handler_is_recognized(self):
        ns = load_share_patch_functions()
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: "first-friend"

        self.assertTrue(ns["_looks_share_target_module"](mod))

    def test_loaded_scan_patches_obfuscated_share_module(self):
        ns = load_share_patch_functions()
        original_calls = []
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: original_calls.append(True) or True
        ns["sys"] = types.SimpleNamespace(modules={mod.__name__: mod})

        changed = ns["_patch_share_target_guard_loaded"]("unit-test")
        result = mod._click_share_dialog_first_friend_and_confirm()

        self.assertEqual([mod.__name__ + ":1"], changed)
        self.assertTrue(result)
        self.assertEqual([], original_calls)

    def test_obfuscated_first_friend_handler_is_replaced_by_exact_target_guard(self):
        ns = load_share_patch_functions()
        original_calls = []
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: original_calls.append(True) or True

        changed = ns["_patch_share_target_guard_for_module"](mod, "unit-test")
        result = mod._click_share_dialog_first_friend_and_confirm()

        self.assertEqual(1, changed)
        self.assertTrue(result)
        self.assertEqual([], original_calls)
        self.assertEqual(1, len(ns["calls"]))
        self.assertIs(mod, ns["calls"][0][0])
        self.assertEqual("指定好友", ns["calls"][0][1]["target_name"])


    def test_exact_target_wait_polls_and_returns_as_soon_as_result_appears(self):
        ns = load_share_fast_path_functions()
        self.assertTrue(callable(ns.get("_share_wait_exact_uia_target")))
        calls = []
        target = object()
        ns["_share_find_exact_uia_target"] = lambda *a, **k: calls.append(1) or (target if len(calls) == 3 else None)
        found = ns["_share_wait_exact_uia_target"](100, "1000000001", False, 1200)
        self.assertIs(target, found)
        self.assertEqual(3, len(calls))
        self.assertLess(ns["fake_time"].now, 0.4)

    def test_dialog_close_wait_requires_window_to_disappear(self):
        ns = load_share_fast_path_functions()
        self.assertTrue(callable(ns.get("_share_wait_dialog_closed")))
        states = iter([100, 100, 0])
        ns["_share_find_dialog_hwnd"] = lambda mod=None: next(states)
        self.assertTrue(ns["_share_wait_dialog_closed"](None, 800))
        self.assertLess(ns["fake_time"].now, 0.4)

    def test_share_entry_settle_recognizes_obfuscated_module(self):
        ns = load_share_entry_patch_functions()
        self.assertTrue(callable(ns.get("_looks_share_entry_module")))
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_template_once = lambda *a, **k: False
        self.assertTrue(ns["_looks_share_entry_module"](mod))

    def test_share_entry_settle_loaded_scan_patches_obfuscated_module(self):
        ns = load_share_entry_patch_functions()
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_template_once = lambda *a, **k: False
        ns["sys"] = types.SimpleNamespace(modules={mod.__name__: mod})
        changed = ns["_patch_share_entry_settle_loaded"]("unit-test")
        self.assertEqual([mod.__name__ + ":1"], changed)
        self.assertEqual("wrapped", mod._click_template_once("share_btn_click"))

    def test_daily_entry_kind_accepts_positional_share_prompt_and_button(self):
        ns = load_named_hook_functions("_daily_entry_call_kind")
        detect = ns["_daily_entry_call_kind"]
        self.assertEqual("share_prompt", detect((object(), "share_prompt"), {}))
        self.assertEqual("share_btn_click", detect((object(), "share_btn_click"), {}))

    def test_share_farm_window_title_accepts_miniapp_and_rejects_helper(self):
        ns = load_named_hook_functions("_share_is_farm_window_title")
        self.assertTrue(callable(ns.get("_share_is_farm_window_title")))
        match = ns["_share_is_farm_window_title"]
        self.assertTrue(match("\u0051\u0051\u7ecf\u5178\u519c\u573a"))
        self.assertFalse(match("\u0051\u0051\u7ecf\u5178\u519c\u573a - \u89c6\u89c9\u81ea\u52a8\u5316"))
        self.assertFalse(match("QQ"))

    def test_share_prompt_frame_can_be_recovered_from_bot_argument(self):
        ns = load_named_hook_functions("_share_prompt_frame_from_call")
        self.assertTrue(callable(ns.get("_share_prompt_frame_from_call")))
        frame = object()
        bot = object()
        ns["_get_frame_from_bot"] = lambda value: frame if value is bot else None
        self.assertIs(frame, ns["_share_prompt_frame_from_call"]((bot, "share_btn_click"), {}))

    def test_green_share_button_detector_finds_lower_center_capsule(self):
        ns = load_share_fast_path_functions()
        self.assertTrue(callable(ns.get("_share_prompt_button_center_from_rgb")))
        image = [[[240, 240, 240] for _ in range(200)] for _ in range(300)]
        for y in range(225, 255):
            for x in range(55, 145):
                image[y][x] = [45, 190, 95]
        center = ns["_share_prompt_button_center_from_rgb"](image)
        self.assertIsNotNone(center)
        self.assertTrue(85 <= center[0] <= 115)
        self.assertTrue(232 <= center[1] <= 248)

    def test_share_prompt_recovers_when_visual_button_is_already_visible(self):
        ns = load_share_fast_path_functions()
        self.assertTrue(callable(ns.get("_wrap_share_entry_settle_func")))
        ns["_share_find_prompt_button_center"] = lambda: (500, 600)
        wrapped, changed = ns["_wrap_share_entry_settle_func"](lambda *a, **k: False)
        self.assertTrue(changed)
        self.assertTrue(wrapped("share_prompt"))

    def test_share_button_fallback_passes_call_context_to_visual_finder(self):
        ns = load_share_fast_path_functions()
        seen = []
        context = object()
        ns["_share_find_prompt_button_center"] = (
            lambda *args: seen.append(args) or (500, 600)
        )
        ns["_share_click_abs"] = lambda x, y: True
        wrapped, _ = ns["_wrap_share_entry_settle_func"](lambda *a, **k: False)
        self.assertTrue(wrapped(context, "share_btn_click"))
        self.assertEqual((((context, "share_btn_click"), {}),), tuple(seen))

    def test_share_button_fallback_prefers_background_window_click(self):
        ns = load_share_fast_path_functions()
        context = object()
        calls = []
        ns["_share_find_prompt_button_center"] = lambda *args: (500, 600)
        ns["_share_click_prompt_button"] = (
            lambda center, call_args=(), call_kwargs=None: calls.append(
                (center, call_args, call_kwargs)
            ) or True
        )
        ns["_share_click_abs"] = lambda x, y: self.fail("absolute click fallback used")
        wrapped, _ = ns["_wrap_share_entry_settle_func"](lambda *a, **k: False)
        self.assertTrue(wrapped(context, "share_btn_click"))
        self.assertEqual([((500, 600), (context, "share_btn_click"), {})], calls)

    def test_share_button_fallback_clicks_only_with_visual_evidence(self):
        ns = load_share_fast_path_functions()
        clicks = []
        ns["_share_find_prompt_button_center"] = lambda: (500, 600)
        ns["_share_click_abs"] = lambda x, y: clicks.append((x, y)) or True
        wrapped, _ = ns["_wrap_share_entry_settle_func"](lambda *a, **k: False)
        self.assertTrue(wrapped("share_btn_click"))
        self.assertEqual([(500, 600)], clicks)


    def test_share_dialog_wait_polls_until_dialog_is_ready(self):
        ns = load_named_hook_functions("_share_wait_dialog_hwnd")
        self.assertTrue(callable(ns.get("_share_wait_dialog_hwnd")))

        class Clock:
            def __init__(self):
                self.now = 0.0
            def monotonic(self):
                return self.now
            def sleep(self, seconds):
                self.now += seconds

        clock = Clock()
        handles = iter((0, 0, 321))
        ns.update({
            "time": clock,
            "_share_find_dialog_hwnd": lambda mod=None: next(handles),
            "_share_int_cfg": lambda key, default: default,
        })
        self.assertEqual(321, ns["_share_wait_dialog_hwnd"](None, timeout_ms=1200))
        self.assertLess(clock.now, 0.5)

    def test_share_numeric_target_is_typed_without_clipboard_dependency(self):
        ns = load_named_hook_functions("_share_type_target")
        self.assertTrue(callable(ns.get("_share_type_target")))
        keys = []
        ctrl = []
        ns.update({
            "_share_send_ctrl_key": lambda vk: ctrl.append(vk) or True,
            "_share_key": lambda vk, up=False: keys.append((vk, up)) or True,
            "_share_set_clipboard_unicode": lambda value: False,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })
        self.assertTrue(ns["_share_type_target"]("1000000001"))
        self.assertEqual([0x41], ctrl)
        typed = [vk for vk, up in keys if not up]
        self.assertEqual([ord(ch) for ch in "1000000001"], typed)

    def test_share_target_prefers_single_clipboard_paste_when_available(self):
        ns = load_named_hook_functions("_share_type_target")
        ctrl = []
        keys = []
        clipboard = []
        ns.update({
            "_share_send_ctrl_key": lambda vk: ctrl.append(vk) or True,
            "_share_key": lambda vk, up=False: keys.append((vk, up)) or True,
            "_share_set_clipboard_unicode": lambda value: clipboard.append(value) or True,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        self.assertTrue(ns["_share_type_target"]("1000000001"))
        self.assertEqual(["1000000001"], clipboard)
        self.assertEqual([0x41, 0x56], ctrl)
        self.assertEqual([], keys)

    def test_share_search_rejects_numeric_coordinate_fallback_without_exact_uia(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, matched=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertFalse(any(event[0] in ("coord", "dialog", "uia") for event in state["events"]))
        self.assertTrue(any(key == "exact-miss" for key, _, _ in state["logs"]))
        self.assertIn(("close", 77), state["events"])


    def test_share_direct_confirm_is_clicked_once_without_visual_fallback(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual(
            [("uia", "target"), ("uia", "confirm")],
            [event for event in state["events"] if event[0] == "uia"],
        )
        self.assertFalse(any(event[0] in ("coord", "dialog") for event in state["events"]))
        self.assertIn(("close", 77), state["events"])

    def test_share_open_dialog_after_direct_confirm_logs_failure_and_closes(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertTrue(any(key == "confirm-not-closed" for key, _, _ in state["logs"]))
        self.assertIn(("close", 77), state["events"])

    def test_share_strict_uia_flow_uses_no_coordinate_selection_or_confirm(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=True)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertTrue(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual(
            [("uia", "target"), ("uia", "confirm")],
            [event for event in state["events"] if event[0] == "uia"],
        )
        self.assertFalse(any(event[0] in ("coord", "dialog") for event in state["events"]))

    def test_share_numeric_result_never_retries_result_card_coordinates(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, matched=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertFalse(any(event[0] in ("coord", "dialog") for event in state["events"]))

    def test_numeric_share_stops_before_uia_wait_when_backend_is_missing(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, uia_available=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertNotIn(("wait-exact",), state["events"])
        self.assertFalse(any(event[0] in ("coord", "dialog", "uia") for event in state["events"]))
        self.assertTrue(any(key == "uia-required" for key, _, _ in state["logs"]))


    def test_daily_entry_kind_accepts_obfuscated_keyword_value(self):
        ns = load_named_hook_functions("_daily_entry_call_kind")
        self.assertEqual(
            "share_btn_click",
            ns["_daily_entry_call_kind"]((), {"template_key": "share_btn_click"}),
        )

    def test_share_button_stops_before_target_confirmation_when_pause_arrives_after_template_click(self):
        ns = load_share_fast_path_functions()
        context = types.SimpleNamespace(stop_requested=False)
        events = []

        def native_template_click(*args, **kwargs):
            events.append("template-click")
            context.stop_requested = True
            return True

        ns.update({
            "_stop_requested_in_args": (
                lambda args, kwargs=None: bool(context.stop_requested)
            ),
            "_stop_gate_return": (
                lambda name: events.append(("stop", name)) or False
            ),
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
            },
            "_share_target_module": lambda: object(),
            "_share_wait_dialog_hwnd": (
                lambda *args, **kwargs: events.append("dialog-wait") or 77
            ),
            "_share_search_and_maybe_confirm": (
                lambda *args, **kwargs: events.append("target-confirm") or True
            ),
            "_share_context_from_call": lambda args, kwargs: context,
            "_share_mark_runtime_success": (
                lambda *args, **kwargs: events.append("persist-success") or True
            ),
            "_SHARE_DIRECT_SUCCESS_STATE": {"evidence": {}},
            "_share_log_runtime": lambda *args, **kwargs: None,
        })

        wrapped, changed = ns["_wrap_share_entry_settle_func"](native_template_click)

        self.assertTrue(changed)
        self.assertFalse(wrapped(context, "share_btn_click"))
        self.assertEqual(
            ["template-click", ("stop", "daily-share-entry-settle")],
            events,
        )

    def test_share_button_stops_after_visual_recovery_click_when_pause_arrives(self):
        ns = load_share_fast_path_functions()
        context = types.SimpleNamespace(stop_requested=False)
        events = []

        def native_template_click(*args, **kwargs):
            events.append("template-click")
            return False

        def visual_recovery_click(*args, **kwargs):
            events.append("visual-recovery-click")
            context.stop_requested = True
            return True

        ns.update({
            "_stop_requested_in_args": (
                lambda args, kwargs=None: bool(context.stop_requested)
            ),
            "_stop_gate_return": (
                lambda name: events.append(("stop", name)) or False
            ),
            "_share_find_prompt_button_center": lambda *args, **kwargs: (500, 600),
            "_share_click_prompt_button": visual_recovery_click,
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
            },
            "_share_target_module": lambda: object(),
            "_share_wait_dialog_hwnd": (
                lambda *args, **kwargs: events.append("dialog-wait") or 77
            ),
            "_share_search_and_maybe_confirm": (
                lambda *args, **kwargs: events.append("target-confirm") or True
            ),
            "_share_context_from_call": lambda args, kwargs: context,
            "_share_mark_runtime_success": (
                lambda *args, **kwargs: events.append("persist-success") or True
            ),
            "_SHARE_DIRECT_SUCCESS_STATE": {"evidence": {}},
            "_share_log_runtime": lambda *args, **kwargs: None,
        })

        wrapped, changed = ns["_wrap_share_entry_settle_func"](native_template_click)

        self.assertTrue(changed)
        self.assertFalse(wrapped(context, "share_btn_click"))
        self.assertEqual(
            [
                "template-click",
                "visual-recovery-click",
                ("stop", "daily-share-entry-settle"),
            ],
            events,
        )

    def test_share_recovery_ignores_same_day_runtime_date_without_v2_proof(self):
        ns = load_named_hook_functions("_share_recovery_due")
        context = types.SimpleNamespace(
            share_last_date=time.strftime("%Y-%m-%d"),
            _qqfarm_share_visual_recovery_last_ts=0.0,
        )
        fake_local = types.SimpleNamespace(tm_hour=5, tm_min=0)
        ns.update({
            "_share_retry_backoff_active": lambda value: False,
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_cfg_get": lambda sections, key, default=None: {
                "enable_daily_share": "True",
                "daily_share_time": "00:31",
            }.get(key, default),
            "_truthy": lambda value, default=False: str(value).lower() in ("1", "true", "yes", "on"),
            "_share_target_guard_config": lambda: {"enabled": True, "target_name": "1000000001"},
            "_share_direct_success_recent": lambda target="": False,
            "time": types.SimpleNamespace(
                strftime=lambda fmt: context.share_last_date,
                localtime=lambda: fake_local,
                monotonic=lambda: 100.0,
            ),
        })

        self.assertTrue(ns["_share_recovery_due"](context))

    def test_share_recovery_schedule_uses_shanghai_clock_not_host_localtime(self):
        ns = load_named_hook_functions("_share_recovery_due")
        context = types.SimpleNamespace(
            share_last_date="",
            _qqfarm_share_visual_recovery_last_ts=0.0,
        )
        # Host-local time says 23:59, while the injected UTC epoch is
        # 2026-08-05 04:59 in Asia/Shanghai. A 05:00 share is not due yet.
        ns.update({
            "_share_retry_backoff_active": lambda value: False,
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_cfg_get": lambda sections, key, default=None: {
                "enable_daily_share": "True",
                "daily_share_time": "05:00",
            }.get(key, default),
            "_truthy": lambda value, default=False: str(value).lower() in ("1", "true", "yes", "on"),
            "_share_target_guard_config": lambda: {"enabled": True, "target_name": "1000000001"},
            "_share_direct_success_recent": lambda target="": False,
            "_daily_business_date": lambda: "2026-08-05",
            "time": types.SimpleNamespace(
                time=lambda: 1785877140,
                gmtime=time.gmtime,
                localtime=lambda: types.SimpleNamespace(tm_hour=23, tm_min=59),
                monotonic=lambda: 100.0,
            ),
        })

        self.assertFalse(ns["_share_recovery_due"](context))


    def test_invalid_active_daily_share_time_fails_closed(self):
        ns = load_named_hook_functions("_parse_hhmm", "_share_recovery_due")
        context = types.SimpleNamespace(
            share_last_date="",
            _qqfarm_share_visual_recovery_last_ts=0.0,
        )
        ns.update({
            "_share_retry_backoff_active": lambda value: False,
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_cfg_get": lambda sections, key, default=None: {
                "enable_daily_share": "True",
                "daily_share_time": "not-a-time",
            }.get(key, default),
            "_truthy": lambda value, default=False: str(value).lower() in ("1", "true", "yes", "on"),
            "_share_target_guard_config": lambda: {"enabled": True, "target_name": "1000000001"},
            "_share_direct_success_recent": lambda target="": False,
            "_daily_business_date": lambda: "2026-08-05",
            "_share_log_runtime": lambda *args, **kwargs: None,
            "time": types.SimpleNamespace(
                time=lambda: 1785938400,
                gmtime=time.gmtime,
                monotonic=lambda: 100.0,
            ),
        })

        self.assertFalse(ns["_share_recovery_due"](context))


    def test_run_share_prompt_recovery_prefers_native_daily_flow_before_visual_click(self):
        ns = load_named_hook_functions("_run_share_prompt_recovery")
        events = []
        context = types.SimpleNamespace()
        state = {"dialog": 0, "verified": False}
        module = types.SimpleNamespace(__name__="bot.synthetic.freebenefits_flow")

        def run_daily_share(bot):
            events.append(("native", bot))
            state["dialog"] = 77
            return False

        def send_exact_target(mod, cfg):
            events.append(("send", cfg["target_name"]))
            state["verified"] = True
            return True

        module.run_daily_share = run_daily_share
        ns.update({
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
                "dry_run": False,
                "allow_group": False,
            },
            "_share_recovery_due": lambda value: True,
            "_share_target_module": lambda: module,
            "_share_find_dialog_hwnd": lambda mod=None: state["dialog"],
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: state["dialog"],
            "_share_find_prompt_button_center": lambda *args, **kwargs: events.append(("visual-probe",)) or (500, 600),
            "_share_click_prompt_button": lambda *args, **kwargs: events.append(("visual-click",)) or True,
            "_share_search_and_maybe_confirm": send_exact_target,
            "_share_direct_success_recent": lambda target="": state["verified"],
            "_daily_flow_apply_success_context": lambda bot, flow: events.append(("apply", bot, flow)) or True,
            "_share_clear_retry_backoff": lambda bot: events.append(("backoff-clear", bot)) or True,
            "_share_log_runtime": lambda *args, **kwargs: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(ns["_run_share_prompt_recovery"](context))
        self.assertEqual(
            [
                ("native", context),
                ("send", "1000000001"),
                ("apply", context, "share"),
                ("backoff-clear", context),
            ],
            events,
        )

    def test_run_share_prompt_recovery_clicks_prompt_sends_target_and_marks_success(self):
        ns = load_named_hook_functions("_run_share_prompt_recovery")
        self.assertTrue(callable(ns.get("_run_share_prompt_recovery")))
        events = []
        state = {"verified": False}
        context = object()
        module = types.SimpleNamespace(__name__="bot._q8eacf4154f.freebenefits_flow")

        def send_exact_target(mod, cfg):
            events.append(("send", cfg["target_name"]))
            state["verified"] = True
            return True

        ns.update({
            "time": type("Clock", (), {"monotonic": staticmethod(lambda: 100.0)}),
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
                "dry_run": False,
                "allow_group": False,
            },
            "_share_recovery_due": lambda value: True,
            "_share_target_module": lambda: module,
            "_share_find_dialog_hwnd": lambda mod=None: 0,
            "_share_find_prompt_button_center": lambda args=(), kwargs=None: (500, 600),
            "_share_click_prompt_button": lambda center, args=(), kwargs=None: events.append(("click", center)) or True,
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 77,
            "_share_search_and_maybe_confirm": send_exact_target,
            "_share_direct_success_recent": lambda target="": state["verified"],
            "_daily_flow_apply_success_context": lambda bot, flow: events.append(("apply", bot, flow)) or True,
            "_share_clear_retry_backoff": lambda bot: events.append(("backoff-clear", bot)) or True,
            "_share_log_runtime": lambda *args, **kwargs: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(ns["_run_share_prompt_recovery"](context))
        self.assertEqual(
            [
                ("click", (500, 600)),
                ("send", "1000000001"),
                ("apply", context, "share"),
                ("backoff-clear", context),
            ],
            events,
        )

    def test_share_button_success_immediately_hands_contact_dialog_to_exact_target_sender(self):
        ns = load_share_fast_path_functions()
        events = []
        context = types.SimpleNamespace(instance_id="1")
        module = types.SimpleNamespace(__name__="bot.synthetic.freebenefits_flow")
        ns.update({
            "_share_target_module": lambda: module,
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
                "dry_run": False,
                "allow_group": False,
            },
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: events.append(("dialog", mod)) or 77,
            "_share_search_and_maybe_confirm": lambda mod, cfg: events.append(("send", cfg["target_name"])) or True,
            "_share_record_direct_success": lambda target: events.append(("record", target)) or True,
            "_share_mark_runtime_success": lambda value: events.append(("mark", value)) or True,
            "_share_log_runtime": lambda *args, **kwargs: None,
        })
        wrapped, changed = ns["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: True
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(context, "share_btn_click"))
        self.assertEqual(
            [
                ("dialog", module),
                ("send", "1000000001"),
            ],
            events,
        )

    def test_share_button_visual_fallback_also_hands_off_to_exact_target_sender(self):
        ns = load_share_fast_path_functions()
        events = []
        context = types.SimpleNamespace(instance_id="1")
        module = types.SimpleNamespace(__name__="bot.synthetic.freebenefits_flow")
        ns.update({
            "_share_find_prompt_button_center": lambda *args, **kwargs: (500, 600),
            "_share_click_prompt_button": lambda *args, **kwargs: events.append(("prompt-click",)) or True,
            "_share_target_module": lambda: module,
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
                "dry_run": False,
                "allow_group": False,
            },
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 77,
            "_share_search_and_maybe_confirm": lambda mod, cfg: events.append(("send", cfg["target_name"])) or True,
            "_share_record_direct_success": lambda target: True,
            "_share_mark_runtime_success": lambda value: True,
            "_share_log_runtime": lambda *args, **kwargs: None,
        })
        wrapped, _ = ns["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: False
        )

        self.assertTrue(wrapped(context, "share_btn_click"))
        self.assertEqual([("prompt-click",), ("send", "1000000001")], events)

    def test_first_friend_handler_acknowledges_recent_direct_target_send(self):
        ns = load_share_patch_functions()
        original_calls = []
        ns["_share_direct_success_recent"] = lambda target="", max_age=15.0: bool(target)
        wrapped, changed = ns["_wrap_share_target_guard_func"](
            lambda: original_calls.append(True) or False,
            types.SimpleNamespace(__name__="bot.synthetic.freebenefits_flow"),
            "_click_share_dialog_first_friend_and_confirm",
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped())
        self.assertEqual([], original_calls)
        self.assertEqual([], ns["calls"])

    def test_share_entry_settle_wraps_compiled_callable_alias(self):
        ns = load_share_entry_patch_functions()

        class CompiledCallable:
            def __call__(self, *args, **kwargs):
                return False

        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._qcompiled = CompiledCallable()
        ns["sys"] = types.SimpleNamespace(modules={mod.__name__: mod})

        changed = ns["_patch_share_entry_settle_loaded"]("unit-test")

        self.assertEqual([mod.__name__ + ":1"], changed)
        self.assertEqual("wrapped", mod._qcompiled(None, "share_btn_click"))

    def test_share_entry_settle_wraps_obfuscated_click_helper_name(self):
        ns = load_share_entry_patch_functions()
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._q17c9 = lambda *args, **kwargs: False
        ns["sys"] = types.SimpleNamespace(modules={mod.__name__: mod})

        changed = ns["_patch_share_entry_settle_loaded"]("unit-test")

        self.assertEqual([mod.__name__ + ":1"], changed)
        self.assertEqual("wrapped", mod._q17c9(None, "share_btn_click"))


    def test_task_entry_waits_long_enough_for_slow_prompt_render(self):
        """A successful task-entry click reserves the 2.4 s live render budget."""
        namespace = load_named_hook_functions("_wrap_share_entry_settle_func")
        sleeps = []
        namespace.update({
            "time": types.SimpleNamespace(sleep=lambda seconds: sleeps.append(seconds)),
            "_daily_entry_call_kind": lambda args, kwargs: "task_entry",
            "_stop_requested_in_args": lambda args, kwargs: False,
            "_stop_gate_return": lambda name: False,
            "_share_click_result_succeeded": lambda value: bool(value),
            "_share_int_cfg": lambda key, default: default,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        wrapped, patched = namespace["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: True
        )

        self.assertTrue(patched)
        self.assertTrue(wrapped(object(), "task_entry"))
        self.assertEqual([2.4], sleeps)

    def test_green_share_button_detector_finds_real_lime_physical_button(self):
        ns = load_share_fast_path_functions()
        image = [[[245, 231, 191] for _ in range(642)] for _ in range(1200)]
        for y in range(955, 1026):
            for x in range(342, 559):
                image[y][x] = [160, 190, 0]

        center = ns["_share_prompt_button_center_from_rgb"](image)

        self.assertIsNotNone(center)
        self.assertTrue(435 <= center[0] <= 465)
        self.assertTrue(980 <= center[1] <= 1000)

    def test_visual_share_click_is_not_success_until_contact_dialog_appears(self):
        ns = load_share_fast_path_functions()
        context = types.SimpleNamespace(instance_id="1")
        module = types.SimpleNamespace(__name__="bot.synthetic.freebenefits_flow")
        ns.update({
            "_share_find_prompt_button_center": lambda *args, **kwargs: (450, 990),
            "_share_click_prompt_button": lambda *args, **kwargs: True,
            "_share_target_module": lambda: module,
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
                "dry_run": False,
                "allow_group": False,
            },
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 0,
            "_share_search_and_maybe_confirm": lambda *args, **kwargs: self.fail(
                "target input started without a contact dialog"
            ),
            "_share_log_runtime": lambda *args, **kwargs: None,
        })
        wrapped, _ = ns["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: False
        )

        self.assertFalse(wrapped(context, "share_btn_click"))

    def test_share_failure_backoff_blocks_immediate_retry_but_reopens_later(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(HOOK))
        wanted = {
            "_share_flow_key",
            "_share_bot_from_args",
            "_share_retry_backoff_seconds",
            "_share_retry_backoff_active",
            "_share_set_retry_backoff",
            "_share_clear_retry_backoff",
            "_patch_share_retry_backoff_for_module",
        }
        nodes = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        module_ast = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(module_ast)

        class Clock:
            now = 100.0

            @classmethod
            def monotonic(cls):
                return cls.now

        namespace = {
            "time": Clock,
            "_cfg_get": lambda sections, key, default: "300",
            "_active_bot_sections": lambda: {},
            "_SHARE_RETRY_PATCH_LOG_SEEN": set(),
            "_throttled_write": lambda *args, **kwargs: None,
            "_write": lambda *args, **kwargs: None,
        }
        exec(compile(module_ast, str(HOOK), "exec"), namespace)
        self.assertEqual(wanted, set(namespace).intersection(wanted))

        events = []
        module = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")

        def mark_failure(bot, flow_key):
            events.append(("failure", flow_key))
            bot.daily_flow_retry_counts[flow_key] += 1
            return False

        module._mark_daily_flow_failure = mark_failure
        module.should_run_daily_share = lambda bot: events.append(("should",)) or True
        module.run_daily_share = lambda bot: events.append(("run",)) or True
        module._mark_daily_flow_success = (
            lambda bot, flow_key: events.append(("success", flow_key)) or True
        )
        bot = types.SimpleNamespace(
            daily_flow_retry_counts={"share": 0},
            share_last_date="",
        )

        changed = namespace["_patch_share_retry_backoff_for_module"](
            module, "unit-test"
        )
        self.assertGreaterEqual(changed, 3)
        self.assertFalse(module._mark_daily_flow_failure(bot, "share"))
        self.assertEqual(1, bot.daily_flow_retry_counts["share"])
        self.assertFalse(module.should_run_daily_share(bot))
        self.assertFalse(module.run_daily_share(bot))
        self.assertNotIn(("should",), events)
        self.assertNotIn(("run",), events)

        Clock.now = 401.0
        self.assertTrue(module.should_run_daily_share(bot))
        self.assertTrue(module.run_daily_share(bot))
        self.assertTrue(module._mark_daily_flow_success(bot, "share"))
        self.assertFalse(namespace["_share_retry_backoff_active"](bot))


    def test_verified_direct_share_success_suppresses_late_native_failure(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(HOOK))
        wanted = {
            "_share_flow_key",
            "_share_bot_from_args",
            "_share_retry_backoff_seconds",
            "_share_retry_backoff_active",
            "_share_set_retry_backoff",
            "_share_clear_retry_backoff",
            "_patch_share_retry_backoff_for_module",
        }
        nodes = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        module_ast = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(module_ast)

        class Clock:
            now = 100.0

            @classmethod
            def monotonic(cls):
                return cls.now

        events = []
        namespace = {
            "time": Clock,
            "_cfg_get": lambda sections, key, default: "300",
            "_active_bot_sections": lambda: {},
            "_SHARE_RETRY_PATCH_LOG_SEEN": set(),
            "_throttled_write": lambda *args, **kwargs: None,
            "_write": lambda *args, **kwargs: None,
            "_share_target_guard_config": lambda: {
                "target_name": "1000000001",
            },
            "_share_direct_success_recent": (
                lambda target="", max_age=15.0:
                target == "1000000001" and max_age >= 86400.0
            ),
            "_daily_flow_apply_success_context": (
                lambda bot, flow: events.append(("apply-success-context", bot, flow)) or True
            ),
        }
        exec(compile(module_ast, str(HOOK), "exec"), namespace)

        module = types.ModuleType("bot.synthetic.freebenefits_flow")

        def mark_failure(bot, flow_key):
            events.append(("native-failure", flow_key))
            bot.daily_flow_retry_counts[flow_key] += 1
            return False

        module._mark_daily_flow_failure = mark_failure
        module.should_run_daily_share = lambda bot: True
        module.run_daily_share = lambda bot: True
        bot = types.SimpleNamespace(
            daily_flow_retry_counts={"share": 0},
            share_last_date="",
        )

        self.assertGreater(
            namespace["_patch_share_retry_backoff_for_module"](module), 0
        )
        self.assertFalse(module._mark_daily_flow_failure(bot, "share"))
        self.assertEqual(0, bot.daily_flow_retry_counts["share"])
        self.assertFalse(namespace["_share_retry_backoff_active"](bot))
        self.assertNotIn(("native-failure", "share"), events)
        self.assertIn(("apply-success-context", bot, "share"), events)
        self.assertFalse(any(event[0] == "mark-runtime-success" for event in events))

    def test_share_exact_entry_retries_until_clipboard_readback_matches_target(self):
        ns = load_named_hook_functions("_share_enter_target_exact")
        helper = ns.get("_share_enter_target_exact")
        self.assertTrue(callable(helper), "exact target entry helper is missing")

        typed = []
        clicks = []
        logs = []
        readbacks = iter(("25736062", "1000000001"))
        ns.update({
            "_share_activate_dialog": lambda mod, hwnd: True,
            "_share_click_dialog_point": (
                lambda hwnd, x, y, repeat=False: clicks.append((hwnd, x, y, repeat)) or True
            ),
            "_share_type_target": lambda target: typed.append(target) or True,
            "_share_read_focused_text_via_clipboard": lambda: next(readbacks),
            "_share_find_dialog_hwnd": lambda mod=None: 77,
            "_share_int_cfg": lambda key, default: 3 if key == "share_target_input_retry_count" else default,
            "_share_norm_text": lambda value: "".join(str(value or "").split()).casefold(),
            "_share_log_runtime": lambda key, msg, warning=False: logs.append((key, msg, warning)),
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        self.assertTrue(helper(None, 77, 442, 308, "1000000001"))
        self.assertEqual(["1000000001", "1000000001"], typed)
        self.assertEqual(2, len(clicks))
        self.assertTrue(any(key == "target-readback-mismatch" for key, _, _ in logs))
        self.assertTrue(any(key == "target-readback-verified" for key, _, _ in logs))


    def test_share_exact_entry_allows_unreadable_readback_to_reach_exact_uia_gate(self):
        ns = load_named_hook_functions("_share_enter_target_exact")
        helper = ns.get("_share_enter_target_exact")
        typed = []
        logs = []
        ns.update({
            "_share_activate_dialog": lambda mod, hwnd: True,
            "_share_click_dialog_point": lambda *args, **kwargs: True,
            "_share_type_target": lambda target: typed.append(target) or True,
            "_share_read_focused_text_via_clipboard": lambda: None,
            "_share_find_exact_uia_target": lambda *args, **kwargs: None,
            "_share_find_dialog_hwnd": lambda mod=None: 77,
            "_share_int_cfg": lambda key, default: 2 if key == "share_target_input_retry_count" else default,
            "_share_norm_text": lambda value: "".join(str(value or "").split()).casefold(),
            "_share_log_runtime": lambda key, msg, warning=False: logs.append((key, msg, warning)),
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        self.assertTrue(helper(None, 77, 100, 50, "1000000001"))
        self.assertEqual(["1000000001", "1000000001"], typed)
        self.assertTrue(any(
            key == "target-readback-provisional" and not warning
            for key, _msg, warning in logs
        ))

    def test_share_clipboard_reader_prefers_native_value_over_stale_qt_cache(self):
        ns = load_named_hook_functions("_share_get_clipboard_unicode")
        helper = ns.get("_share_get_clipboard_unicode")
        self.assertTrue(callable(helper))

        qt_module = types.ModuleType("PySide6.QtGui")
        qt_module.QGuiApplication = types.SimpleNamespace(
            instance=lambda: types.SimpleNamespace(
                clipboard=lambda: types.SimpleNamespace(
                    text=lambda: "__QQFARM_SHARE_READBACK_SENTINEL__"
                )
            )
        )
        py_side = types.ModuleType("PySide6")
        win32 = types.ModuleType("win32clipboard")
        win32.CF_UNICODETEXT = 13
        win32.OpenClipboard = lambda: None
        win32.GetClipboardData = lambda fmt: "1000000001"
        win32.CloseClipboard = lambda: None

        with mock.patch.dict(
            sys.modules,
            {
                "PySide6": py_side,
                "PySide6.QtGui": qt_module,
                "win32clipboard": win32,
            },
        ):
            self.assertEqual("1000000001", helper())

    def test_share_clipboard_writer_prefers_native_clipboard_before_qt(self):
        ns = load_named_hook_functions("_share_set_clipboard_unicode")
        helper = ns.get("_share_set_clipboard_unicode")
        self.assertTrue(callable(helper))
        events = []

        qt_clipboard = types.SimpleNamespace(
            setText=lambda value: events.append(("qt", value)),
            text=lambda: "1000000001",
        )
        qt_module = types.ModuleType("PySide6.QtGui")
        qt_module.QGuiApplication = types.SimpleNamespace(
            instance=lambda: types.SimpleNamespace(clipboard=lambda: qt_clipboard)
        )
        py_side = types.ModuleType("PySide6")
        win32 = types.ModuleType("win32clipboard")
        win32.CF_UNICODETEXT = 13
        win32.OpenClipboard = lambda: events.append(("open",))
        win32.EmptyClipboard = lambda: events.append(("empty",))
        win32.SetClipboardText = lambda value, fmt: events.append(("set", value, fmt))
        win32.CloseClipboard = lambda: events.append(("close",))

        with mock.patch.dict(
            sys.modules,
            {
                "PySide6": py_side,
                "PySide6.QtGui": qt_module,
                "win32clipboard": win32,
            },
        ):
            self.assertTrue(helper("1000000001"))

        self.assertEqual(
            [
                ("open",),
                ("empty",),
                ("set", "1000000001", 13),
                ("close",),
            ],
            events,
        )


    @unittest.skipUnless(os.name == "nt", "Windows clipboard integration")
    def test_share_native_clipboard_roundtrip_uses_pointer_sized_handles(self):
        ns = load_named_hook_functions(
            "_share_set_clipboard_unicode",
            "_share_get_clipboard_unicode",
        )
        ns.update({"time": time, "_write": lambda message: None})
        value = "1000000001"
        original = subprocess.check_output(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Get-Clipboard -Raw",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            self.assertTrue(ns["_share_set_clipboard_unicode"](value))
            self.assertEqual(value, ns["_share_get_clipboard_unicode"]())
        finally:
            payload = base64.b64encode(original.encode("utf-16le")).decode("ascii")
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "$v=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('"
                    + payload
                    + "')); Set-Clipboard -Value $v",
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


    def test_share_dialog_is_moved_inside_work_area_and_returns_refreshed_rect(self):
        ns = load_named_hook_functions("_share_ensure_dialog_on_screen")
        helper = ns.get("_share_ensure_dialog_on_screen")
        self.assertTrue(callable(helper))
        rects = iter([
            (830, 350, 1730, 1250),
            (795, 101, 1695, 1001),
        ])
        moves = []
        ns.update({
            "_share_get_rect": lambda hwnd: next(rects),
            "_share_get_work_area": lambda hwnd: (0, 0, 1707, 1013),
            "_share_move_dialog_window": (
                lambda hwnd, left, top: moves.append((hwnd, left, top)) or True
            ),
            "_share_log_runtime": lambda *args, **kwargs: None,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        result = helper(77)

        self.assertEqual((795, 101, 1695, 1001), result)
        self.assertEqual([(77, 795, 101)], moves)

    def test_share_flow_ensures_visible_rect_before_strict_uia_send(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=True, ensure_rect=True)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertTrue(ns["_share_search_and_maybe_confirm"](None, cfg))
        ensure_index = state["events"].index(("ensure", 77))
        target_index = state["events"].index(("uia", "target"))
        self.assertLess(ensure_index, target_index)

    def test_numeric_share_uses_exact_uia_element_not_radio_candidate_chain(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=True)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertTrue(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual(1, sum(event == ("uia", "target") for event in state["events"]))
        self.assertFalse(any(event[0] in ("coord", "dialog") for event in state["events"]))


    def test_numeric_share_never_toggles_custom_radio_by_coordinates(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, uia_available=False)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertFalse(any(event[0] in ("coord", "dialog", "uia") for event in state["events"]))


    def test_recent_exact_share_suppresses_duplicate_contact_dialog_send(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        waits = []
        closes = []
        logs = []
        ns.update({
            "_share_direct_success_recent": lambda target, max_age=15.0: target == "1000000001",
            "_share_find_dialog_hwnd": lambda mod=None: 77,
            "_share_close_dialog": lambda mod=None, hwnd=0: closes.append((mod, hwnd)) or True,
            "_share_wait_dialog_hwnd": lambda *args, **kwargs: waits.append(True) or 0,
            "_share_log_runtime": lambda key, msg, warning=False: logs.append((key, msg, warning)),
        })

        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}
        self.assertTrue(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual([], waits)
        self.assertEqual([(None, 77)], closes)
        self.assertTrue(any(key == "duplicate-send-suppressed" for key, _, _ in logs))

    def test_verified_dialog_close_records_success_before_returning_to_wrappers(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(ns, dialog_closes=True)
        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}

        self.assertTrue(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual("1000000001", state["recorded"][0][0])
        evidence = state["recorded"][0][1]
        self.assertTrue(evidence["target_match"])
        self.assertEqual(1, evidence["selected_count"])
        self.assertTrue(evidence["confirm_clicked"])
        self.assertTrue(evidence["dialog_closed"])
        self.assertEqual(
            [("uia", "target"), ("uia", "confirm")],
            [event for event in state["events"] if event[0] == "uia"],
        )


    def test_group_candidate_with_member_count_is_rejected(self):
        ns = load_named_hook_functions("_share_uia_candidate_is_group")

        class Candidate:
            element_info = types.SimpleNamespace(
                control_type="ListItem", class_name="", automation_id=""
            )

            def parent(self):
                return None

        candidate = Candidate()
        ns["_share_uia_element_texts"] = lambda element: [
            "name" + chr(0xFF08) + "2" + chr(0x4EBA) + chr(0xFF09),
            "1000000001",
        ]

        self.assertTrue(ns["_share_uia_candidate_is_group"](candidate))

    def test_share_rejects_two_selected_contacts_before_confirm(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        target_element = object()
        confirm_element = object()
        clicks = []
        closes = []

        def click_uia(element):
            clicks.append("target" if element is target_element else "confirm")
            return True

        ns.update({
            "_share_direct_success_recent": lambda *args, **kwargs: False,
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 77,
            "_share_activate_dialog": lambda mod, hwnd: True,
            "_share_get_rect": lambda hwnd: (0, 0, 900, 900),
            "_share_ratio_cfg": lambda key, default: default,
            "_share_int_cfg": lambda key, default: default,
            "_share_point": lambda rect, xr, yr: (round(xr, 3), round(yr, 3)),
            "_share_enter_target_exact": lambda *args, **kwargs: True,
            "_share_uia_backend_available": lambda: True,
            "_share_wait_exact_uia_target": lambda *args, **kwargs: target_element,
            "_share_uia_candidate_is_group": lambda element: False,
            "_share_confirm_label_is_direct_send": lambda element: element is confirm_element,
            "_share_click_uia_element": click_uia,
            "_share_single_target_selection_proof": lambda *args, **kwargs: {
                "ok": False,
                "reason": "selected-count-2",
                "selected_count": 2,
                "confirm": None,
            },
            "_share_find_uia_button": lambda *args, **kwargs: confirm_element,
            "_share_wait_dialog_closed": lambda mod=None, timeout_ms=0: True,
            "_share_close_dialog": lambda mod=None, hwnd=0: closes.append(hwnd) or True,
            "_share_log_runtime": lambda *args, **kwargs: None,
            "_share_click_abs": lambda *args, **kwargs: True,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}
        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual(["target"], clicks)
        self.assertEqual([77], closes)

    def test_share_uses_one_exact_selection_and_one_direct_confirm_only(self):
        ns = load_named_hook_functions("_share_search_and_maybe_confirm")
        target_element = object()
        confirm_element = object()
        events = []

        def click_uia(element):
            events.append(("uia", "target" if element is target_element else "confirm"))
            return True

        ns.update({
            "_share_direct_success_recent": lambda *args, **kwargs: False,
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=None: 77,
            "_share_activate_dialog": lambda mod, hwnd: True,
            "_share_get_rect": lambda hwnd: (0, 0, 900, 900),
            "_share_ratio_cfg": lambda key, default: default,
            "_share_int_cfg": lambda key, default: default,
            "_share_point": lambda rect, xr, yr: (round(xr, 3), round(yr, 3)),
            "_share_enter_target_exact": lambda *args, **kwargs: True,
            "_share_uia_backend_available": lambda: True,
            "_share_wait_exact_uia_target": lambda *args, **kwargs: target_element,
            "_share_uia_candidate_is_group": lambda element: False,
            "_share_confirm_label_is_direct_send": lambda element: element is confirm_element,
            "_share_click_uia_element": click_uia,
            "_share_single_target_selection_proof": lambda *args, **kwargs: {
                "ok": True,
                "reason": "single-target",
                "selected_count": 1,
                "confirm": confirm_element,
            },
            "_share_find_uia_button": lambda *args, **kwargs: confirm_element,
            "_share_wait_dialog_closed": lambda mod=None, timeout_ms=0: False,
            "_share_close_dialog": lambda *args, **kwargs: True,
            "_share_log_runtime": lambda *args, **kwargs: None,
            "_share_click_abs": lambda x, y: events.append(("coord", (x, y))) or True,
            "_share_click_dialog_point": lambda hwnd, x, y, repeat=False: events.append(("dialog", (x, y, repeat))) or True,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        cfg = {"target_name": "1000000001", "allow_group": False, "dry_run": False}
        self.assertFalse(ns["_share_search_and_maybe_confirm"](None, cfg))
        self.assertEqual([("uia", "target"), ("uia", "confirm")], events)

    def test_same_day_share_success_survives_fresh_hook_namespace(self):
        import tempfile

        names = (
            "_daily_flow_status_paths",
            "_daily_flow_read_status",
            "_daily_flow_write_status",
            "_daily_flow_mark_status",
            "_daily_flow_success_today",
            "_share_record_direct_success",
            "_share_direct_success_recent",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_hook = str(Path(temp_dir) / "hook.py")
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": temp_dir}, clear=False):
                first = load_named_hook_functions(*names)
                first.update({"os": os, "time": time, "__file__": fake_hook})
                self.assertTrue(first["_share_record_direct_success"]("1000000001", evidence={'target_match': True, 'selected_count': 1, 'confirm_clicked': True, 'dialog_closed': True}))

                second = load_named_hook_functions(*names)
                second.update({"os": os, "time": time, "__file__": fake_hook})
                self.assertTrue(second["_share_direct_success_recent"]("1000000001"))


    def test_runtime_share_success_requires_direct_send_evidence(self):
        ns = load_named_hook_functions('_share_record_direct_success')
        calls = []
        ns.update({
            'time': time,
            '_daily_flow_mark_status': (
                lambda *args, **kwargs: calls.append((args, kwargs)) or True
            ),
            '_runtime_info_once': lambda *args, **kwargs: None,
        })

        self.assertFalse(ns['_share_record_direct_success']('1000000001'))
        self.assertEqual([], calls)

    def test_runtime_share_success_accepts_complete_direct_send_evidence(self):
        ns = load_named_hook_functions('_share_record_direct_success')
        calls = []
        ns.update({
            'time': time,
            '_daily_flow_mark_status': (
                lambda flow, status, target='', reason='':
                calls.append((flow, status, target, reason)) or True
            ),
            '_runtime_info_once': lambda *args, **kwargs: None,
        })
        evidence = {
            'target_match': True,
            'selected_count': 1,
            'confirm_clicked': True,
            'dialog_closed': True,
        }

        self.assertTrue(ns['_share_record_direct_success'](
            '1000000001', evidence=evidence
        ))
        self.assertIn(
            ('share', 'success', '1000000001',
             'verified-direct-contact-send-v2'),
            calls,
        )

    def test_runtime_share_success_also_persists_durable_flow_status(self):
        ns = load_named_hook_functions('_share_mark_runtime_success')
        calls = []
        context = types.SimpleNamespace(
            instance_id='1',
            share_last_date='',
            daily_flow_retry_counts={'share': 2},
        )
        ns.update({
            'os': os,
            'time': time,
            '__file__': str(ROOT / 'portable' / 'hook.py'),
            '_share_clear_retry_backoff': lambda value: None,
            '_daily_flow_target': lambda flow: '1000000001',
            '_daily_flow_mark_status': (
                lambda flow, status, target='', reason='':
                calls.append((flow, status, target, reason)) or True
            ),
            '_throttled_write': lambda *args, **kwargs: None,
        })

        self.assertTrue(ns['_share_mark_runtime_success'](context, evidence={'target_match': True, 'selected_count': 1, 'confirm_clicked': True, 'dialog_closed': True}))
        self.assertIn(
            ('share', 'success', '1000000001', 'verified-direct-contact-send-v2'),
            calls,
        )

    def test_runtime_share_success_routes_counters_through_canonical_metrics_sync(self):
        ns = load_named_hook_functions('_share_mark_runtime_success')
        today = '2026-08-05'
        sync = mock.Mock(return_value={'date': today})
        context = types.SimpleNamespace(
            instance_id='1',
            share_last_date='',
            daily_flow_retry_counts={'share': 2},
        )
        ns.update({
            'os': os,
            'time': time,
            '__file__': str(ROOT / 'portable' / 'hook.py'),
            '_daily_business_date': lambda: today,
            '_daily_metrics_sync_runtime': sync,
            '_share_clear_retry_backoff': lambda value: None,
            '_daily_flow_target': lambda flow: '1000000001',
            '_daily_flow_mark_status': lambda *args, **kwargs: True,
            '_throttled_write': lambda *args, **kwargs: None,
        })

        self.assertTrue(ns['_share_mark_runtime_success'](
            context, evidence={
                'target_match': True,
                'selected_count': 1,
                'confirm_clicked': True,
                'dialog_closed': True,
            },
        ))
        sync.assert_called_once_with(context, today=today, force=True)

    def test_share_success_counter_does_not_rewrite_already_current_files(self):
        import json
        import tempfile

        ns = load_named_hook_functions('_share_mark_runtime_success')
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            local = root / 'local'
            portable = root / 'UserData' / 'legacy-qq-farm-bot-rev'
            local.mkdir(parents=True)
            portable.mkdir(parents=True)
            today = time.strftime('%Y-%m-%d')
            payload = {
                'share_last_date': today,
                'daily_flow_retry_date': today,
                'daily_flow_retry_counts': {'share': 0},
                'instances': {
                    '1': {
                        'share_last_date': today,
                        'daily_flow_retry_date': today,
                        'daily_flow_retry_counts': {'share': 0},
                    }
                },
            }
            for target in (
                local / 'qq-farm-bot-rev' / 'daily_counters.json',
                portable / 'daily_counters.json',
            ):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(payload), encoding='utf-8')

            os_proxy = types.SimpleNamespace(
                environ={'LOCALAPPDATA': str(local)},
                path=os.path,
                replace=mock.Mock(side_effect=PermissionError(13, 'locked')),
                getpid=os.getpid,
            )
            ns.update({
                'os': os_proxy,
                'time': time,
                '__file__': str(root / 'hook.py'),
                '_share_clear_retry_backoff': lambda context: None,
                '_throttled_write': lambda *args, **kwargs: None,
            })
            saver = mock.Mock()
            context = types.SimpleNamespace(
                instance_id='1',
                share_last_date='',
                daily_flow_retry_counts={'share': 2},
                save_daily_counters=saver,
            )

            self.assertTrue(ns['_share_mark_runtime_success'](context, evidence={'target_match': True, 'selected_count': 1, 'confirm_clicked': True, 'dialog_closed': True}))
            os_proxy.replace.assert_not_called()
            saver.assert_not_called()
            self.assertEqual(today, context.share_last_date)
            self.assertEqual(0, context.daily_flow_retry_counts['share'])



class ShareDirectRecipientSelectorTests(unittest.TestCase):
    def test_vendored_uia_runtime_packages_are_present(self):
        self.assertTrue((ROOT / "portable" / "pywinauto" / "__init__.py").is_file())
        self.assertTrue((ROOT / "portable" / "comtypes" / "__init__.py").is_file())
        self.assertTrue((ROOT / "portable" / "six.py").is_file())
        self.assertTrue((ROOT / "portable" / "win32gui_struct.py").is_file())
        self.assertTrue((ROOT / "portable" / "win32con.py").is_file())
        self.assertTrue((ROOT / "portable" / "commctrl.py").is_file())

    def test_group_creation_dialog_is_detected_before_target_entry(self):
        ns = load_named_hook_functions("_share_dialog_text_indicates_group_mode")
        detect = ns["_share_dialog_text_indicates_group_mode"]

        self.assertTrue(detect(["\u521b\u5efa\u7fa4\u804a", "\u521b\u5efa\u5e76\u53d1\u9001", "\u8fd4\u56de"]))
        self.assertFalse(detect(["\u53d1\u9001\u7ed9", "\u5df2\u9009\u62e9 1 \u4eba", "\u53d1\u9001"]))

    def test_direct_send_header_overrides_hidden_group_creation_artifacts(self):
        ns = load_named_hook_functions("_share_dialog_text_indicates_group_mode")
        detect = ns["_share_dialog_text_indicates_group_mode"]

        self.assertFalse(detect([
            "\u53d1\u9001\u7ed9", "\u5df2\u9009\u62e9 1 \u4eba", "\u786e\u5b9a",
            "\u521b\u5efa\u7fa4\u804a", "\u521b\u5efa\u5e76\u53d1\u9001",
        ]))

    def test_single_target_proof_accepts_direct_dialog_with_hidden_group_artifacts(self):
        ns = load_named_hook_functions(
            "_share_dialog_text_indicates_group_mode",
            "_share_single_target_selection_proof",
        )
        matched = object()
        confirm = object()
        ns.update({
            "_share_uia_candidate_is_group": lambda element: False,
            "_share_uia_dialog_texts": lambda hwnd: [
                "\u53d1\u9001\u7ed9", "\u5df2\u9009\u62e9 1 \u4eba", "\u786e\u5b9a",
                "\u521b\u5efa\u7fa4\u804a", "\u521b\u5efa\u5e76\u53d1\u9001",
            ],
            "_share_selected_contact_count": lambda texts: 1,
            "_share_find_uia_button": lambda hwnd, labels: confirm,
            "_share_confirm_label_is_direct_send": lambda element: element is confirm,
        })

        proof = ns["_share_single_target_selection_proof"](77, "1000000001", matched)
        self.assertTrue(proof["ok"], proof)
        self.assertEqual("single-exact-target", proof["reason"])

    def test_group_creation_dialog_uses_back_button_to_recover_direct_send(self):
        ns = load_named_hook_functions("_share_recover_direct_dialog_from_group_mode")
        back = object()
        states = iter((
            ["\u521b\u5efa\u7fa4\u804a", "\u521b\u5efa\u5e76\u53d1\u9001", "\u8fd4\u56de"],
            ["\u53d1\u9001\u7ed9", "\u5df2\u9009\u62e9 0 \u4eba", "\u53d1\u9001"],
        ))
        clicks = []
        ns.update({
            "_share_uia_dialog_texts": lambda hwnd: next(states),
            "_share_dialog_text_indicates_group_mode": (
                lambda texts: any("\u521b\u5efa\u7fa4\u804a" in str(x) or "\u521b\u5efa\u5e76\u53d1\u9001" in str(x) for x in texts)
            ),
            "_share_find_uia_button": lambda hwnd, labels: back,
            "_share_click_uia_element": lambda element: clicks.append(element) or True,
            "time": type("Clock", (), {
                "monotonic": staticmethod(iter((0.0, 0.1, 0.2)).__next__),
                "sleep": staticmethod(lambda seconds: None),
            }),
        })

        self.assertTrue(ns["_share_recover_direct_dialog_from_group_mode"](77, 500))
        self.assertEqual([back], clicks)

    def test_exact_contact_selection_prefers_exposed_radio_button(self):
        ns = load_named_hook_functions("_share_select_exact_contact")
        target = object()
        radio = object()
        clicks = []
        ns.update({
            "_share_uia_candidate_is_group": lambda element: False,
            "_share_find_exact_uia_selector": lambda element: radio,
            "_share_click_uia_element": lambda element: clicks.append(element) or True,
            "_share_exact_selector_point": lambda element: self.fail("coordinate fallback used"),
            "_share_click_abs": lambda x, y: self.fail("absolute click used"),
        })

        self.assertTrue(ns["_share_select_exact_contact"](77, target))
        self.assertEqual([radio], clicks)

    def test_exact_contact_selection_can_click_circle_derived_from_exact_row(self):
        ns = load_named_hook_functions("_share_select_exact_contact")
        target = object()
        clicks = []
        ns.update({
            "_share_uia_candidate_is_group": lambda element: False,
            "_share_find_exact_uia_selector": lambda element: None,
            "_share_exact_selector_point": lambda element: (124, 250),
            "_share_click_abs": lambda x, y: clicks.append((x, y)) or True,
        })

        self.assertTrue(ns["_share_select_exact_contact"](77, target))
        self.assertEqual([(124, 250)], clicks)

    def test_exact_selector_point_is_inside_left_side_of_matched_contact_row(self):
        ns = load_named_hook_functions("_share_exact_selector_point")

        class Rect:
            left, top, right, bottom = 100, 200, 500, 300

        class Element:
            def rectangle(self):
                return Rect()

            def parent(self):
                return None

        x, y = ns["_share_exact_selector_point"](Element())
        self.assertTrue(116 <= x <= 136)
        self.assertEqual(250, y)



    def test_uia_backend_prepares_comtypes_gen_before_importing_pywinauto(self):
        ns = load_named_hook_functions(
            "_share_prepare_uia_runtime",
            "_share_uia_backend_available",
        )
        calls = []
        ns["_share_prepare_uia_runtime"] = lambda: calls.append("prepare") or True

        self.assertTrue(ns["_share_uia_backend_available"]())
        self.assertEqual(["prepare"], calls)

    def test_uia_runtime_injects_memory_gen_package_when_submodule_import_fails(self):
        import importlib

        ns = load_named_hook_functions("_share_prepare_uia_runtime")
        fake_comtypes = types.SimpleNamespace(
            __file__=str(ROOT / "portable" / "comtypes" / "__init__.py"),
            __path__=[str(ROOT / "portable" / "comtypes")],
        )
        fake_pywinauto = object()

        def fake_import(name):
            if name == "comtypes":
                return fake_comtypes
            if name == "comtypes.gen":
                raise ImportError("synthetic frozen-package submodule failure")
            if name == "pywinauto":
                self.assertTrue(hasattr(fake_comtypes, "gen"))
                self.assertIn("comtypes.gen", sys.modules)
                return fake_pywinauto
            raise AssertionError(name)

        old_gen = sys.modules.pop("comtypes.gen", None)
        try:
            with mock.patch.object(importlib, "import_module", side_effect=fake_import):
                self.assertTrue(ns["_share_prepare_uia_runtime"]())
            self.assertIs(fake_comtypes.gen, sys.modules["comtypes.gen"])
            self.assertEqual(
                [str(ROOT / "portable" / "comtypes" / "gen")],
                list(fake_comtypes.gen.__path__),
            )
        finally:
            sys.modules.pop("comtypes.gen", None)
            if old_gen is not None:
                sys.modules["comtypes.gen"] = old_gen


    def test_share_entry_preflight_blocks_native_template_click_after_completion(self):
        namespace = load_named_hook_functions("_wrap_share_entry_settle_func")
        events = []
        context = types.SimpleNamespace()
        namespace.update({
            "time": types.SimpleNamespace(sleep=lambda seconds: None),
            "_daily_entry_call_kind": lambda args, kwargs: "share_entry",
            "_share_context_from_call": lambda args, kwargs: context,
            "_share_preflight_completed": (
                lambda bot: events.append(("preflight", bot)) or True
            ),
            "_stop_requested_in_args": lambda args, kwargs: False,
            "_stop_gate_return": lambda name: False,
            "_share_click_result_succeeded": lambda value: bool(value),
            "_share_int_cfg": lambda key, default: default,
            "_throttled_write": lambda *args, **kwargs: None,
            "_share_log_runtime": lambda *args, **kwargs: None,
        })

        wrapped, patched = namespace["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: events.append(("native-click", args)) or True
        )
        self.assertTrue(patched)
        self.assertFalse(wrapped(context, "share_entry"))
        self.assertEqual([("preflight", context)], events)


class SharePostSendPauseTests(unittest.TestCase):
    def test_target_sender_rechecks_pause_after_direct_send_before_recording(self):
        """A stop raised while the direct-send dialog closes suppresses late success writes."""
        namespace = load_named_hook_functions("_share_search_and_maybe_confirm")
        state = configure_strict_share_namespace(namespace)
        paused = {"value": False}
        context = types.SimpleNamespace()

        def hard_gate(bot, phase, cfg=None):
            state["events"].append(("hard-gate", phase, paused["value"]))
            return paused["value"]

        def dialog_closed(mod=None, timeout_ms=0):
            state["events"].append(("dialog-closed",))
            paused["value"] = True
            return True

        namespace.update({
            "_share_action_blocked": hard_gate,
            "_share_wait_dialog_closed": dialog_closed,
        })
        cfg = {
            "target_name": "1000000001",
            "allow_group": False,
            "dry_run": False,
        }

        self.assertFalse(namespace["_share_search_and_maybe_confirm"](
            types.SimpleNamespace(), cfg, context=context
        ))
        self.assertEqual([], state["recorded"])
        self.assertTrue(any(
            item[0] == "hard-gate" and item[1] == "target-confirm-after-direct-send"
            and item[2]
            for item in state["events"]
        ))



if __name__ == "__main__":
    unittest.main()
