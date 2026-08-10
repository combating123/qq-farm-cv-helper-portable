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

# Loaded when it exists so the RED test can first demonstrate the missing
# preflight behavior without making the test loader itself the only failure.
OPTIONAL_FUNCTIONS = (
    "_qqfarm_native_friend_help_quorum_baseline",
)


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
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
    namespace = {"__file__": str(HOOK), "__name__": "v436_exactly_once_test"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def write_counter(path, *, day, count, gui_count=None, global_gui_count=None):
    gui_count = count if gui_count is None else gui_count
    global_gui_count = (
        gui_count if global_gui_count is None else global_gui_count
    )
    payload = {
        "friend_help_daily_count": count,
        "friend_help_daily_date": day,
        "gui_metrics": {
            "date": day,
            "friend_farming_count": gui_count,
        },
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
                "gui_metrics": {
                    "date": day,
                    "friend_farming_count": gui_count,
                },
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_counter(path):
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return (
        int(payload["friend_help_daily_count"]),
        int(payload["instances"]["1"]["friend_help_daily_count"]),
        int(payload["gui_metrics"]["friend_farming_count"]),
        int(payload["instances"]["1"]["gui_metrics"]["friend_farming_count"]),
        int(payload["instances"]["__global__"]["gui_metrics"]["friend_farming_count"]),
    )


def read_csv_help(path, day):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    row = next(item for item in rows if item["date"] == day)
    return int(row["friend_help"])


def write_csv_help(path, *, day, count):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "date", "harvest", "operation", "friend_steal", "friend_help",
            ),
        )
        writer.writeheader()
        writer.writerow({
            "date": day,
            "harvest": 0,
            "operation": 0,
            "friend_steal": 0,
            "friend_help": count,
        })


