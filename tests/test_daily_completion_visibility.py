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
            "_share_target_guard_config": lambda: {"target_name": "2135736062"},
            "_share_direct_success_recent": (
                lambda target="", max_age=15.0:
                target == "2135736062" and max_age >= 86400.0
            ),
        })

        message, rewritten = namespace["_rewrite_verified_share_failure_log_message"](
            "\u00d7\u672a\u68c0\u6d4b\u5230 share_btn_click\uff0c"
            "\u672c\u6b21\u6bcf\u65e5\u5206\u4eab\u672a\u6267\u884c"
        )

        self.assertTrue(rewritten)
        self.assertIn("\u6bcf\u65e5\u5206\u4eab\u5df2\u6210\u529f", message)
        self.assertIn("2135736062", message)
        self.assertNotIn("\u672a\u6267\u884c", message)


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
                "target_name": "2135736062",
            },
            "_share_target_module": lambda: module,
            "_share_find_dialog_hwnd": lambda mod=None: 0,
            "_get_frame_from_bot": lambda context: frame,
            "_share_direct_success_recent": (
                lambda target="", max_age=15.0:
                state["sent"] and target == "2135736062"
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
            "2135736062",
            evidence={
                "target_match": True,
                "selected_count": 1,
                "confirm_clicked": True,
                "dialog_closed": True,
            },
        ))
        self.assertEqual("2135736062", namespace["_SHARE_DIRECT_SUCCESS_STATE"]["target"])
        self.assertTrue(any("share-complete" in key for key, _ in logs))
        self.assertTrue(any("2135736062" in message for _, message in logs))
        self.assertEqual(
            [("share", "success", "2135736062", "verified-direct-contact-send-v2")],
            marks,
        )


if __name__ == "__main__":
    unittest.main()
