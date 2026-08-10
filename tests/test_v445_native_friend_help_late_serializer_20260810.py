import ast
import csv
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


FUNCTIONS = (
    "_daily_metrics_sync_runtime",
    "_qqfarm_native_friend_help_durable_snapshot",
    "_qqfarm_commit_native_friend_help_confirmation",
    "_qqfarm_cache_native_v225_friend_help_candidate",
    "_wrap_native_v225_friend_help_candidate_cache",
    "_wrap_native_v225_friend_help_confirmation",
)
OPTIONAL_FUNCTIONS = ("_qqfarm_native_friend_help_quorum_baseline",)


def load_functions(*names):
    tree = ast.parse(HOOK.read_text(encoding="utf-8-sig"), filename=str(HOOK))
    wanted = set(names)
    optional = set(OPTIONAL_FUNCTIONS)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in (wanted | optional)
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v445_late_serializer_test"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def write_counter(path, *, day, count, gui_count=None, global_gui_count=None):
    gui_count = count if gui_count is None else gui_count
    global_gui_count = gui_count if global_gui_count is None else global_gui_count
    payload = {
        "friend_help_daily_count": count,
        "friend_help_daily_date": day,
        "gui_metrics": {"date": day, "friend_farming_count": gui_count},
        "instances": {
            "__global__": {
                "gui_metrics": {
                    "date": day,
                    "friend_farming_count": global_gui_count,
                },
            },
            "1": {
                "friend_help_daily_count": count,
                "friend_help_daily_date": day,
                "gui_metrics": {"date": day, "friend_farming_count": gui_count},
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")


def read_counter(path):
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    instance = payload["instances"]["1"]
    global_metrics = payload["instances"]["__global__"]["gui_metrics"]
    return (
        int(payload["friend_help_daily_count"]),
        int(instance["friend_help_daily_count"]),
        int(payload["gui_metrics"]["friend_farming_count"]),
        int(instance["gui_metrics"]["friend_farming_count"]),
        int(global_metrics["friend_farming_count"]),
    )


def write_csv_help(path, *, day, count):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("date", "harvest", "operation", "friend_steal", "friend_help"),
        )
        writer.writeheader()
        writer.writerow({
            "date": day,
            "harvest": 0,
            "operation": 0,
            "friend_steal": 0,
            "friend_help": count,
        })


def read_csv_help(path, day):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item for item in rows if item["date"] == day)
    return int(row["friend_help"])


class NativeFriendHelpLateSerializer20260810Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(*FUNCTIONS)
        self.namespace.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_DAILY_METRICS_LAST_SYNC_DAY": "",
            "_DAILY_METRICS_REPAIR_PENDING": False,
            "_write": lambda _message: None,
        })

    def _assert_surfaces(self, context, paths, csv_paths, day, expected):
        self.assertEqual(expected, context.friend_help_daily_count)
        self.assertEqual(expected, context._instance_metrics["1"]["friend_farming_count"])
        self.assertEqual(expected, context.gui_metrics["friend_farming_count"])
        self.assertEqual(
            expected,
            context._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"],
        )
        for path in paths:
            self.assertEqual((expected,) * 5, read_counter(path), path)
        for path in csv_paths:
            self.assertEqual(expected, read_csv_help(path, day), path)

    def test_late_native_local_serializer_is_reconciled_after_process_return(self):
        """A serializer queued by native process_friend_farm cannot leave Local-primary stale."""
        day = "2026-08-10"
        baseline = 41
        expected = baseline + 1
        cache_wrapper = self.namespace["_wrap_native_v225_friend_help_candidate_cache"]
        recorder_wrapper = self.namespace["_wrap_native_v225_friend_help_confirmation"]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            portable_root = root / "portable-root"
            local = root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            roaming = root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            paths = (
                local,
                local.with_name("daily_counters.hook.json"),
                roaming,
                roaming.with_name("daily_counters.hook.json"),
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            portable_csv = portable_root / "UserData" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            roaming_csv = root / "roaming" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            write_csv_help(portable_csv, day=day, count=baseline)
            write_csv_help(roaming_csv, day=day, count=baseline)

            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None
            frames = iter(("before-frame", "after-frame"))
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: next(frames),
                "_friend_guard_help_button_match": lambda frame: {
                    "matched": frame == "before-frame",
                },
                "_qqfarm_native_friend_help_card_signature": lambda _frame: (
                    "selected-carousel-v1", "same-card",
                ),
                "_friend_help_visual_completion_proof": lambda *_args, **_kwargs: True,
            })

            late_native_callbacks = []
            deferred_reconcile_contexts = []
            self.namespace[
                "_qqfarm_schedule_native_friend_help_postreturn_reconcile"
            ] = lambda context: deferred_reconcile_contexts.append(context) or 1

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": baseline},
                        "__global__": {
                            "gui_metrics": {
                                "date": day,
                                "friend_farming_count": baseline,
                            },
                        },
                    }
                    self.gui_metrics = {
                        "date": day,
                        "friend_farming_count": baseline,
                    }

                def _record_friend_help_action(self):
                    self.friend_help_daily_count = expected
                    self._instance_metrics["1"]["friend_farming_count"] = expected
                    self.gui_metrics["friend_farming_count"] = expected
                    self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"] = expected
                    write_counter(local, day=day, count=expected)
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._record_friend_help_action()

                    def native_late_serializer():
                        self._instance_metrics["1"]["friend_farming_count"] = expected + 4
                        self.gui_metrics["friend_farming_count"] = expected + 4
                        self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"] = 0
                        write_counter(
                            local,
                            day=day,
                            count=expected,
                            gui_count=expected + 4,
                            global_gui_count=0,
                        )

                    late_native_callbacks.append(native_late_serializer)
                    return "native-returned"

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm,
                "FarmBotCV.process_friend_farm",
            )
            FarmBotCV._record_friend_help_action, bridged = recorder_wrapper(
                FarmBotCV._record_friend_help_action,
                "FarmBotCV._record_friend_help_action",
            )
            self.assertTrue(cached)
            self.assertTrue(bridged)

            with mock.patch.dict(
                os.environ,
                {
                    "QQFARM_DAILY_COUNTERS_PATH": str(roaming),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                context = FarmBotCV()
                self.assertEqual("native-returned", context.process_friend_farm())
                for callback in late_native_callbacks:
                    callback()
                for scheduled_context in deferred_reconcile_contexts:
                    quorum = self.namespace[
                        "_qqfarm_native_friend_help_quorum_baseline"
                    ](scheduled_context)
                    self.assertEqual(expected, quorum)
                    self.namespace[
                        "_qqfarm_commit_native_friend_help_confirmation"
                    ](
                        scheduled_context,
                        confirmed=False,
                        durable_before=quorum,
                    )

            self._assert_surfaces(
                context,
                paths,
                (portable_csv, roaming_csv),
                day,
                expected,
            )


    def test_deferred_scheduler_queues_two_bounded_reconciliations(self):
        """The production deferred repair stays on the UI loop and never increments."""
        helper_name = "_qqfarm_schedule_native_friend_help_postreturn_reconcile"
        namespace = load_functions(*FUNCTIONS, helper_name)
        queued = []
        commits = []
        namespace.update({
            "_write": lambda _message: None,
            "_qqfarm_native_friend_help_deferred_schedule": (
                lambda delay_ms, callback: queued.append((delay_ms, callback)) or 1
            ),
            "_qqfarm_native_friend_help_quorum_baseline": lambda _context: 55,
            "_qqfarm_commit_native_friend_help_confirmation": (
                lambda _context, confirmed=False, durable_before=None: commits.append(
                    (bool(confirmed), int(durable_before))
                ) or int(durable_before)
            ),
        })
        context = types.SimpleNamespace()

        self.assertEqual(2, namespace[helper_name](context))
        self.assertEqual([60, 260], [delay for delay, _callback in queued])
        for _delay, callback in queued:
            callback()
        self.assertEqual([(False, 55), (False, 55)], commits)


if __name__ == "__main__":
    unittest.main()
