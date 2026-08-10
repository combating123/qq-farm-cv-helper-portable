import ast
import types
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class DailyCompletionVisibilityTests(unittest.TestCase):
    def test_late_native_share_failure_log_is_rewritten_after_v2_success(self):
        namespace = load_functions("_rewrite_verified_share_failure_log_message")
        namespace.update({
            "_share_target_guard_config": lambda: {"target_name": "1000000001"},
            "_share_direct_success_recent": (
                lambda target="", max_age=15.0:
                target == "1000000001" and max_age >= 86400.0
            ),
        })

        message, rewritten = namespace["_rewrite_verified_share_failure_log_message"](
            "\u00d7\u672a\u68c0\u6d4b\u5230 share_btn_click\uff0c"
            "\u672c\u6b21\u6bcf\u65e5\u5206\u4eab\u672a\u6267\u884c"
        )

        self.assertTrue(rewritten)
        self.assertIn("\u6bcf\u65e5\u5206\u4eab\u5df2\u6210\u529f", message)
        self.assertIn("1000000001", message)
        self.assertNotIn("\u672a\u6267\u884c", message)


    def test_native_share_success_between_prompt_click_and_probe_blocks_failure(self):
        namespace = load_functions("_share_recovery_fail")
        events = []
        bot = types.SimpleNamespace()
        cfg = {"enabled": True, "target_name": "1000000001"}
        namespace.update({
            "_share_target_guard_config": lambda: cfg,
            "_share_direct_success_recent": lambda *args, **kwargs: False,
            "_daily_share_authoritative_success_today": (
                lambda context=None, cfg=None: events.append("native-success") or True
            ),
            "_share_mark_reward_claimed_success": (
                lambda context, current_cfg:
                events.append(("persist-reward", current_cfg["target_name"])) or True
            ),
            "_share_set_retry_backoff": (
                lambda context: events.append("backoff")
            ),
            "_daily_flow_mark_failure": (
                lambda *args, **kwargs: events.append("failure") or True
            ),
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertFalse(namespace["_share_recovery_fail"](
            bot, "prompt-not-found"
        ))
        self.assertEqual(
            ["native-success", ("persist-reward", "1000000001")],
            events,
        )

    def test_native_share_reward_completion_log_is_authoritative_same_day_proof(self):
        namespace = load_functions("_daily_share_authoritative_success_today")
        helper = namespace.get(
            "_daily_share_authoritative_success_today",
            lambda *args, **kwargs: False,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            native_log = Path(temp_dir) / "2026-08-05.log"
            native_log.write_text(
                "2026-08-05 13:52:30.847 [INFO] "
                "?????????share_prompt??????????"
                "?????2026-08-05\n",
                encoding="utf-8",
            )
            bot = types.SimpleNamespace()
            cfg = {"enabled": True, "target_name": "1000000001"}
            persisted = []
            namespace.update({
                "_daily_business_date": lambda: "2026-08-05",
                "_daily_share_native_log_paths": (
                    lambda today=None: [str(native_log)]
                ),
                "_share_mark_reward_claimed_success": (
                    lambda context, current_cfg:
                    persisted.append(current_cfg["target_name"]) or True
                ),
            })

            self.assertTrue(helper(bot, cfg=cfg))
            self.assertEqual(["1000000001"], persisted)

    def test_native_share_recovery_passes_current_game_frame_when_required(self):
        namespace = load_functions("_run_share_prompt_recovery")
        calls = []
        frame = object()
        state = {"sent": False}

        def run_daily_share(bot, game_frame):
            calls.append((bot, game_frame))
            state["sent"] = True
            return True

        module = types.SimpleNamespace(run_daily_share=run_daily_share)
        bot = types.SimpleNamespace()
        namespace.update({
            "_share_recovery_due": lambda context: True,
            "_share_target_guard_config": lambda: {
                "enabled": True,
                "target_name": "1000000001",
            },
            "_share_target_module": lambda: module,
            "_share_find_dialog_hwnd": lambda mod=None: 0,
            "_get_frame_from_bot": lambda context: frame,
            "_share_direct_success_recent": (
                lambda target="", max_age=15.0:
                state["sent"] and target == "1000000001"
            ),
            "_share_wait_dialog_hwnd": lambda mod=None, timeout_ms=0: 0,
            "_share_find_prompt_button_center": lambda *args, **kwargs: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertTrue(namespace["_run_share_prompt_recovery"](bot))
        self.assertEqual([(bot, frame)], calls)
        self.assertFalse(bot._qqfarm_share_native_recovery_running)
        self.assertFalse(bot._qqfarm_share_visual_recovery_running)

    def test_verified_share_success_emits_visible_completion_log(self):
        namespace = load_functions("_share_record_direct_success")
        logs = []
        marks = []
        namespace.update({
            "time": types.SimpleNamespace(
                monotonic=lambda: 10.0,
                strftime=lambda _fmt: "2026-07-29",
            ),
            "_SHARE_DIRECT_SUCCESS_STATE": {},
            "_daily_flow_mark_status": (
                lambda flow, status, target="", reason="":
                marks.append((flow, status, target, reason)) or True
            ),
            "_runtime_info_once": lambda key, message: logs.append((key, message)),
        })

        self.assertTrue(namespace["_share_record_direct_success"](
            "1000000001",
            evidence={
                "target_match": True,
                "selected_count": 1,
                "confirm_clicked": True,
                "dialog_closed": True,
            },
        ))
        self.assertEqual("1000000001", namespace["_SHARE_DIRECT_SUCCESS_STATE"]["target"])
        self.assertTrue(any("share-complete" in key for key, _ in logs))
        self.assertTrue(any("1000000001" in message for _, message in logs))
        self.assertEqual(
            [("share", "success", "1000000001", "verified-direct-contact-send-v2")],
            marks,
        )


if __name__ == "__main__":
    unittest.main()
