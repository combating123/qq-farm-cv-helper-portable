import ast
import copy
import os
import time
import types
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
DAY = "2026-08-10"
TARGET = "1000000001"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def freebenefits_frame(claimable=True):
    frame = np.zeros((800, 428, 3), dtype=np.uint8)
    frame[255:505, 35:205] = (125, 182, 218)
    frame[458:495, 45:198] = (
        (95, 170, 220) if claimable else (90, 95, 105)
    )
    return frame


class V454DailyClaimAndVipStatusTests(unittest.TestCase):
    def test_startup_reopens_unverified_freebenefits_and_pre_send_reward(self):
        namespace = load_functions("_daily_flow_repair_unverified_status")
        store = {
            "status.json": {
                "_revision": 7,
                "date": DAY,
                "flows": {
                    "freebenefits": {
                        "date": DAY,
                        "status": "success",
                        "reason": "native-completion-date-transition",
                        "verified_at": DAY + "T15:13:33+0800",
                    },
                    "share": {
                        "date": DAY,
                        "status": "success",
                        "reason": "verified-direct-contact-send-v2",
                        "target": TARGET,
                        "verified_at": DAY + "T15:39:58+0800",
                    },
                    "share_reward": {
                        "date": DAY,
                        "status": "success",
                        "reason": "verified-share-reward-claimed-v2",
                        "target": TARGET,
                        "verified_at": DAY + "T13:39:56+0800",
                    },
                },
            }
        }

        def read_status(path):
            return copy.deepcopy(store[path])

        def write_status(path, payload):
            store[path] = copy.deepcopy(payload)
            return True

        def commit(path, flow, entry, today=None, mutate=None):
            payload = copy.deepcopy(store[path])
            current = payload.get("flows", {}).get(flow)
            next_entry = mutate(payload, current, today) if callable(mutate) else entry
            if next_entry is None:
                return True
            payload.setdefault("flows", {})[flow] = copy.deepcopy(next_entry)
            payload["_revision"] = int(payload.get("_revision", 0)) + 1
            store[path] = payload
            return True

        namespace.update({
            "os": os,
            "time": types.SimpleNamespace(
                strftime=lambda fmt: (
                    DAY if fmt == "%Y-%m-%d" else DAY + "T16:00:00+0800"
                )
            ),
            "_daily_business_date": lambda: DAY,
            "_daily_flow_status_paths": lambda paths=None: ["status.json"],
            "_daily_flow_read_status": read_status,
            "_daily_flow_write_status": write_status,
            "_daily_flow_commit": commit,
        })

        self.assertTrue(namespace["_daily_flow_repair_unverified_status"](
            counter_paths=[], today=DAY
        ))
        flows = store["status.json"]["flows"]
        self.assertEqual("pending", flows["freebenefits"]["status"])
        self.assertEqual(
            "legacy-success-requires-verification",
            flows["freebenefits"]["reason"],
        )
        self.assertEqual("success", flows["share"]["status"])
        self.assertEqual("pending", flows["share_reward"]["status"])
        self.assertEqual(
            "legacy-success-requires-verification",
            flows["share_reward"]["reason"],
        )

    def test_startup_preserves_user_confirmed_manual_freebenefits_claim(self):
        namespace = load_functions("_daily_flow_repair_unverified_status")
        store = {
            "status.json": {
                "_revision": 8,
                "date": DAY,
                "flows": {
                    "freebenefits": {
                        "date": DAY,
                        "status": "success",
                        "reason": "user-confirmed-manual-claim-v1",
                        "verified_at": DAY + "T17:45:00+0800",
                    },
                },
            }
        }

        def read_status(path):
            return copy.deepcopy(store[path])

        def write_status(path, payload):
            store[path] = copy.deepcopy(payload)
            return True

        def commit(path, flow, entry, today=None, mutate=None):
            payload = copy.deepcopy(store[path])
            current = payload.get("flows", {}).get(flow)
            next_entry = mutate(payload, current, today) if callable(mutate) else entry
            if next_entry is None:
                return True
            payload.setdefault("flows", {})[flow] = copy.deepcopy(next_entry)
            store[path] = payload
            return True

        namespace.update({
            "os": os,
            "time": types.SimpleNamespace(
                strftime=lambda fmt: (
                    DAY if fmt == "%Y-%m-%d" else DAY + "T17:45:00+0800"
                )
            ),
            "_daily_business_date": lambda: DAY,
            "_daily_flow_status_paths": lambda paths=None: ["status.json"],
            "_daily_flow_read_status": read_status,
            "_daily_flow_write_status": write_status,
            "_daily_flow_commit": commit,
        })

        self.assertFalse(namespace["_daily_flow_repair_unverified_status"](
            counter_paths=[], today=DAY
        ))
        entry = store["status.json"]["flows"]["freebenefits"]
        self.assertEqual("success", entry["status"])
        self.assertEqual("user-confirmed-manual-claim-v1", entry["reason"])

    def test_freebenefits_detector_and_click_transition_use_the_real_card(self):
        namespace = load_functions(
            "_freebenefits_claim_button_center_from_rgb",
            "_freebenefits_claim_transition_verified",
        )
        before = freebenefits_frame(True)
        after = freebenefits_frame(False)
        home = np.zeros((800, 428, 3), dtype=np.uint8)

        center = namespace["_freebenefits_claim_button_center_from_rgb"](before)
        self.assertIsNotNone(center)
        self.assertAlmostEqual(121, center[0], delta=4)
        self.assertAlmostEqual(477, center[1], delta=4)
        self.assertEqual((428, 800), tuple(center[2:4]))
        self.assertIsNone(
            namespace["_freebenefits_claim_button_center_from_rgb"](home)
        )
        self.assertTrue(namespace["_freebenefits_claim_transition_verified"](
            before, after
        ))
        self.assertFalse(namespace["_freebenefits_claim_transition_verified"](
            before, before.copy()
        ))

    def test_freebenefits_fallback_clicks_visible_free_card_and_records_visual_proof(self):
        namespace = load_functions(
            "_daily_entry_call_kind",
            "_share_click_result_succeeded",
            "_freebenefits_claim_button_center_from_rgb",
            "_freebenefits_claim_transition_verified",
            "_wrap_share_entry_settle_func",
        )
        before = freebenefits_frame(True)
        after = freebenefits_frame(False)
        frames = iter((before, after))
        clicks = []
        context = types.SimpleNamespace()
        clock = types.SimpleNamespace(
            sleep=lambda _seconds: None,
            strftime=lambda _fmt: DAY,
        )
        namespace.update({
            "time": clock,
            "_daily_business_date": lambda: DAY,
            "_stop_requested_in_args": lambda *args, **kwargs: False,
            "_daily_flow_context_from_args": lambda args, kwargs: context,
            "_share_context_from_call": lambda args, kwargs: context,
            "_share_prompt_frame_from_call": lambda args, kwargs: None,
            "_get_frame_from_bot": lambda bot: next(frames),
            "_friend_guard_post_client_click": (
                lambda x, y, w=428, h=800:
                clicks.append((x, y, w, h)) or True
            ),
            "_throttled_write": lambda *args, **kwargs: None,
        })

        wrapped, changed = namespace["_wrap_share_entry_settle_func"](
            lambda *args, **kwargs: False
        )
        self.assertTrue(changed)
        self.assertTrue(wrapped(context, tag="freebenefits"))
        self.assertEqual([(121, 477, 428, 800)], clicks)
        self.assertEqual(
            DAY, context._qqfarm_freebenefits_claim_verified_day
        )

    def test_claimed_share_reward_requires_current_reward_page_proof(self):
        namespace = load_functions("_share_reward_claimed_visible")
        frame = np.zeros((1200, 640, 3), dtype=np.uint8)
        frame[986:1014, 102:148] = (55, 188, 65)
        frame[956:1032, 342:558] = (160, 205, 12)
        context = types.SimpleNamespace()
        namespace.update({
            "_get_frame_from_bot": lambda bot: frame,
            "_throttled_write": lambda *args, **kwargs: None,
            "_qqfarm_visible_frame_has_farm_scene": lambda image: False,
        })

        self.assertFalse(namespace["_share_reward_claimed_visible"](context))
        context._qqfarm_share_reward_open_attempt_epoch = 1.0
        self.assertTrue(namespace["_share_reward_claimed_visible"](context))

    def test_candidate_due_keeps_share_reward_pending_after_send_success(self):
        namespace = load_functions("_native_v225_daily_candidate_due")
        namespace.update({
            "_native_v225_daily_home_ready": lambda context: True,
            "_native_v225_daily_schedule_due": lambda *args, **kwargs: True,
            "_share_target_guard_config": lambda: {
                "enabled": True, "target_name": TARGET
            },
            "_daily_flow_target": lambda flow: TARGET,
            "_daily_flow_success_today": (
                lambda flow, **kwargs: flow == "share"
            ),
            "_daily_flow_retry_blocked": lambda flow: False,
        })

        self.assertTrue(namespace["_native_v225_daily_candidate_due"](
            types.SimpleNamespace(), "share", require_home=True
        ))

    def test_catchup_runs_reward_only_after_verified_direct_send(self):
        namespace = load_functions(
            "_native_v225_daily_home_ready",
            "_run_native_v225_daily_catchup",
        )
        events = []
        context = types.SimpleNamespace(_qqfarm_live_scene_hint="home")
        namespace.update({
            "_daily_flow_success_today": (
                lambda flow, **kwargs: flow == "share"
            ),
            "_daily_flow_attempted_today": lambda *args, **kwargs: False,
            "_daily_flow_entry_red_dot_state": lambda *args, **kwargs: None,
            "_native_v225_daily_flow_module": lambda: None,
            "_native_v225_daily_flow_due": lambda context, flow: False,
            "_run_share_prompt_recovery": (
                lambda bot: events.append(("share-reward", bot)) or True
            ),
            "_daily_business_date": lambda: DAY,
        })

        self.assertEqual(
            "share-reward",
            namespace["_run_native_v225_daily_catchup"](context),
        )
        self.assertEqual([("share-reward", context)], events)

    def test_claimed_reward_preempts_false_claim_button_and_closes_page(self):
        namespace = load_functions("_run_share_prompt_recovery")
        events = []
        context = types.SimpleNamespace()
        namespace.update({
            "time": types.SimpleNamespace(strftime=lambda fmt: DAY),
            "_daily_business_date": lambda: DAY,
            "_QQFARM_SHARE_RECOVERY_COMPLETED_DAY": "",
            "_share_target_guard_config": lambda: {
                "enabled": True, "target_name": TARGET
            },
            "_daily_flow_success_today": (
                lambda flow, **kwargs: flow == "share"
            ),
            "_daily_flow_apply_success_context": lambda *args, **kwargs: True,
            "_share_clear_retry_backoff": lambda *args, **kwargs: True,
            "_share_action_blocked": lambda *args, **kwargs: False,
            "_share_reward_claimed_visible": (
                lambda bot: events.append("claimed-check") or True
            ),
            "_share_reward_claim_available_visible": (
                lambda bot: events.append("available-check") or True
            ),
            "_share_click_reward_claim": (
                lambda bot: (_ for _ in ()).throw(
                    AssertionError("claimed reward must not click the share button")
                )
            ),
            "_share_mark_reward_claimed_success": (
                lambda bot, cfg: events.append("persist-reward") or True
            ),
            "_share_target_module": lambda: "share-module",
            "_share_find_dialog_hwnd": (
                lambda module: events.append(("find-dialog", module)) or 12345
            ),
            "_share_close_dialog": (
                lambda module, hwnd: events.append(
                    ("close-dialog", module, hwnd)
                ) or True
            ),
            "_share_wait_dialog_closed": (
                lambda module, timeout_ms=0: events.append(
                    ("wait-dialog-closed", module, timeout_ms)
                ) or True
            ),
            "_share_close_share_page": (
                lambda bot: events.append("close-share-page") or True
            ),
        })

        self.assertTrue(namespace["_run_share_prompt_recovery"](context))
        self.assertEqual(
            [
                "claimed-check",
                "persist-reward",
                ("find-dialog", "share-module"),
                ("close-dialog", "share-module", 12345),
                ("wait-dialog-closed", "share-module", 1200),
                "close-share-page",
            ],
            events,
        )

    def test_restart_adopts_visible_checked_reward_page_without_process_lease(self):
        namespace = load_functions("_run_share_prompt_recovery")
        events = []
        context = types.SimpleNamespace()
        namespace.update({
            "time": types.SimpleNamespace(strftime=lambda fmt: DAY),
            "_daily_business_date": lambda: DAY,
            "_QQFARM_SHARE_RECOVERY_COMPLETED_DAY": "",
            "_share_target_guard_config": lambda: {
                "enabled": True, "target_name": TARGET
            },
            "_daily_flow_success_today": (
                lambda flow, **kwargs: flow == "share"
            ),
            "_daily_flow_apply_success_context": lambda *args, **kwargs: True,
            "_share_clear_retry_backoff": lambda *args, **kwargs: True,
            "_share_action_blocked": lambda *args, **kwargs: False,
            "_share_reward_claimed_visible": (
                lambda bot: events.append("leased-check") or False
            ),
            "_share_reward_claimed_current_page_visible": (
                lambda bot: events.append("restart-visible-check") or True
            ),
            "_share_reward_claim_available_visible": (
                lambda bot: (_ for _ in ()).throw(
                    AssertionError("checked page must preempt claim-button detection")
                )
            ),
            "_share_click_reward_claim": (
                lambda bot: (_ for _ in ()).throw(
                    AssertionError("checked page must not reopen the QQ picker")
                )
            ),
            "_share_mark_reward_claimed_success": (
                lambda bot, cfg: events.append("persist-reward") or True
            ),
            "_share_target_module": lambda: None,
            "_share_find_dialog_hwnd": lambda module: 0,
            "_share_close_share_page": (
                lambda bot: events.append("close-share-page") or True
            ),
        })

        self.assertTrue(namespace["_run_share_prompt_recovery"](context))
        self.assertEqual(
            [
                "leased-check",
                "restart-visible-check",
                "persist-reward",
                "close-share-page",
            ],
            events,
        )

    def test_current_page_probe_uses_fresh_overlay_capture_not_stale_bot_frame(self):
        namespace = load_functions(
            "_share_reward_claimed_visible",
            "_share_reward_claimed_current_page_visible",
        )
        stale = np.zeros((800, 428, 3), dtype=np.uint8)
        current = np.zeros((1200, 642, 3), dtype=np.uint8)
        current[986:1014, 102:148] = (55, 188, 65)
        current[956:1032, 342:558] = (160, 205, 12)
        calls = []
        context = types.SimpleNamespace()

        def capture(*, prefer_desktop=False, allow_overlay=False):
            calls.append((prefer_desktop, allow_overlay))
            return current

        namespace.update({
            "_get_frame_from_bot": lambda bot: stale,
            "_qqfarm_capture_visible_farm_frame": capture,
            # The share modal still shows farm sky behind it, so the broad
            # farm-scene classifier is true even though the reward page is
            # the foreground transaction surface.
            "_qqfarm_visible_frame_has_farm_scene": lambda image: True,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(
            namespace["_share_reward_claimed_current_page_visible"](context)
        )
        self.assertEqual([(True, True)], calls)

    def test_reward_claim_detector_rejects_oversized_warm_share_panel(self):
        namespace = load_functions("_share_reward_claim_button_center")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        # The current claimed page has one large warm panel containing the green
        # ?? button. It is not the compact yellow reward-claim action.
        frame[560:800, 79:428] = (45, 180, 220)
        self.assertIsNone(
            namespace["_share_reward_claim_button_center"](frame)
        )

    def test_activated_button_opens_local_membership_status(self):
        namespace = load_functions("_apply_vip_dialog_text_fix")
        opened = []

        class Signal:
            def __init__(self):
                self.callbacks = []

            def connect(self, callback):
                self.callbacks.append(callback)

            def emit(self):
                for callback in list(self.callbacks):
                    callback(False)

        class Widget:
            def __init__(self):
                self.clicked = Signal()
                self._text = "已激活"
                self._tip = ""
                self.props = {}

            def setText(self, value):
                self._text = value

            def text(self):
                return self._text

            def toolTip(self):
                return self._tip

            def setToolTip(self, value):
                self._tip = value

            def property(self, key):
                return self.props.get(key)

            def setProperty(self, key, value):
                self.props[key] = value

        widget = Widget()
        namespace.update({
            "_obj_name": lambda obj: "btnVipAccess",
            "_text_of": lambda obj: obj.text(),
            "_safe_str": str,
            "_replace_inactive_text": lambda value: value,
            "_show_vip_status_dialog": (
                lambda anchor=None: opened.append(anchor) or True
            ),
        })

        namespace["_apply_vip_dialog_text_fix"](widget)
        self.assertEqual(1, len(widget.clicked.callbacks))
        widget.clicked.emit()
        self.assertEqual([widget], opened)


if __name__ == "__main__":
    unittest.main()
