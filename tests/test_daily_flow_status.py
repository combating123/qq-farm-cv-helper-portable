import ast
import gc
import json
import os
import warnings
import tempfile
import threading
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
    "_daily_flow_unverified_today",
    "_daily_task_native_log_paths",
    "_daily_task_authoritative_success_today",
    "_daily_flow_mark_failure",
    "_daily_flow_retry_blocked",
    "_repair_daily_task_retry_state_file",
    "_daily_flow_repair_unverified_status",
    "_daily_flow_key",
    "_daily_flow_context_from_args",
    "_daily_flow_target",
    "_daily_flow_apply_success_context",
    "_daily_flow_context_success_today",
    "_daily_flow_attempted_today",
    "_daily_entry_red_dot_present",
    "_daily_flow_entry_red_dot_state",
    "_daily_flow_confirmed_reopened_red_dot",
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
            "_cfg_get": lambda *args, **kwargs: "1000000001",
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

    def test_env_daily_counter_path_overrides_localappdata(self):
        namespace = load_functions("_daily_counters_default_path")
        with tempfile.TemporaryDirectory() as temp_dir:
            portable_path = os.path.join(temp_dir, "portable", "daily_counters.json")
            namespace["os"] = types.SimpleNamespace(
                environ={
                    "LOCALAPPDATA": os.path.join(temp_dir, "local"),
                    "QQFARM_DAILY_COUNTERS_PATH": portable_path,
                },
                path=os.path,
            )
            self.assertEqual(
                os.path.abspath(portable_path),
                namespace["_daily_counters_default_path"](),
            )

    def test_env_daily_status_path_is_the_only_runtime_write_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            portable_path = os.path.join(temp_dir, "portable", "daily_flow_status.json")
            namespace["os"].environ["QQFARM_DAILY_FLOW_STATUS_PATH"] = portable_path

            self.assertEqual(
                [os.path.abspath(portable_path)],
                namespace["_daily_flow_status_paths"](),
            )

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
                target = "1000000001" if flow == "share" else ""
                reason = (
                    "verified-direct-contact-send-v2" if flow == "share" else ""
                )
                self.assertTrue(namespace["_daily_flow_mark_status"](
                    flow, "success", target=target, reason=reason
                ))
            for flow in ("freebenefits", "task", "share", "svip"):
                target = "1000000001" if flow == "share" else ""
                self.assertTrue(namespace["_daily_flow_success_today"](
                    flow, target=target
                ))


    def test_concurrent_task_and_share_marks_preserve_both_flows(self):
        """Concurrent marks from one empty snapshot must merge, not clobber."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-04"
            original_read = namespace["_daily_flow_read_status"]
            original_write = namespace["_daily_flow_write_status"]
            both_reads = threading.Barrier(2)
            task_read_started = threading.Event()
            task_write_done = threading.Event()
            results = {}
            errors = []

            def synchronized_read(path):
                data = original_read(path)
                if threading.current_thread().name == "daily-task-mark":
                    task_read_started.set()
                try:
                    both_reads.wait(timeout=0.5)
                except threading.BrokenBarrierError:
                    pass
                return data

            def ordered_write(path, data):
                flow_keys = set((data.get("flows") or {}).keys())
                if flow_keys == {"share"}:
                    if not task_write_done.wait(timeout=2.0):
                        raise AssertionError("task status write did not complete first")
                written = original_write(path, data)
                if flow_keys == {"task"}:
                    task_write_done.set()
                return written

            namespace["_daily_flow_read_status"] = synchronized_read
            namespace["_daily_flow_write_status"] = ordered_write

            def mark(flow, reason):
                try:
                    results[flow] = namespace["_daily_flow_mark_status"](
                        flow,
                        "success",
                        target="1000000001" if flow == "share" else "",
                        reason=reason,
                        today=today,
                    )
                except BaseException as error:
                    errors.append((flow, error))

            task_thread = threading.Thread(
                target=mark,
                args=("task", "native-completion-date-transition"),
                name="daily-task-mark",
            )
            share_thread = threading.Thread(
                target=mark,
                args=("share", "verified-direct-contact-send-v2"),
                name="daily-share-mark",
            )
            task_thread.start()
            self.assertTrue(task_read_started.wait(timeout=1.0))
            share_thread.start()
            task_thread.join(timeout=3.0)
            share_thread.join(timeout=3.0)

            self.assertFalse(task_thread.is_alive())
            self.assertFalse(share_thread.is_alive())
            self.assertEqual([], errors)
            self.assertEqual({"task": True, "share": True}, results)
            persisted = original_read(
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual(
                {"task", "share"},
                set((persisted.get("flows") or {}).keys()),
            )


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



    def test_repair_clears_seeded_task_benefits_and_unverified_share(self):
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
                        "target": "1000000001",
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
            self.assertEqual("pending", status["flows"]["share"]["status"])
            counters = json.loads(counters_path.read_text(encoding="utf-8"))
            self.assertEqual("", counters["task_last_date"])
            self.assertEqual("", counters["freebenefits_last_date"])
            self.assertEqual("", counters["share_last_date"])
            self.assertEqual("", counters["instances"]["1"]["task_last_date"])
            self.assertEqual(
                "", counters["instances"]["1"]["freebenefits_last_date"]
            )
            self.assertEqual(
                "", counters["instances"]["1"]["share_last_date"]
            )


    def test_repair_reopens_reward_only_share_and_legacy_freebenefits_red_dot_success(self):
        import json

        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            status_path = Path(temp_dir) / "daily_flow_status.json"
            counters_path = Path(temp_dir) / "daily_counters.json"
            status_path.write_text(json.dumps({
                "date": today,
                "flows": {
                    "freebenefits": {
                        "date": today,
                        "status": "success",
                        "reason": "entry-red-dot-cleared",
                    },
                    "share": {
                        "date": today,
                        "status": "success",
                        "target": "1000000001",
                        "reason": "verified-share-reward-claimed-v1",
                    },
                    "share_reward": {
                        "date": today,
                        "status": "success",
                        "target": "1000000001",
                        "reason": "verified-share-reward-claimed-v2",
                    },
                },
            }), encoding="utf-8")
            counters_path.write_text(json.dumps({
                "freebenefits_last_date": today,
                "share_last_date": today,
                "instances": {
                    "1": {
                        "freebenefits_last_date": today,
                        "share_last_date": today,
                    }
                },
            }), encoding="utf-8")

            self.assertTrue(namespace["_daily_flow_repair_unverified_status"](
                paths=[str(status_path)],
                counter_paths=[str(counters_path)],
                today=today,
            ))

            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual("pending", status["flows"]["freebenefits"]["status"])
            self.assertEqual("pending", status["flows"]["share"]["status"])
            self.assertEqual("pending", status["flows"]["share_reward"]["status"])
            counters = json.loads(counters_path.read_text(encoding="utf-8"))
            self.assertEqual("", counters["freebenefits_last_date"])
            self.assertEqual("", counters["share_last_date"])
            self.assertEqual(
                "", counters["instances"]["1"]["freebenefits_last_date"]
            )
            self.assertEqual("", counters["instances"]["1"]["share_last_date"])


    def test_same_day_native_share_date_is_a_no_replay_latch_without_send_proof(self):
        """A native completion date blocks another share dispatch for the day.

        The durable status remains pending without exact-recipient proof, but
        the original sender must never be reopened automatically.  This is the
        behavior required by the July 29/31 duplicate-share logs.
        """
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
            self.assertFalse(namespace["_daily_flow_success_today"](
                "share", target="1000000001", today=today
            ))


    def test_pending_share_status_overrides_raw_native_date_latch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-03"
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt: today,
                time=time.time,
                monotonic=time.monotonic,
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "share", "pending", target="1000000001",
                reason="native-send-not-verified", today=today,
            ))
            bot = types.SimpleNamespace(
                share_last_date=today,
                daily_flow_retry_counts={"share": 0},
            )

            self.assertTrue(namespace["_daily_flow_unverified_today"](
                "share", today=today
            ))
            self.assertFalse(namespace["_daily_flow_context_success_today"](
                bot, "share", today=today
            ))
            self.assertEqual("", bot.share_last_date)

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

    def test_live_home_share_notification_dot_is_detected(self):
        import cv2
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        fixture = (
            ROOT / "tests" / "fixtures" /
            "live-home-share-task-badges-20260803.png"
        )
        frame = cv2.imdecode(
            np.fromfile(str(fixture), dtype=np.uint8), cv2.IMREAD_COLOR
        )

        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_daily_entry_red_dot_present"](
            frame, "share"
        ))

    def test_live_home_task_badge_is_detected(self):
        import cv2
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        fixture = (
            ROOT / "tests" / "fixtures" /
            "live-home-share-task-badges-20260803.png"
        )
        frame = cv2.imdecode(
            np.fromfile(str(fixture), dtype=np.uint8), cv2.IMREAD_COLOR
        )

        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_daily_entry_red_dot_present"](
            frame, "task"
        ))

    def test_live_home_shop_scenery_is_not_a_freebenefits_dot(self):
        import cv2
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        fixture = (
            ROOT / "tests" / "fixtures" /
            "live-home-share-task-badges-20260803.png"
        )
        frame = cv2.imdecode(
            np.fromfile(str(fixture), dtype=np.uint8), cv2.IMREAD_COLOR
        )

        self.assertIsNotNone(frame)
        self.assertFalse(namespace["_daily_entry_red_dot_present"](
            frame, "freebenefits"
        ))

    def test_freebenefits_red_dot_is_exposed_from_shop_entry_home_surface(self):
        """A visible shop-entry dot must reopen stale daily-benefit state.

        The free-benefits route begins from the home-screen shop entry.  A
        same-day success cache is not enough when that entry still visibly has
        a compact notification dot.
        """
        import numpy as np

        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            frame = np.full((800, 428, 3), 10, dtype=np.uint8)
            # Compact red dot beside the upper-right shop entry.
            frame[164:175, 388:399, 2] = 245
            bot = types.SimpleNamespace(_qqfarm_cycle_branch_hint="self")
            namespace["_get_frame_from_bot"] = lambda context: frame

            self.assertTrue(
                namespace["_daily_flow_entry_red_dot_state"](
                    bot, "freebenefits"
                )
            )


    def test_live_home_level_progress_digits_are_not_task_red_dot(self):
        """Red 122/123 progress digits must not keep the daily task pending."""
        import cv2
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        detect = namespace["_daily_entry_red_dot_present"]
        fixture = ROOT / "tests" / "fixtures" / "live-home-no-task-red-dot-20260802.png"
        frame = cv2.imdecode(
            np.fromfile(str(fixture), dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )

        self.assertIsNotNone(frame)
        self.assertFalse(detect(frame, "task"))

    def test_task_red_dot_rejects_wide_horizontal_red_strip(self):
        import numpy as np

        namespace = load_functions("_daily_entry_red_dot_present")
        detect = namespace["_daily_entry_red_dot_present"]
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[632:650, 13:100, 2] = 245

        self.assertFalse(detect(frame, "task"))

    def test_daily_task_retry_state_defaults_to_active_local_profile(self):
        namespace = load_functions("_daily_task_retry_state_default_path")
        resolve = namespace.get("_daily_task_retry_state_default_path")
        if resolve is None:
            self.fail("_daily_task_retry_state_default_path is missing")
        namespace["os"] = types.SimpleNamespace(
            environ={"LOCALAPPDATA": r"E:\ActiveProfile"},
            path=os.path,
        )

        self.assertEqual(
            os.path.join(
                r"E:\ActiveProfile", "qq-farm-bot-rev",
                "daily_task_retry_state.json",
            ),
            resolve(),
        )
    def test_daily_task_soft_retry_from_previous_business_day_is_cleared(self):
        """A 2026-08-03 soft retry must not block the 2026-08-04 task."""
        from datetime import datetime, timedelta, timezone

        namespace = load_functions(
            "_daily_task_zero_retry_state",
            "_daily_task_load_retry_state",
            "_daily_task_write_retry_state",
            "_daily_task_retry_backoff_active",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            retry_path = Path(temp_dir) / "daily_task_retry_state.json"
            china_tz = timezone(timedelta(hours=8))
            failed_at = datetime(2026, 8, 3, 23, 59, tzinfo=china_tz).timestamp()
            checked_at = datetime(2026, 8, 4, 0, 1, tzinfo=china_tz).timestamp()
            retry_path.write_text(
                json.dumps({
                    "date": "2026-08-03",
                    "last_fail_ts": failed_at,
                    "next_ts": checked_at + 180.0,
                    "reason": "task-prompt-missing",
                }),
                encoding="utf-8",
            )

            def localtime_at(epoch=None):
                value = checked_at if epoch is None else float(epoch)
                return datetime.fromtimestamp(value, china_tz).timetuple()

            def strftime_at(fmt, value=None):
                return time.strftime(
                    fmt,
                    localtime_at() if value is None else value,
                )

            namespace.update({
                "os": os,
                "time": types.SimpleNamespace(
                    time=lambda: checked_at,
                    localtime=localtime_at,
                    strftime=strftime_at,
                ),
                "_DAILY_TASK_RETRY_STATE_PATH": str(retry_path),
                "_throttled_write": lambda *args, **kwargs: None,
            })

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                retry_is_active = namespace["_daily_task_retry_backoff_active"]()
            self.assertFalse(
                retry_is_active,
                "a previous business day's soft retry still blocks 2026-08-04",
            )
            cleared = json.loads(retry_path.read_text(encoding="utf-8"))
            self.assertEqual(0.0, float(cleared.get("next_ts", -1.0)))
            self.assertEqual(0.0, float(cleared.get("last_fail_ts", -1.0)))


    def test_restart_repair_preserves_exhausted_task_retry_count(self):
        """A same-day 3/3 task failure is an exhaustion record, not corrupt data.

        Regression from 2026-07-29: the startup repair rewrote task=3 to 0
        whenever task_last_date was empty, so a restart immediately reopened
        the same failed daily task.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            namespace["_DAILY_RETRY_REPAIR_LAST_TS"] = 0.0
            counters_path = Path(temp_dir) / "daily_counters.json"
            counters_path.write_text(
                json.dumps({
                    "task_last_date": "",
                    "daily_flow_retry_counts": {"task": 3},
                }),
                encoding="utf-8",
            )

            self.assertFalse(
                namespace["_repair_daily_task_retry_state_file"](
                    "fixture-restart", path=str(counters_path), max_retry=3
                )
            )
            repaired = json.loads(counters_path.read_text(encoding="utf-8"))
            self.assertEqual(3, repaired["daily_flow_retry_counts"]["task"])

    def test_retry_repair_closes_counter_file_handles(self):
        """Startup repair must not leak the counters file on a capped write."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            namespace["_DAILY_RETRY_REPAIR_LAST_TS"] = 0.0
            counters_path = Path(temp_dir) / "daily_counters.json"
            counters_path.write_text(
                json.dumps({
                    "task_last_date": "",
                    "daily_flow_retry_counts": {"task": 4},
                }),
                encoding="utf-8",
            )

            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always", ResourceWarning)
                self.assertTrue(
                    namespace["_repair_daily_task_retry_state_file"](
                        "fixture-repair", path=str(counters_path), max_retry=3
                    )
                )
                gc.collect()

            self.assertEqual(
                [],
                [
                    warning for warning in captured
                    if issubclass(warning.category, ResourceWarning)
                ],
            )

    def test_exhausted_task_retry_blocks_for_the_rest_of_its_day(self):
        """A 3/3 durable failure must remain blocked after its delay expires."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-07-29"
            status_path = namespace["_daily_flow_status_paths"]()[0]
            self.assertTrue(namespace["_daily_flow_write_status"](
                status_path,
                {
                    "date": today,
                    "flows": {
                        "task": {
                            "date": today,
                            "status": "failed",
                            "attempts": 3,
                            "next_retry_at": 0.0,
                            "reason": "task-prompt-missing",
                        },
                    },
                },
            ))

            self.assertTrue(namespace["_daily_flow_retry_blocked"](
                "task", today=today, now_epoch=86400.0
            ))
            self.assertFalse(namespace["_daily_flow_retry_blocked"](
                "task", today="2026-07-30", now_epoch=86400.0
            ))

    def test_runtime_task_prompt_miss_marks_flow_failed_and_keeps_retry_state(self):
        namespace = load_functions("_note_runtime_daily_task_outcome")
        note = namespace.get("_note_runtime_daily_task_outcome")
        if note is None:
            self.fail("_note_runtime_daily_task_outcome is missing")
        events = []
        bot = types.SimpleNamespace(
            task_last_date="",
            daily_flow_retry_counts={"task": 1},
        )
        namespace.update({
            "_DAILY_TASK_PROMPT_MISS_LAST_TS": 0.0,
            "_ACTIVE_RUN_CYCLE_CONTEXT": bot,
            "_daily_flow_mark_failure": (
                lambda flow, reason="", **kwargs:
                events.append(("failure", flow, reason)) or True
            ),
            "_daily_flow_mark_status": (
                lambda flow, status, reason="", **kwargs:
                events.append(("unexpected-status", flow, status, reason)) or True
            ),
            "_daily_flow_apply_success_context": (
                lambda context, flow:
                events.append(("unexpected-context", context, flow)) or True
            ),
            "_daily_task_clear_retry_backoff": (
                lambda: events.append(("unexpected-clear-backoff",)) or True
            ),
            "_throttled_write": lambda *args, **kwargs: None,
        })

        first = note(
            "\u00d7\u672a\u68c0\u6d4b\u5230 task_prompt\uff0c\u672c\u6b21\u6bcf\u65e5\u4efb\u52a1\u672a\u9886\u53d6", now=100.0
        )
        duplicate = note(
            "\u6bcf\u65e5\u4efb\u52a1\u9886\u53d6\u5931\u8d25\uff1a\u5df2\u70b9\u51fb\u5173\u95ed\u6309\u94ae\u6536\u655b\u6bcf\u65e5\u5f39\u7a97", now=101.0
        )

        self.assertEqual("task-prompt-missing-failed", first)
        self.assertEqual("task-prompt-missing-duplicate", duplicate)
        self.assertEqual(
            [("failure", "task", "task-prompt-missing")],
            [item for item in events if item[0] == "failure"],
        )
        self.assertEqual([], [item for item in events if item[0] == "unexpected-status"])
        self.assertEqual([], [item for item in events if item[0] == "unexpected-context"])
        self.assertEqual([], [item for item in events if item[0] == "unexpected-clear-backoff"])

    def test_legacy_task_no_prompt_success_is_invalidated_by_entry_red_dot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-07-28"
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt: today,
                time=time.time,
            )
            bot = types.SimpleNamespace(
                task_last_date=today,
                daily_flow_retry_counts={"task": 0},
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task", "success", reason="entry-no-prompt-assumed-cleared", today=today
            ))

            self.assertTrue(namespace["_daily_flow_invalidate_success"](
                bot, "task", reason="entry-red-dot-still-present"
            ))

            self.assertEqual("", bot.task_last_date)
            self.assertFalse(namespace["_daily_task_authoritative_success_today"](
                today=today
            ))
            self.assertFalse(namespace["_daily_flow_success_today"](
                "task", today=today
            ))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("pending", status["flows"]["task"]["status"])
            self.assertEqual(
                "entry-red-dot-still-present",
                status["flows"]["task"]["reason"],
            )


    def test_verified_native_task_success_hard_gates_a_stale_red_dot(self):
        """A completed native claim must not be reopened by the next stale frame."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                task_last_date=today,
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task",
                "success",
                reason="native-completion-date-transition",
                today=today,
            ))
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "task" else None
            )
            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )

            self.assertFalse(module.should_run_daily_task(bot))
            self.assertNotIn(("should-task",), events)
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("success", status["flows"]["task"]["status"])
            self.assertEqual(
                "native-completion-date-transition",
                status["flows"]["task"]["reason"],
            )

    def test_persistent_home_task_badge_does_not_reopen_verified_native_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = "2026-08-03"
            clock = [100.0]
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt: today,
                time=time.time,
                monotonic=lambda: clock[0],
            )
            bot = types.SimpleNamespace(
                task_last_date=today,
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task", "success",
                reason="native-completion-date-transition", today=today,
            ))
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "task" else None
            )
            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )

            self.assertFalse(module.should_run_daily_task(bot))
            self.assertNotIn(("should-task",), events)
            clock[0] = 103.0
            self.assertFalse(module.should_run_daily_task(bot))

            self.assertEqual(0, events.count(("should-task",)))
            self.assertEqual(today, bot.task_last_date)
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("success", status["flows"]["task"]["status"])
            self.assertEqual(
                "native-completion-date-transition",
                status["flows"]["task"]["reason"],
            )

    def test_native_task_success_log_recovers_pending_status_after_late_prompt_misses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-02"
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt: today,
                time=time.time,
            )
            status_path = namespace["_daily_flow_status_paths"]()[0]
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task",
                "pending",
                reason="entry-red-dot-still-present",
                today=today,
            ))
            native_log = Path(temp_dir) / "logs" / (today + ".log")
            native_log.parent.mkdir(parents=True, exist_ok=True)
            native_log.write_text(
                "2026-08-02 00:56:20.817 [INFO] "
                "\u6bcf\u65e5\u4efb\u52a1\u9886\u53d6\u6267\u884c\u5b8c\u6210\uff0c"
                "\u8bb0\u5f55\u65e5\u671f\uff1a2026-08-02\n"
                "2026-08-02 01:45:20.215 [WARNING] "
                "\u00d7\u672a\u68c0\u6d4b\u5230 task_prompt\uff0c"
                "\u672c\u6b21\u6bcf\u65e5\u4efb\u52a1\u672a\u9886\u53d6\n",
                encoding="utf-8",
            )
            namespace["os"].environ["QQFARM_DAILY_TASK_LOG_PATH"] = str(native_log)

            self.assertTrue(namespace["_daily_task_authoritative_success_today"](
                paths=[status_path], today=today
            ))
            status = namespace["_daily_flow_read_status"](status_path)
            self.assertEqual("success", status["flows"]["task"]["status"])
            self.assertEqual(
                "verified-native-task-log-v1",
                status["flows"]["task"]["reason"],
            )


    def test_confirmed_reopened_task_badge_blocks_older_native_log_recovery(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-03"
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt: today,
                time=time.time,
                monotonic=time.monotonic,
            )
            status_path = namespace["_daily_flow_status_paths"]()[0]
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task", "pending",
                reason="entry-red-dot-confirmed-persistent", today=today,
            ))
            native_log = Path(temp_dir) / "logs" / (today + ".log")
            native_log.parent.mkdir(parents=True, exist_ok=True)
            native_log.write_text(
                "2026-08-03 00:57:33.897 [INFO] "
                "每日任务领取执行完成，记录日期：2026-08-03\n",
                encoding="utf-8",
            )
            namespace["os"].environ["QQFARM_DAILY_TASK_LOG_PATH"] = str(
                native_log
            )

            self.assertFalse(
                namespace["_daily_task_authoritative_success_today"](
                    paths=[status_path], today=today
                )
            )
            status = namespace["_daily_flow_read_status"](status_path)
            self.assertEqual("pending", status["flows"]["task"]["status"])
            self.assertEqual(
                "entry-red-dot-confirmed-persistent",
                status["flows"]["task"]["reason"],
            )

    def test_loaded_daily_patch_reconciles_native_task_log_before_scheduler_gate(self):
        namespace = load_functions("_patch_daily_flow_status_loaded")
        events = []
        namespace.update({
            "sys": types.SimpleNamespace(modules={}),
            "_patch_daily_flow_status_for_module": (
                lambda module, tag="": events.append(("module", module, tag)) or 0
            ),
            "_daily_task_authoritative_success_today": (
                lambda: events.append(("task-log-reconciled",)) or True
            ),
        })

        self.assertEqual([], namespace["_patch_daily_flow_status_loaded"]("startup"))
        self.assertEqual([("task-log-reconciled",)], events)


    def test_runtime_logger_routes_task_outcomes_to_backoff_helper(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertGreaterEqual(
            source.count("_note_runtime_daily_task_outcome(msg)"), 2
        )
    def test_share_red_dot_does_not_reopen_native_completion_latch(self):
        """A stale red dot is never permission to send today's share again."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date=today,
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "share" else None
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertFalse(module.should_run_daily_share(bot))
            self.assertEqual(today, bot.share_last_date)
            self.assertNotIn(("should-share",), events)

    def test_cleared_share_red_dot_keeps_flow_due_without_send_proof(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "share" else None
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.should_run_daily_share(bot))
            self.assertEqual("", bot.share_last_date)
            self.assertFalse(namespace["_daily_flow_success_today"](
                "share", target="1000000001"
            ))
            self.assertIn(("should-share",), events)

    def test_unverified_share_success_write_is_downgraded_to_pending(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = time.strftime("%Y-%m-%d")
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "share", "success", target="1000000001",
                reason="entry-red-dot-cleared", today=today,
            ))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("pending", status["flows"]["share"]["status"])
            self.assertEqual(
                "share-success-requires-v2-proof",
                status["flows"]["share"]["reason"],
            )

    def test_fresh_cleared_red_dot_keeps_task_due_until_a_real_attempt(self):
        """No badge before the first attempt is not proof that today's task ran."""
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

            self.assertTrue(module.should_run_daily_task(bot))
            self.assertEqual("", bot.task_last_date)
            self.assertFalse(namespace["_daily_flow_success_today"]("task"))
            self.assertIn(("should-task",), events)




    def test_non_authoritative_task_success_reopens_native_check_from_home(self):
        """Task completion without native claim proof remains due even on home."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-04"
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date=today,
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
                _qqfarm_daily_flow_attempt_day_task=today,
            )
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt, *args: today,
                time=time.time,
                localtime=time.localtime,
                monotonic=time.monotonic,
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task", "success", today=today,
                reason="entry-red-dot-cleared",
            ))
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "task" else None
            )
            namespace["_daily_task_claim_available_visible"] = (
                lambda context: events.append(("task-claim-visible",)) or False
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.should_run_daily_task(bot))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("pending", status["flows"]["task"]["status"])
            self.assertEqual(
                "task-success-requires-claim-proof",
                status["flows"]["task"]["reason"],
            )
            self.assertEqual("", bot.task_last_date)
            self.assertIn(("should-task",), events)

    def test_visible_task_claim_reopens_non_authoritative_red_dot_success_after_restart(self):
        """A stale entry-red-dot-cleared record cannot hide a real task claim."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-04"
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date=today,
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
                _qqfarm_daily_flow_attempt_day_task=today,
            )
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt, *args: today,
                time=time.time,
                localtime=time.localtime,
                monotonic=time.monotonic,
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "task", "success", today=today,
                reason="entry-red-dot-cleared",
            ))
            self.assertFalse(namespace[
                "_daily_task_authoritative_success_today"
            ](today=today))
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "task" else None
            )
            namespace["_daily_task_claim_available_visible"] = (
                lambda context: events.append(("task-claim-visible",)) or True
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.should_run_daily_task(bot))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual("pending", status["flows"]["task"]["status"])
            self.assertEqual(
                "task-claim-still-visible",
                status["flows"]["task"]["reason"],
            )
            self.assertEqual("", bot.task_last_date)
            self.assertIn(("task-claim-visible",), events)
            self.assertIn(("should-task",), events)

    def test_task_red_dot_clear_does_not_complete_while_claim_button_is_visible(self):
        """A cleared home badge cannot outrank a claim button still on the task page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            today = "2026-08-04"
            events = []
            marks = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
                _qqfarm_daily_flow_attempt_day_task=today,
            )
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt, *args: today,
                time=time.time,
                localtime=time.localtime,
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "task" else None
            )
            namespace["_daily_task_claim_available_visible"] = (
                lambda context: events.append(("task-claim-visible",)) or True
            )
            namespace["_daily_flow_mark_status"] = (
                lambda flow, status, target="", reason="", **kwargs:
                marks.append((flow, status, reason)) or True
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            should_run = module.should_run_daily_task(bot)

            self.assertEqual([], marks)
            self.assertTrue(should_run)
            self.assertIn(("task-claim-visible",), events)
            self.assertEqual("", bot.task_last_date)


    def test_cleared_task_red_dot_stays_due_without_native_claim_proof(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            bot = types.SimpleNamespace(
                task_last_date="",
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 1, "svip": 0, "share": 0,
                },
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: False if flow == "task" else None
            )
            namespace["_daily_flow_retry_blocked"] = (
                lambda flow: flow == "task"
            )
            patch = namespace["_patch_daily_flow_status_for_module"]
            self.assertGreater(patch(module), 0)

            self.assertTrue(module.should_run_daily_task(bot))
            self.assertIn(("should-task",), events)
            self.assertEqual("", bot.task_last_date)
            self.assertFalse(namespace["_daily_flow_success_today"]("task"))
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
                "share", "success", target="1000000001", today=today
            ))
            namespace["_share_direct_success_recent"] = (
                lambda target="", max_age=15.0:
                target == "1000000001" and max_age >= 86400.0
            )

            self.assertTrue(namespace["_daily_flow_invalidate_success"](
                bot, "share", reason="entry-red-dot-still-present"
            ))

            self.assertEqual(today, bot.share_last_date)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "share", target="1000000001", today=today
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


    def test_verified_share_blocks_scheduler_before_red_dot_can_reopen_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")
            bot = types.SimpleNamespace(
                share_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "share", "success", target="1000000001", today=today,
                reason="verified-direct-contact-send-v2",
            ))
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "share" else None
            )

            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            self.assertFalse(module.should_run_daily_share(bot))
            self.assertNotIn(("should-share",), events)
            self.assertEqual(today, bot.share_last_date)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "share", target="1000000001", today=today
            ))


    def test_native_freebenefits_completion_date_promotes_durable_success(self):
        """A native completed-benefits run must become a durable one-day lock.

        July 29/31 logs showed `freebenefits_last_date` being written by the
        native flow, while the durable JSON status remained failed.  The next
        polling round consequently reopened the same daily UI.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")

            def run_freebenefits(bot):
                events.append(("run-freebenefits",))
                bot._qqfarm_freebenefits_claim_verified_day = today
                bot.freebenefits_last_date = today
                return True

            module.should_run_daily_freebenefits = (
                lambda bot: events.append(("should-freebenefits",)) or True
            )
            module.run_daily_freebenefits = run_freebenefits
            bot = types.SimpleNamespace(
                freebenefits_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )

            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            self.assertTrue(module.run_daily_freebenefits(bot))
            self.assertTrue(namespace["_daily_flow_success_today"](
                "freebenefits", today=today
            ))
            status = namespace["_daily_flow_read_status"](
                namespace["_daily_flow_status_paths"]()[0]
            )
            self.assertEqual(
                "success", status["flows"]["freebenefits"]["status"]
            )

            self.assertFalse(module.should_run_daily_freebenefits(bot))
            self.assertEqual([("run-freebenefits",)], events)
            self.assertFalse(module._mark_daily_flow_failure(bot, "freebenefits"))
            self.assertEqual(0, bot.daily_flow_retry_counts["freebenefits"])
            self.assertEqual(
                "success",
                namespace["_daily_flow_read_status"](
                    namespace["_daily_flow_status_paths"]()[0]
                )["flows"]["freebenefits"]["status"],
            )

    def test_freebenefits_success_hard_gates_persistent_marketplace_red_dot(self):
        """A same-day benefit success must not re-run merely because the shop dot stays visible."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")

            module.should_run_daily_freebenefits = (
                lambda bot: events.append(("should-freebenefits",)) or True
            )
            module.run_daily_freebenefits = (
                lambda bot: events.append(("run-freebenefits",)) or True
            )
            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "freebenefits" else None
            )

            first_bot = types.SimpleNamespace(
                freebenefits_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "freebenefits", "success", today=today,
                reason="verified-freebenefits-claim-v2",
            ))
            self.assertFalse(module.should_run_daily_freebenefits(first_bot))
            self.assertEqual([], events)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "freebenefits", today=today
            ))

            second_bot = types.SimpleNamespace(
                freebenefits_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(module.run_daily_freebenefits(second_bot))
            self.assertEqual([], events)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "freebenefits", today=today
            ))
    def test_native_task_completion_date_promotes_durable_success(self):
        """Native task completion must survive a later scheduler poll/reload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")

            def run_task(bot):
                events.append(("run-task-native-date",))
                bot.task_last_date = today
                return True

            module.should_run_daily_task = (
                lambda bot: events.append(("should-task-native-date",)) or True
            )
            module.run_daily_task = run_task
            bot = types.SimpleNamespace(
                task_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )

            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            self.assertTrue(module.run_daily_task(bot))
            self.assertTrue(namespace["_daily_flow_success_today"](
                "task", today=today
            ))
            self.assertFalse(module.should_run_daily_task(bot))
            self.assertEqual([("run-task-native-date",)], events)


    def test_native_completion_repromotes_after_stale_context_date_is_cleared(self):
        """A native re-run after cache cleanup must still promote its new date.

        This is the exact July 31 contradiction: the counter cache already said
        today, durable state said failed, and the wrapper cleared that cache
        before the native flow completed again.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            today = time.strftime("%Y-%m-%d")

            def run_freebenefits(bot):
                events.append(("run-after-cache-clear", bot.freebenefits_last_date))
                bot._qqfarm_freebenefits_claim_verified_day = today
                bot.freebenefits_last_date = today
                return True

            module.run_daily_freebenefits = run_freebenefits
            bot = types.SimpleNamespace(
                freebenefits_last_date=today,
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )

            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            self.assertTrue(module.run_daily_freebenefits(bot))
            self.assertEqual([("run-after-cache-clear", "")], events)
            self.assertTrue(namespace["_daily_flow_success_today"](
                "freebenefits", today=today
            ))


    def test_future_durable_success_does_not_block_current_day_red_dot_flow(self):
        """A future-dated state may not suppress today's visible daily benefit.

        Calendar-day de-duplication is intentionally exact.  Treating an
        August 1 status as a July 31 success made the scheduler skip a visible
        benefit on the actual current day and hid the resulting date drift.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            namespace = self.build_namespace(temp_dir)
            events = []
            module = self.build_module(events)
            host_day = "2026-07-31"
            future_day = "2026-08-01"

            module.should_run_daily_freebenefits = (
                lambda bot: events.append(("should-freebenefits",)) or True
            )
            module.run_daily_freebenefits = (
                lambda bot: events.append(("run-freebenefits",)) or True
            )
            self.assertTrue(namespace["_daily_flow_mark_status"](
                "freebenefits", "success", today=future_day,
                reason="native-completion-date-transition",
            ))

            self.assertFalse(namespace["_daily_flow_success_today"](
                "freebenefits", today=host_day
            ))

            real_time = namespace["time"]
            namespace["time"] = types.SimpleNamespace(
                strftime=lambda fmt, *args: host_day if fmt == "%Y-%m-%d" else real_time.strftime(fmt, *args),
                time=real_time.time,
                localtime=real_time.localtime,
            )
            namespace["_daily_flow_entry_red_dot_state"] = (
                lambda context, flow: True if flow == "freebenefits" else None
            )
            self.assertGreater(
                namespace["_patch_daily_flow_status_for_module"](module), 0
            )
            bot = types.SimpleNamespace(
                freebenefits_last_date="",
                daily_flow_retry_counts={
                    "freebenefits": 0, "task": 0, "svip": 0, "share": 0,
                },
            )
            self.assertTrue(module.should_run_daily_freebenefits(bot))
            self.assertTrue(module.run_daily_freebenefits(bot))
            self.assertEqual(
                [("should-freebenefits",), ("run-freebenefits",)], events
            )



if __name__ == "__main__":
    unittest.main()