class NativeFriendHelpExactlyOnce20260809Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(*FUNCTIONS)
        self.namespace.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_DAILY_METRICS_LAST_SYNC_DAY": "",
            "_DAILY_METRICS_REPAIR_PENDING": False,
            "_write": lambda _message: None,
        })

    def _context(self, day, count=0):
        return types.SimpleNamespace(
            instance_id="1",
            friend_help_daily_count=count,
            friend_help_daily_date=day,
            _instance_metrics={
                "1": {"date": day, "friend_farming_count": count}
            },
            gui_metrics={"date": day, "friend_farming_count": count},
        )

    def _assert_surfaces(self, *, context, paths, csv_paths, day, expected):
        self.assertEqual(expected, context.friend_help_daily_count)
        self.assertEqual(
            expected, context._instance_metrics["1"]["friend_farming_count"]
        )
        self.assertEqual(expected, context.gui_metrics["friend_farming_count"])
        for path in paths:
            self.assertEqual(
                (expected, expected, expected, expected, expected),
                read_counter(path),
            )
        for path in csv_paths:
            self.assertEqual(expected, read_csv_help(path, day))

    def test_native_prewrite_of_expected_count_is_mirrored_not_incremented_again(self):
        """Native durable 0?1 plus proof remains exactly 1, never 2."""
        day = "2026-08-09"
        commit = self.namespace["_qqfarm_commit_native_friend_help_confirmation"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "QQFarmCopilot" / "daily_counters.json"
            mirror = primary.with_name("daily_counters.hook.json")
            portable_csv = root / "portable" / "daily_action_stats.csv"
            profile_csv = root / "profile" / "daily_action_stats.csv"
            for path in (primary, mirror):
                # This is the native runtime recorder's early durable write.
                write_counter(path, day=day, count=1)
            context = self._context(day, count=1)

            with mock.patch.dict(
                os.environ,
                {"QQFARM_DAILY_COUNTERS_PATH": str(primary)},
                clear=False,
            ):
                recorded = commit(
                    context,
                    confirmed=True,
                    durable_before=0,
                    counter_paths=[str(primary), str(mirror)],
                    csv_paths=[str(portable_csv), str(profile_csv)],
                    today=day,
                )

            self.assertEqual(1, recorded)
            self._assert_surfaces(
                context=context,
                paths=(primary, mirror),
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=1,
            )

    def test_two_native_prewrites_follow_zero_one_two_without_bridge_double_add(self):
        """Two separately proven native writes must produce the exact 0?1?2 ledger."""
        day = "2026-08-09"
        commit = self.namespace["_qqfarm_commit_native_friend_help_confirmation"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "QQFarmCopilot" / "daily_counters.json"
            mirror = primary.with_name("daily_counters.hook.json")
            portable_csv = root / "portable" / "daily_action_stats.csv"
            profile_csv = root / "profile" / "daily_action_stats.csv"
            context = self._context(day, count=0)

            with mock.patch.dict(
                os.environ,
                {"QQFARM_DAILY_COUNTERS_PATH": str(primary)},
                clear=False,
            ):
                for before, expected in ((0, 1), (1, 2)):
                    for path in (primary, mirror):
                        write_counter(path, day=day, count=expected)
                    context.friend_help_daily_count = expected
                    context._instance_metrics["1"]["friend_farming_count"] = expected
                    context.gui_metrics["friend_farming_count"] = expected
                    recorded = commit(
                        context,
                        confirmed=True,
                        durable_before=before,
                        counter_paths=[str(primary), str(mirror)],
                        csv_paths=[str(portable_csv), str(profile_csv)],
                        today=day,
                    )
                    self.assertEqual(expected, recorded)
                    self._assert_surfaces(
                        context=context,
                        paths=(primary, mirror),
                        csv_paths=(portable_csv, profile_csv),
                        day=day,
                        expected=expected,
                    )

    def test_unproven_native_prewrite_is_rolled_back_from_json_csv_and_gui(self):
        """A visual-proof miss reverses the native early write from every mirror."""
        day = "2026-08-09"
        sync = self.namespace["_daily_metrics_sync_runtime"]
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "QQFarmCopilot" / "daily_counters.json"
            mirror = primary.with_name("daily_counters.hook.json")
            profile_csv = (
                root / "QQFarmCopilot" / "instances" / "default" / "stats"
                / "daily_action_stats.csv"
            )
            portable_root = root / "portable-runtime"
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None
            captures = iter(("before-frame", "after-frame"))
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: next(captures),
                "_friend_guard_help_button_match": lambda frame: (
                    {"matched": True, "center": (210, 592)}
                    if frame == "before-frame" else {"matched": False}
                ),
                "_qqfarm_native_friend_help_card_signature": (
                    lambda _frame: ("friend", "A")
                ),
                "_friend_help_visual_completion_proof": (
                    lambda *_args, **_kwargs: False
                ),
            })

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = 0
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": 0}
                    }
                    self.gui_metrics = {
                        "date": day, "friend_farming_count": 0
                    }

                def _record_friend_help_action(self):
                    # Native runtime persists before fresh visual confirmation.
                    self.friend_help_daily_count = 1
                    self._instance_metrics["1"]["friend_farming_count"] = 1
                    self.gui_metrics["friend_farming_count"] = 1
                    sync(
                        self,
                        counter_paths=[str(primary), str(mirror)],
                        csv_paths=[str(portable_csv), str(profile_csv)],
                        today=day,
                        force=True,
                        trusted_context_fields=("friend_help_daily_count",),
                    )
                    return "native-result"

                def process_friend_farm(self):
                    return self._record_friend_help_action()

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
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
                    "QQFARM_DAILY_COUNTERS_PATH": str(primary),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                context = FarmBotCV()
                self.assertEqual("native-result", context.process_friend_farm())

            self._assert_surfaces(
                context=context,
                paths=(primary, mirror),
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=0,
            )


    def test_pre_record_native_prewrite_is_not_taken_as_durable_baseline(self):
        """An unproven pre-record disk write must restore the prior ledger."""
        day = "2026-08-09"
        sync = self.namespace["_daily_metrics_sync_runtime"]
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "QQFarmCopilot" / "daily_counters.json"
            mirror = primary.with_name("daily_counters.hook.json")
            profile_csv = (
                root / "QQFarmCopilot" / "instances" / "default" / "stats"
                / "daily_action_stats.csv"
            )
            portable_root = root / "portable-runtime"
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None
            captures = iter(("before-frame", "after-frame"))
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": (
                    lambda _bot: next(captures)
                ),
                "_friend_guard_help_button_match": lambda frame: (
                    {"matched": True, "center": (210, 592)}
                    if frame == "before-frame" else {"matched": False}
                ),
                "_qqfarm_native_friend_help_card_signature": (
                    lambda _frame: ("friend", "A")
                ),
                "_friend_help_visual_completion_proof": (
                    lambda *_args, **_kwargs: False
                ),
            })

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = 0
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": 0}
                    }
                    self.gui_metrics = {
                        "date": day, "friend_farming_count": 0
                    }

                def _native_pre_record_write(self):
                    # Live v437 regression: native persists the +1 before the
                    # wrapped recorder snapshots its durable baseline.
                    self.friend_help_daily_count = 1
                    self._instance_metrics["1"]["friend_farming_count"] = 1
                    self.gui_metrics["friend_farming_count"] = 1
                    sync(
                        self,
                        counter_paths=[str(primary), str(mirror)],
                        csv_paths=[str(portable_csv), str(profile_csv)],
                        today=day,
                        force=True,
                        trusted_context_fields=("friend_help_daily_count",),
                    )

                def _record_friend_help_action(self):
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._native_pre_record_write()
                    return self._record_friend_help_action()

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
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
                    "QQFARM_DAILY_COUNTERS_PATH": str(primary),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                context = FarmBotCV()
                self.assertEqual(
                    "native-recorder-result", context.process_friend_farm()
                )

            self._assert_surfaces(
                context=context,
                paths=(primary, mirror),
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=0,
            )


    def test_missing_preproof_prewrite_is_rolled_back_from_every_active_mirror(self):
        """A no-frame prewrite cannot bypass the native transaction guard."""
        day = "2026-08-09"
        baseline = 17
        sync = self.namespace["_daily_metrics_sync_runtime"]
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None
            # The pre-action frame cannot establish visual proof, but native code
            # still prewrites B+1 before it calls its recorder.
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: None,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
                "_friend_help_visual_completion_proof": lambda *_a, **_k: False,
            })

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": baseline}
                    }
                    self.gui_metrics = {
                        "date": day, "friend_farming_count": baseline
                    }

                def _native_pre_record_write(self):
                    self.friend_help_daily_count = baseline + 1
                    self._instance_metrics["1"]["friend_farming_count"] = baseline + 1
                    self.gui_metrics["friend_farming_count"] = baseline + 1
                    sync(
                        self,
                        today=day,
                        force=True,
                        trusted_context_fields=("friend_help_daily_count",),
                    )

                def _record_friend_help_action(self):
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._native_pre_record_write()
                    return self._record_friend_help_action()

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
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
                self.assertEqual(
                    "native-recorder-result", context.process_friend_farm()
                )

            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


    def test_capture_exception_prewrite_is_rolled_back_from_every_active_mirror(self):
        """A capture exception must still leave the native recorder guarded."""
        day = "2026-08-09"
        baseline = 23
        sync = self.namespace["_daily_metrics_sync_runtime"]
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace["_friend_guard_sleep"] = lambda _seconds: None

            def capture_failure(_bot):
                raise RuntimeError("simulated pre-action capture failure")

            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": capture_failure,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
                "_friend_help_visual_completion_proof": lambda *_a, **_k: False,
            })

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": baseline}
                    }
                    self.gui_metrics = {
                        "date": day, "friend_farming_count": baseline
                    }

                def _native_pre_record_write(self):
                    self.friend_help_daily_count = baseline + 1
                    self._instance_metrics["1"]["friend_farming_count"] = baseline + 1
                    self.gui_metrics["friend_farming_count"] = baseline + 1
                    sync(
                        self,
                        today=day,
                        force=True,
                        trusted_context_fields=("friend_help_daily_count",),
                    )

                def _record_friend_help_action(self):
                    return "native-recorder-result"

                def process_friend_farm(self):
                    self._native_pre_record_write()
                    return self._record_friend_help_action()

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
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
                self.assertEqual(
                    "native-recorder-result", context.process_friend_farm()
                )

            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


    def test_quorum_baseline_prefers_strict_same_day_majority_over_lone_ahead_mirror(self):
        """The recovery baseline must be a strict durable-file majority, not max()."""
        day = "2026-08-09"
        snapshot = self.namespace["_qqfarm_native_friend_help_durable_snapshot"]
        quorum = self.namespace.get("_qqfarm_native_friend_help_quorum_baseline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
            )
            for path in paths:
                write_counter(path, day=day, count=30)
            # This is the live 30/33 drift: the Local primary file has an
            # orphan native prewrite while the other durable mirrors agree.
            write_counter(
                local,
                day=day,
                count=33,
                gui_count=33,
                global_gui_count=27,
            )
            context = self._context(day, count=33)
            self.namespace["_daily_business_date"] = lambda: day

            with mock.patch.dict(
                os.environ,
                {
                    "QQFARM_DAILY_COUNTERS_PATH": str(roaming),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                # Keep max() available to the existing rollback transaction so
                # it can detect the ahead write.  Only the preflight baseline
                # chooses the independent durable quorum.
                self.assertEqual(33, snapshot(context))
                self.assertTrue(callable(quorum))
                self.assertEqual(30, quorum(context))

    def test_quorum_baseline_declines_a_tied_durable_ledger(self):
        """A tie has no safe recovery target and must not trigger a rewrite."""
        day = "2026-08-09"
        quorum = self.namespace.get("_qqfarm_native_friend_help_quorum_baseline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            values = (
                (roaming, 30),
                (roaming.with_name("daily_counters.hook.json"), 30),
                (local, 33),
                (local.with_name("daily_counters.hook.json"), 33),
            )
            for path, count in values:
                write_counter(path, day=day, count=count)
            context = self._context(day, count=33)
            self.namespace["_daily_business_date"] = lambda: day

            with mock.patch.dict(
                os.environ,
                {
                    "QQFARM_DAILY_COUNTERS_PATH": str(roaming),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                self.assertTrue(callable(quorum))
                self.assertIsNone(quorum(context))

    def test_quorum_preflight_restores_lone_ahead_mirror_before_native_processing(self):
        """The native process must see restored B, not a lone B+3 mirror."""
        day = "2026-08-09"
        baseline = 30
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            write_counter(
                local,
                day=day,
                count=baseline + 3,
                gui_count=baseline + 3,
                global_gui_count=27,
            )
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: None,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
            })
            seen_by_native = []

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline + 3
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {
                            "date": day,
                            "friend_farming_count": baseline + 3,
                        }
                    }
                    self.gui_metrics = {
                        "date": day,
                        "friend_farming_count": baseline + 3,
                    }

                def process_friend_farm(self):
                    # No action is taken here.  The assertion proves that the
                    # recovery completed before native behavior can begin.
                    seen_by_native.append(self.friend_help_daily_count)
                    return "native-no-action"

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
            )
            self.assertTrue(cached)

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
                self.assertEqual("native-no-action", context.process_friend_farm())

            self.assertEqual([baseline], seen_by_native)
            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


    def test_quorum_preflight_repairs_stale_nested_global_gui_before_native_processing(self):
        """A same-day global GUI residue is normalized before native serialization."""
        day = "2026-08-09"
        baseline = 30
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            for path in (profile_csv, portable_csv):
                write_csv_help(path, day=day, count=baseline)
            # Exact startup residue from the field capture: root, instance, and
            # root GUI all agree at B, but the native serializer's nested
            # __global__.gui_metrics bucket is still M.
            write_counter(
                local,
                day=day,
                count=baseline,
                gui_count=baseline,
                global_gui_count=27,
            )
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: None,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
            })
            seen_by_native = []

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {
                            "date": day,
                            "friend_farming_count": baseline,
                        },
                        "__global__": {
                            "gui_metrics": {
                                "date": day,
                                "friend_farming_count": 27,
                            },
                        },
                    }
                    self.gui_metrics = {
                        "date": day,
                        "friend_farming_count": baseline,
                    }

                def process_friend_farm(self):
                    # This captures the exact native serializer source before
                    # any native save or action can run.
                    seen_by_native.append((
                        self.friend_help_daily_count,
                        self._instance_metrics["1"]["friend_farming_count"],
                        self.gui_metrics["friend_farming_count"],
                        self._instance_metrics["__global__"]
                        ["gui_metrics"]["friend_farming_count"],
                        read_counter(local),
                    ))
                    return "native-no-action"

            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
            )
            self.assertTrue(cached)

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
                self.assertEqual("native-no-action", context.process_friend_farm())

            expected_native_view = (
                baseline,
                baseline,
                baseline,
                baseline,
                (baseline, baseline, baseline, baseline, baseline),
            )
            self.assertEqual([expected_native_view], seen_by_native)
            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


    def test_missing_or_stale_candidate_never_leaves_native_prewrite_unsynced(self):
        """Direct or stale recorder entry must roll back one orphan native prewrite."""
        day = "2026-08-09"
        baseline = 30
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]

        for case in ("missing", "stale"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                portable_root = root / "portable-runtime"
                roaming = (
                    root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
                )
                local = (
                    root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
                )
                legacy = (
                    portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                    / "daily_counters.json"
                )
                paths = (
                    roaming,
                    roaming.with_name("daily_counters.hook.json"),
                    local,
                    local.with_name("daily_counters.hook.json"),
                    legacy,
                    legacy.with_name("daily_counters.hook.json"),
                )
                profile_csv = (
                    root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                    / "stats" / "daily_action_stats.csv"
                )
                portable_csv = (
                    portable_root / "UserData" / "QQFarmCopilot" / "instances"
                    / "default" / "stats" / "daily_action_stats.csv"
                )
                for path in paths:
                    write_counter(path, day=day, count=baseline)
                for path in (profile_csv, portable_csv):
                    write_csv_help(path, day=day, count=baseline)
                # Exact live signature: native has advanced Local root/instance
                # surfaces only; both CSVs and all canonical mirrors remain B.
                write_counter(
                    local,
                    day=day,
                    count=baseline + 1,
                    gui_count=baseline + 1,
                    global_gui_count=27,
                )
                self.namespace["__file__"] = str(portable_root / "hook.py")
                self.namespace["_daily_business_date"] = lambda: day
                self.namespace["_friend_guard_sleep"] = lambda _seconds: None
                calls = []

                class FarmBotCV:
                    def __init__(self):
                        self.instance_id = "1"
                        self.friend_help_daily_count = baseline + 1
                        self.friend_help_daily_date = day
                        self._instance_metrics = {
                            "1": {
                                "date": day,
                                "friend_farming_count": baseline + 1,
                            }
                        }
                        self.gui_metrics = {
                            "date": day,
                            "friend_farming_count": baseline + 1,
                        }

                    def _record_friend_help_action(self):
                        calls.append(self.friend_help_daily_count)
                        return "native-recorder-result"

                FarmBotCV._record_friend_help_action, bridged = recorder_wrapper(
                    FarmBotCV._record_friend_help_action,
                    "FarmBotCV._record_friend_help_action",
                )
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
                    if case == "stale":
                        import time

                        context._qqfarm_native_v225_friend_help_candidate = {
                            "timestamp": time.monotonic() - 9.0,
                            "durable_before": baseline,
                            "before_frame": "old-before-frame",
                            "before_match": {
                                "matched": True,
                                "center": (210, 592),
                            },
                            "card_signature": ("friend", "A"),
                        }
                    self.assertEqual(
                        "native-recorder-result",
                        context._record_friend_help_action(),
                    )

                self.assertEqual([baseline], calls)
                self._assert_surfaces(
                    context=context,
                    paths=paths,
                    csv_paths=(portable_csv, profile_csv),
                    day=day,
                    expected=baseline,
                )


    def test_native_recorder_exception_after_prewrite_rolls_back_every_mirror(self):
        """A recorder exception after B?B+1 remains an unconfirmed transaction."""
        day = "2026-08-09"
        baseline = 30
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            for path in (profile_csv, portable_csv):
                write_csv_help(path, day=day, count=baseline)
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            calls = []

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {"date": day, "friend_farming_count": baseline}
                    }
                    self.gui_metrics = {
                        "date": day,
                        "friend_farming_count": baseline,
                    }

                def _native_prewrite_then_fail(self):
                    self.friend_help_daily_count = baseline + 1
                    self._instance_metrics["1"]["friend_farming_count"] = baseline + 1
                    self.gui_metrics["friend_farming_count"] = baseline + 1
                    write_counter(
                        local,
                        day=day,
                        count=baseline + 1,
                        gui_count=baseline + 1,
                        global_gui_count=27,
                    )

                def _record_friend_help_action(self):
                    calls.append(self.friend_help_daily_count)
                    self._native_prewrite_then_fail()
                    raise RuntimeError("simulated native recorder failure")

            FarmBotCV._record_friend_help_action, bridged = recorder_wrapper(
                FarmBotCV._record_friend_help_action,
                "FarmBotCV._record_friend_help_action",
            )
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
                with self.assertRaisesRegex(RuntimeError, "simulated native recorder failure"):
                    context._record_friend_help_action()

            self.assertEqual([baseline], calls)
            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


    def test_unconfirmed_gui_only_prewrite_repairs_every_default_mirror(self):
        """A stale GUI-only native prewrite must be overwritten with durable state."""
        day = "2026-08-09"
        rollback = self.namespace["_qqfarm_commit_native_friend_help_confirmation"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            configured = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                configured,
                configured.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            csv_paths = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv",
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv",
            )
            for path in paths:
                write_counter(path, day=day, count=18)
            # This is the exact live defect: durable root/instance counters are
            # still 18, while one LocalAppData GUI mirror remains at 19.
            write_counter(
                local,
                day=day,
                count=18,
                gui_count=19,
                global_gui_count=14,
            )
            context = self._context(day, count=19)
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day

            with mock.patch.dict(
                os.environ,
                {
                    "QQFARM_DAILY_COUNTERS_PATH": str(configured),
                    "LOCALAPPDATA": str(root / "local"),
                    "APPDATA": str(root / "roaming"),
                },
                clear=True,
            ):
                self.assertEqual(
                    18,
                    rollback(
                        context,
                        confirmed=False,
                        durable_before=18,
                    ),
                )

            self._assert_surfaces(
                context=context,
                paths=paths,
                csv_paths=csv_paths,
                day=day,
                expected=18,
            )


    def test_quorum_repair_then_unconfirmed_native_save_cannot_restore_stale_nested_global_gui(self):
        """A native Local-primary save must not restore the actual nested global GUI payload."""
        day = "2026-08-09"
        baseline = 30
        cache_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ]
        recorder_wrapper = self.namespace[
            "_wrap_native_v225_friend_help_confirmation"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable_root = root / "portable-runtime"
            roaming = (
                root / "roaming" / "QQFarmCopilot" / "daily_counters.json"
            )
            local = (
                root / "local" / "qq-farm-bot-rev" / "daily_counters.json"
            )
            legacy = (
                portable_root / "UserData" / "legacy-qq-farm-bot-rev"
                / "daily_counters.json"
            )
            paths = (
                roaming,
                roaming.with_name("daily_counters.hook.json"),
                local,
                local.with_name("daily_counters.hook.json"),
                legacy,
                legacy.with_name("daily_counters.hook.json"),
            )
            profile_csv = (
                root / "roaming" / "QQFarmCopilot" / "instances" / "default"
                / "stats" / "daily_action_stats.csv"
            )
            portable_csv = (
                portable_root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            for path in paths:
                write_counter(path, day=day, count=baseline)
            for path in (profile_csv, portable_csv):
                write_csv_help(path, day=day, count=baseline)
            # Exact deployed state: a lone Local primary durable prewrite is
            # accompanied by a stale native __global__ GUI bucket.
            write_counter(
                local,
                day=day,
                count=baseline + 3,
                gui_count=baseline + 3,
                global_gui_count=27,
            )
            self.namespace["__file__"] = str(portable_root / "hook.py")
            self.namespace["_daily_business_date"] = lambda: day
            self.namespace.update({
                "_qqfarm_capture_native_friend_help_frame": lambda _bot: None,
                "_friend_guard_help_button_match": lambda _frame: {"matched": False},
                "_qqfarm_native_friend_help_card_signature": lambda _frame: None,
            })

            class FarmBotCV:
                def __init__(self):
                    self.instance_id = "1"
                    self.friend_help_daily_count = baseline + 3
                    self.friend_help_daily_date = day
                    self._instance_metrics = {
                        "1": {
                            "date": day,
                            "friend_farming_count": baseline + 3,
                        },
                        "__global__": {
                            "gui_metrics": {
                                "date": day,
                                "friend_farming_count": 27,
                            },
                        },
                    }
                    self.gui_metrics = {
                        "date": day,
                        "friend_farming_count": baseline + 3,
                    }

                def _record_friend_help_action(self):
                    # Native runtime persists before visual confirmation, then
                    # fails.  Its serializer keeps the stale global bucket.
                    self.friend_help_daily_count = baseline + 1
                    self._instance_metrics["1"]["friend_farming_count"] = (
                        baseline + 1
                    )
                    self.gui_metrics["friend_farming_count"] = baseline + 1
                    write_counter(
                        local,
                        day=day,
                        count=baseline + 1,
                        gui_count=baseline + 1,
                        global_gui_count=(
                            self._instance_metrics["__global__"]
                            ["gui_metrics"]["friend_farming_count"]
                        ),
                    )
                    raise RuntimeError("simulated native recorder failure")

                def process_friend_farm(self):
                    try:
                        self._record_friend_help_action()
                    except RuntimeError:
                        pass
                    # This is the later native Local-primary persistence pass
                    # that reproduced the live 48/48/48/48/27 state.
                    write_counter(
                        local,
                        day=day,
                        count=self.friend_help_daily_count,
                        gui_count=self.gui_metrics["friend_farming_count"],
                        global_gui_count=(
                            self._instance_metrics["__global__"]
                            ["gui_metrics"]["friend_farming_count"]
                        ),
                    )
                    return "native-serialized"

            FarmBotCV._record_friend_help_action, bridged = recorder_wrapper(
                FarmBotCV._record_friend_help_action,
                "FarmBotCV._record_friend_help_action",
            )
            self.assertTrue(bridged)
            FarmBotCV.process_friend_farm, cached = cache_wrapper(
                FarmBotCV.process_friend_farm,
                "FarmBotCV.process_friend_farm",
            )
            self.assertTrue(cached)

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
                context=context,
                paths=paths,
                csv_paths=(portable_csv, profile_csv),
                day=day,
                expected=baseline,
            )


if __name__ == "__main__":
    unittest.main()
