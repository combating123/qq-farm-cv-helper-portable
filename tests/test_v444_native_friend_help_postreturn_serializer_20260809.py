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
    namespace = {"__file__": str(HOOK), "__name__": "v444_postreturn_test"}
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
    path.write_text(json.dumps(payload), encoding="utf-8")


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


class NativeFriendHelpPostreturnSerializer20260809Tests(unittest.TestCase):
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
        self.assertEqual(
            expected,
            context._instance_metrics["1"]["friend_farming_count"],
        )
        self.assertEqual(expected, context.gui_metrics["friend_farming_count"])
        self.assertEqual(
            expected,
            context._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"],
        )
        for path in paths:
            self.assertEqual((expected,) * 5, read_counter(path), path)
        for path in csv_paths:
            self.assertEqual(expected, read_csv_help(path, day), path)

    def test_process_return_repairs_native_post_record_serializer_stale_gui(self):
        """A native Local-primary write after the recorder returns cannot survive to the next cycle."""
        day = "2026-08-09"
        baseline = 30
        cache_wrapper = self.namespace["_wrap_native_v225_friend_help_candidate_cache"]
        recorder_wrapper = self.namespace["_wrap_native_v225_friend_help_confirmation"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            local = root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            legacy = portable_root / "UserData" / "legacy-qq-farm-bot-rev" / "daily_counters.json"
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = root / "roaming" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            portable_csv = portable_root / "UserData" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            for path in paths:
                write_counter(path, day=day, count=baseline)
            write_csv_help(profile_csv, day=day, count=baseline)
            write_csv_help(portable_csv, day=day, count=baseline)
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: None,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
                "_friend_help_visual_completion_proof": lambda *_args, **_kwargs: False,
            })

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
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._record_friend_help_action()
                    # This is the live v443 gap: a native Local-primary serializer
                    # runs after the wrapped recorder has already returned. It keeps
                    # the durable count at B but reuses stale GUI buckets B+2 and B-10.
                    self._instance_metrics["1"]["friend_farming_count"] = baseline + 2
                    self.gui_metrics["friend_farming_count"] = baseline + 2
                    self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"] = baseline - 10
                    write_counter(
                        local,
                        day=day,
                        count=self.friend_help_daily_count,
                        gui_count=self.gui_metrics["friend_farming_count"],
                        global_gui_count=self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"],
                    )
                    return "native-serialized"

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
                self.assertEqual("native-serialized", context.process_friend_farm())

            self._assert_surfaces(
                context,
                paths,
                (portable_csv, profile_csv),
                day,
                baseline,
            )

    def test_process_return_preserves_confirmed_increment_after_stale_serializer(self):
        """A confirmed B -> B+1 remains B+1 when native serializes stale GUI after return."""
        day = "2026-08-09"
        baseline = 40
        expected = baseline + 1
        cache_wrapper = self.namespace["_wrap_native_v225_friend_help_candidate_cache"]
        recorder_wrapper = self.namespace["_wrap_native_v225_friend_help_confirmation"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            local = root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            legacy = portable_root / "UserData" / "legacy-qq-farm-bot-rev" / "daily_counters.json"
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = root / "roaming" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            portable_csv = portable_root / "UserData" / "QQFarmCopilot" / "instances" / "default" / "stats" / "daily_action_stats.csv"
            for path in paths:
                write_counter(path, day=day, count=baseline)
            write_csv_help(profile_csv, day=day, count=baseline)
            write_csv_help(portable_csv, day=day, count=baseline)
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
                    # Model native runtime's early exact B+1 write.  The bridge
                    # must recognize it as this one confirmed transaction rather
                    # than fabricate another increment.
                    self.friend_help_daily_count = expected
                    self._instance_metrics["1"]["friend_farming_count"] = expected
                    self.gui_metrics["friend_farming_count"] = expected
                    self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"] = expected
                    write_counter(local, day=day, count=expected)
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._record_friend_help_action()
                    # The native Local-primary serializer runs after the wrapped
                    # recorder.  Its root/instance count remains B+1, but its
                    # stale GUI buckets would otherwise survive until next cycle.
                    self._instance_metrics["1"]["friend_farming_count"] = expected + 2
                    self.gui_metrics["friend_farming_count"] = expected + 2
                    self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"] = expected - 10
                    write_counter(
                        local,
                        day=day,
                        count=self.friend_help_daily_count,
                        gui_count=self.gui_metrics["friend_farming_count"],
                        global_gui_count=self._instance_metrics["__global__"]["gui_metrics"]["friend_farming_count"],
                    )
                    return "native-serialized"

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
                self.assertEqual("native-serialized", context.process_friend_farm())

            self._assert_surfaces(
                context,
                paths,
                (portable_csv, profile_csv),
                day,
                expected,
            )


if __name__ == "__main__":
    unittest.main()
