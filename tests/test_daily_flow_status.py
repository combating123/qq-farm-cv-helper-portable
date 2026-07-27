import ast
import os
import tempfile
import time
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
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


STATUS_FUNCTIONS = (
    "_daily_flow_status_paths",
    "_daily_flow_read_status",
    "_daily_flow_write_status",
    "_daily_flow_mark_status",
    "_daily_flow_success_today",
    "_daily_flow_mark_failure",
    "_daily_flow_retry_blocked",
    "_daily_flow_repair_unverified_status",
    "_daily_flow_key",
    "_daily_flow_context_from_args",
    "_daily_flow_target",
    "_daily_flow_apply_success_context",
    "_daily_flow_context_success_today",
    "_daily_entry_red_dot_present",
    "_daily_flow_entry_red_dot_state",
    "_daily_flow_invalidate_success",
    "_patch_daily_flow_status_for_module",
)


class DailyFlowStatusTests(unittest.TestCase):
    def build_namespace(self, temp_dir):
        namespace = load_functions(*STATUS_FUNCTIONS)
        os_proxy = types.SimpleNamespace(
            environ={**os.environ, "LOCALAPPDATA": temp_dir},
            path=os.path,
            PathLike=os.PathLike,
            fspath=os.fspath,
            makedirs=os.makedirs,
            replace=os.replace,
            getpid=os.getpid,
            remove=os.remove,
        )
        namespace.update({
            "os": os_proxy,
            "time": time,
            "__file__": str(Path(temp_dir) / "hook.py"),
            "_DAILY_FLOW_STATUS_PATCH_LOG_SEEN": set(),
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_cfg_get": lambda *args, **kwargs: "2135736062",
            "_active_bot_sections": lambda: ("bot", "instance.1.bot"),
            "_daily_retry_max_default": lambda value=None: 3,
        })
        return namespace

    def build_module(self, events):
        module = types.ModuleType("bot.synthetic.freebenefits_flow")

        def mark_success(bot, flow):
            events.append(("verified-success", flow))
            setattr(bot, flow + "_last_date", time.strftime("%Y-%m-%d"))
            return True

        def mark_failure(bot, flow):
            events.append(("failure", flow))
            bot.daily_flow_retry_counts[flow] = (
                bot.daily_flow_retry_counts.get(flow, 0) + 1
            )
            return False

        module._mark_daily_flow_success = mark_success
        module._mark_daily_flow_failure = mark_failure
        module.should_run_daily_task = lambda bot: events.append(("should-task",)) or True
        module.run_daily_task = lambda bot: events.append(("run-task",)) or True
        module.should_run_daily_share = lambda bot: events.append(("should-share",)) or True
        module.run_daily_share = lambda bot: events.append(("run-share",)) or True
        return module

    def test_patch_function_exists_for_all_daily_flows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            self.assertTrue(callable(namespace.get("_patch_daily_flow_status_for_module")))

    def test_unverified_run_return_does_not_mark_task_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            patch = namespace.get("_patch_daily_flow_status_for_module")
            self.assertTrue(callable(patch))
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.run_daily_task(bot))
            self.assertFalse(namespace["_daily_flow_success_today"]("task"))
            self.assertIn(("run-task",), events)

    def test_verified_success_skips_all_same_day_task_ui_after_restart(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 2, "svip": 0, "share": 0,
                },
            )
            first_patch = first.get("_patch_daily_flow_status_for_module")
            self.assertTrue(callable(first_patch))
            first_patch(module)
            self.assertTrue(module._mark_daily_flow_success(bot, "task"))
            self.assertTrue(first["_daily_flow_success_today"]("task"))
            self.assertEqual(0, bot.daily_flow_retry_counts["task"])

            second = self.build_namespace(temp_dir)
            restarted_events = []
            restarted_module = self.build_module(restarted_events)
            restarted_bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            second_patch = second.get("_patch_daily_flow_status_for_module")
            self.assertTrue(callable(second_patch))
            second_patch(restarted_module)

            self.assertFalse(restarted_module.should_run_daily_task(restarted_bot))
            self.assertTrue(restarted_module.run_daily_task(restarted_bot))
            self.assertEqual([], restarted_events)
            self.assertEqual(time.strftime("%Y-%m-%d"), restarted_bot.task_last_date)

    def test_failure_after_success_does_not_increment_retry_or_replace_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                daily_flow_retry_counts={"task": 0},
            )
            patch = namespace.get("_patch_daily_flow_status_for_module")
            self.assertTrue(callable(patch))
            patch(module)
            self.assertTrue(module._mark_daily_flow_success(bot, "task"))
            self.assertFalse(module._mark_daily_flow_failure(bot, "task"))
            self.assertEqual(0, bot.daily_flow_retry_counts["task"])
            self.assertEqual([("verified-success", "task")], events)
            self.assertTrue(namespace["_daily_flow_success_today"]("task"))

    def test_each_daily_item_has_independent_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            for flow in ("freebenefits", "task", "share", "svip"):
                target = "2135736062" if flow == "share" else ""
                self.assertTrue(namespace["_daily_flow_mark_status"](
                    flow, "success", target=target
                ))
            for flow in ("freebenefits", "task", "share", "svip"):
                target = "2135736062" if flow == "share" else ""
                self.assertTrue(namespace["_daily_flow_success_today"](
                    flow, target=target
                ))


    def test_seeded_task_status_is_not_treated_as_verified_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task",
                "success",
                today=today,
                reason="seeded-from-daily-counters",
            ))
            bot = types.SimpleNamespace(
                task_last_date=today,
                daily_flow_retry_counts={"task": 0},
            )

            self.assertFalse(namespace["_daily_flow_success_today"](
                "task", today=today
            ))
            self.assertFalse(namespace["_daily_flow_context_success_today"](
                bot, "task", today=today
            ))
            self.assertEqual("", bot.task_last_date)

    def test_context_date_alone_does_not_create_a_success_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                task_last_date=today,
                daily_flow_retry_counts={"task": 0},
            )

            self.assertFalse(namespace["_daily_flow_context_success_today"](
                bot, "task", today=today
            ))
            self.assertFalse(namespace["_daily_flow_success_today"](
                "task", today=today
            ))
            self.assertEqual("", bot.task_last_date)



    def test_repair_migrates_seeded_task_and_benefits_but_preserves_share(self):
        import json

        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            repair = namespace.get("_daily_flow_repair_unverified_status")
            if repair is None:
                self.fail("_daily_flow_repair_unverified_status is missing")
            today = time.strftime("%Y-%m-%d")
            status_path = Path(temp_dir) / "daily_flow_status.json"
            counters_path = Path(temp_dir) / "daily_counters.json"
            status_path.write_text(json.dumps({
                "date": today,
                "flows": {
                    "freebenefits": {
                        "date": today,
                        "status": "success",
                        "reason": "seeded-from-daily-counters",
                    },
                    "task": {
                        "date": today,
                        "status": "success",
                        "reason": "seeded-from-daily-counters",
                    },
                    "share": {
                        "date": today,
                        "status": "success",
                        "reason": "seeded-from-daily-counters",
                        "target": "2135736062",
                    },
                },
            }), encoding="utf-8")
            counters_path.write_text(json.dumps({
                "task_last_date": today,
                "freebenefits_last_date": today,
                "share_last_date": today,
                "instances": {
                    "1": {
                        "task_last_date": today,
                        "freebenefits_last_date": today,
                        "share_last_date": today,
                    }
                },
            }), encoding="utf-8")

            self.assertTrue(repair(
                paths=[str(status_path)],
                counter_paths=[str(counters_path)],
                today=today,
            ))

            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual("pending", status["flows"]["task"]["status"])
            self.assertEqual("pending", status["flows"]["freebenefits"]["status"])
            self.assertEqual("success", status["flows"]["share"]["status"])
            counters = json.loads(counters_path.read_text(encoding="utf-8"))
            self.assertEqual("", counters["task_last_date"])
            self.assertEqual("", counters["freebenefits_last_date"])
            self.assertEqual(today, counters["share_last_date"])
            self.assertEqual("", counters["instances"]["1"]["task_last_date"])
            self.assertEqual(
                "", counters["instances"]["1"]["freebenefits_last_date"]
            )
            self.assertEqual(
                today, counters["instances"]["1"]["share_last_date"]
            )



    def test_same_day_share_date_is_preserved_to_prevent_duplicate_send(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                share_last_date=today,
                daily_flow_retry_counts={"share": 0},
            )

            self.assertTrue(namespace["_daily_flow_context_success_today"](
                bot, "share", today=today
            ))
            self.assertEqual(today, bot.share_last_date)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "share", target="2135736062", today=today
            ))


    def test_share_and_task_red_dots_are_detected_in_their_home_entry_regions(self):
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        detect = namespace["_daily_entry_red_dot_present"]
        share_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        share_frame[150:160, 62:72, 2] = 245
        task_frame = np.zeros((800, 428, 3), dtype=np.uint8)
        task_frame[640:651, 50:61, 2] = 245

        self.assertTrue(detect(share_frame, "share"))
        self.assertTrue(detect(task_frame, "task"))
        self.assertFalse(detect(np.zeros((800, 428, 3), dtype=np.uint8), "share"))

    def test_red_dot_invalidates_same_day_success_and_allows_a_retry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date=time.strftime("%Y-%m-%d"),
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "share" else None
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.should_run_daily_share(bot))
            self.assertEqual("", bot.share_last_date)
            self.assertIn(("should-share",), events)

    def test_cleared_red_dot_marks_flow_success_without_reopening_ui(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "task" else None
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertFalse(module.should_run_daily_task(bot))
            self.assertEqual(time.strftime("%Y-%m-%d"), bot.task_last_date)
            self.assertTrue(namespace["_daily_flow_success_today"]("task"))
            self.assertIn(("should-task",), events)




    def test_share_red_dot_does_not_invalidate_verified_direct_send(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                share_last_date=today,
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "share", "success", target="2135736062", today=today
            ))
            namespace["_share_direct_success_recent"] = (
                lambda target="", max_age=15.0:
                target == "2135736062" and max_age >= 86400.0
            )

            self.assertTrue(namespace["_daily_flow_invalidate_success"](
                bot, "share", reason="entry-red-dot-still-present"
            ))

            self.assertEqual(today, bot.share_last_date)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "share", target="2135736062", today=today
            ))

    def test_red_dot_preserves_active_failed_backoff_instead_of_reopening_share(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                share_last_date=today,
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 1,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_failure"](
                "share",
                reason="exact contact not selected",
                today=today,
                now_epoch=time.time(),
            ))
            self.assertTrue(namespace["_daily_flow_retry_blocked"](
                "share", today=today, now_epoch=time.time()
            ))

            self.assertTrue(namespace["_daily_flow_invalidate_success"](
                bot, "share", reason="entry-red-dot-still-present"
            ))

            self.assertEqual("", bot.share_last_date)
            self.assertTrue(namespace["_daily_flow_retry_blocked"](
                "share", today=today, now_epoch=time.time()
            ))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("failed", status["flows"]["share"]["status"])


if __name__ == "__main__":
    unittest.main()
