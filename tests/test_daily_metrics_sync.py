import ast
import csv
import json
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_function(name):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not nodes:
        return None
    module = ast.Module(body=[nodes[0]], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace[name]


class DailyMetricsSyncTests(unittest.TestCase):
    def test_sync_uses_largest_same_day_counters_for_live_panel_and_csv(self):
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            local = root / "local.json"
            portable = root / "portable.json"
            csv_path = root / "daily_action_stats.csv"
            today = "2026-07-28"

            local.write_text(json.dumps({
                "instances": {
                    "1": {
                        "friend_help_daily_count": 273,
                        "friend_help_daily_date": today,
                        "self_actions_daily_count": 46,
                        "self_actions_daily_date": today,
                    },
                    "__global__": {
                        "gui_metrics": {
                            "date": today,
                            "friend_farming_count": 0,
                            "self_farming_count": 0,
                            "self_harvest_count": 7,
                        }
                    },
                },
                "friend_help_daily_count": 270,
                "friend_help_daily_date": today,
                "self_actions_daily_count": 40,
                "self_actions_daily_date": today,
                "gui_metrics": {
                    "date": today,
                    "friend_farming_count": 2,
                    "self_farming_count": 4,
                },
            }), encoding="utf-8")
            portable.write_text(json.dumps({
                "instances": {
                    "1": {
                        "friend_help_daily_count": 261,
                        "friend_help_daily_date": today,
                        "self_actions_daily_count": 45,
                        "self_actions_daily_date": today,
                    }
                },
                "friend_help_daily_count": 260,
                "friend_help_daily_date": today,
                "self_actions_daily_count": 45,
                "self_actions_daily_date": today,
            }), encoding="utf-8")
            csv_path.write_text(
                "date,harvest,operation,friend_steal,friend_help\n"
                "2026-05-30,0,224,13,122\n",
                encoding="utf-8",
            )

            context = types.SimpleNamespace(
                current_instance_id="1",
                _instance_metrics={
                    "1": {
                        "date": today,
                        "friend_farming_count": 1,
                        "self_farming_count": 4,
                        "self_harvest_count": 7,
                    }
                },
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda message: None,
            })

            summary = sync(
                context,
                counter_paths=[str(local), str(portable)],
                csv_paths=[str(csv_path)],
                today=today,
                force=True,
            )

            self.assertEqual(273, summary["friend_farming_count"])
            self.assertEqual(46, summary["self_farming_count"])
            live = context._instance_metrics["1"]
            self.assertEqual(273, live["friend_farming_count"])
            self.assertEqual(46, live["self_farming_count"])
            self.assertEqual(7, live["self_harvest_count"])

            for path in (local, portable):
                payload = json.loads(path.read_text(encoding="utf-8"))
                for metrics in (
                    payload["gui_metrics"],
                    payload["instances"]["__global__"]["gui_metrics"],
                    payload["instances"]["1"]["gui_metrics"],
                ):
                    self.assertEqual(today, metrics["date"])
                    self.assertEqual(273, metrics["friend_farming_count"])
                    self.assertEqual(46, metrics["self_farming_count"])

            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            today_rows = [row for row in rows if row["date"] == today]
            self.assertEqual(1, len(today_rows))
            self.assertEqual("46", today_rows[0]["operation"])
            self.assertEqual("273", today_rows[0]["friend_help"])

    def test_sync_resets_stale_live_metrics_when_the_date_changes(self):
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            counters = Path(temp_dir) / "daily_counters.json"
            counters.write_text(json.dumps({
                "friend_help_daily_count": 999,
                "friend_help_daily_date": "2026-07-27",
                "self_actions_daily_count": 888,
                "self_actions_daily_date": "2026-07-27",
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                current_instance_id="1",
                _instance_metrics={
                    "1": {
                        "date": "2026-07-27",
                        "friend_farming_count": 999,
                        "self_farming_count": 888,
                        "self_harvest_count": 44,
                    }
                },
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda message: None,
            })

            summary = sync(
                context,
                counter_paths=[str(counters)],
                csv_paths=[],
                today="2026-07-28",
                force=True,
            )

            self.assertEqual(0, summary["friend_farming_count"])
            self.assertEqual(0, summary["self_farming_count"])
            live = context._instance_metrics["1"]
            self.assertEqual("2026-07-28", live["date"])
            self.assertEqual(0, live["friend_farming_count"])
            self.assertEqual(0, live["self_farming_count"])
            self.assertEqual(0, live["self_harvest_count"])


    def test_default_sync_prefers_configured_portable_same_day_radish_counter_over_stale_local(self):
        """A portable launch must restore today's durable counter before crop choice."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable = root / "Roaming" / "QQFarmCopilot" / "daily_counters.json"
            local = root / "Local" / "qq-farm-bot-rev" / "daily_counters.json"
            portable.parent.mkdir(parents=True, exist_ok=True)
            local.parent.mkdir(parents=True, exist_ok=True)
            today = "2026-07-30"
            portable.write_text(json.dumps({
                "daily_radish_exp_count": 60,
                "daily_radish_exp_date": today,
                "instances": {
                    "1": {
                        "daily_radish_exp_count": 60,
                        "daily_radish_exp_date": today,
                    }
                },
            }), encoding="utf-8")
            local.write_text(json.dumps({
                "daily_radish_exp_count": 0,
                "daily_radish_exp_date": "2026-07-31",
                "instances": {
                    "1": {
                        "daily_radish_exp_count": 0,
                        "daily_radish_exp_date": "2026-07-31",
                    }
                },
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                daily_radish_exp_count=0,
                daily_radish_exp_date="2026-07-31",
                _instance_metrics={"1": {"date": today}},
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda message: None,
            })
            import os
            from unittest import mock
            with mock.patch.dict(os.environ, {
                "QQFARM_DAILY_COUNTERS_PATH": str(portable),
                "LOCALAPPDATA": str(root / "Local"),
            }, clear=False):
                summary = sync(
                    context,
                    counter_paths=None,
                    csv_paths=[],
                    today=today,
                    force=True,
                )

            self.assertEqual(60, summary["daily_radish_exp_count"])
            self.assertEqual(60, context.daily_radish_exp_count)
            self.assertEqual(today, context.daily_radish_exp_date)
            restored = json.loads(portable.read_text(encoding="utf-8"))
            self.assertEqual(60, restored["daily_radish_exp_count"])
            self.assertEqual(today, restored["daily_radish_exp_date"])


    def test_default_sync_treats_configured_portable_counter_as_authoritative_for_today(self):
        """A legacy Local mirror must not inflate the active portable daily quota."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            portable = root / "Roaming" / "QQFarmCopilot" / "daily_counters.json"
            local = root / "Local" / "qq-farm-bot-rev" / "daily_counters.json"
            portable.parent.mkdir(parents=True, exist_ok=True)
            local.parent.mkdir(parents=True, exist_ok=True)
            today = "2026-07-30"
            portable.write_text(json.dumps({
                "daily_radish_exp_count": 60,
                "daily_radish_exp_date": today,
                "instances": {
                    "1": {
                        "daily_radish_exp_count": 60,
                        "daily_radish_exp_date": today,
                    }
                },
            }), encoding="utf-8")
            local.write_text(json.dumps({
                "daily_radish_exp_count": 999,
                "daily_radish_exp_date": today,
                "instances": {
                    "1": {
                        "daily_radish_exp_count": 999,
                        "daily_radish_exp_date": today,
                    }
                },
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                daily_radish_exp_count=999,
                daily_radish_exp_date=today,
                _instance_metrics={"1": {"date": today}},
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda message: None,
            })
            import os
            from unittest import mock
            with mock.patch.dict(os.environ, {
                "QQFARM_DAILY_COUNTERS_PATH": str(portable),
                "LOCALAPPDATA": str(root / "Local"),
            }, clear=False):
                summary = sync(
                    context,
                    counter_paths=None,
                    csv_paths=[],
                    today=today,
                    force=True,
                )

            self.assertEqual(60, summary["daily_radish_exp_count"])
            self.assertEqual(60, context.daily_radish_exp_count)
            merged_local = json.loads(local.read_text(encoding="utf-8"))
            self.assertEqual(60, merged_local["daily_radish_exp_count"])
            self.assertEqual(today, merged_local["daily_radish_exp_date"])


    def test_default_sync_reconciles_configured_sibling_hook_to_primary(self):
        """The portable primary must also repair its stale .hook sibling."""
        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)

        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            from unittest import mock

            root = Path(temp_dir)
            primary = root / "Roaming" / "QQFarmCopilot" / "daily_counters.json"
            sibling = primary.with_name("daily_counters.hook.json")
            primary.parent.mkdir(parents=True, exist_ok=True)
            today = "2026-08-03"
            primary.write_text(json.dumps({
                "friend_help_daily_count": 10,
                "friend_help_daily_date": today,
                "friend_trouble_daily_count": 0,
                "friend_trouble_daily_date": today,
                "self_actions_daily_count": 0,
                "self_actions_daily_date": today,
                "gui_metrics": {
                    "date": today,
                    "friend_farming_count": 10,
                    "friend_harvest_count": 8,
                },
            }), encoding="utf-8")
            sibling.write_text(json.dumps({
                "friend_help_daily_count": 680,
                "friend_help_daily_date": today,
                "friend_trouble_daily_count": 9,
                "friend_trouble_daily_date": today,
                "self_actions_daily_count": 105,
                "self_actions_daily_date": today,
                "gui_metrics": {
                    "date": today,
                    "friend_farming_count": 680,
                    "friend_harvest_count": 8,
                },
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                _instance_metrics={
                    "1": {
                        "date": today,
                        "friend_farming_count": 10,
                        "friend_harvest_count": 8,
                    }
                },
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda _message: None,
            })

            with mock.patch.dict(os.environ, {
                "QQFARM_DAILY_COUNTERS_PATH": str(primary),
                "LOCALAPPDATA": str(root / "Local"),
            }, clear=False):
                sync(
                    context,
                    counter_paths=None,
                    csv_paths=[],
                    today=today,
                    force=True,
                )

            repaired = json.loads(sibling.read_text(encoding="utf-8"))
            self.assertEqual(10, repaired["friend_help_daily_count"])
            self.assertEqual(0, repaired["friend_trouble_daily_count"])
            self.assertEqual(0, repaired["self_actions_daily_count"])
            self.assertEqual(10, repaired["gui_metrics"]["friend_farming_count"])
            self.assertEqual(0, repaired["gui_metrics"]["self_farming_count"])
            self.assertEqual(0, repaired["gui_metrics"]["troublemaker_count"])
            self.assertEqual(8, repaired["gui_metrics"]["friend_harvest_count"])



    def test_counter_sync_uses_a_unique_temp_file_for_each_write(self):
        """Two forced syncs in one process must not share the same temp path."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            from unittest import mock

            root = Path(temp_dir)
            counter_path = root / "daily_counters.json"
            today = "2026-08-02"
            counter_path.write_text(json.dumps({
                "self_actions_daily_count": 3,
                "self_actions_daily_date": today,
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                self_actions_daily_count=3,
                self_actions_daily_date=today,
                _instance_metrics={"1": {"date": today}},
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda message: None,
            })
            real_replace = os.replace
            temp_sources = []

            def capture_replace(source, target):
                if str(target) == str(counter_path):
                    temp_sources.append(str(source))
                return real_replace(source, target)

            with mock.patch("os.replace", side_effect=capture_replace):
                for _ in range(2):
                    sync(
                        context,
                        counter_paths=[str(counter_path)],
                        csv_paths=[],
                        today=today,
                        force=True,
                    )

            self.assertEqual(2, len(temp_sources))
            self.assertNotEqual(temp_sources[0], temp_sources[1])

    def test_counter_sync_retries_transient_permission_error(self):
        """A short Windows file lock must not leave the durable counter stale."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            from unittest import mock

            root = Path(temp_dir)
            counter_path = root / "daily_counters.json"
            today = "2026-08-02"
            counter_path.write_text(json.dumps({
                "self_actions_daily_count": 1,
                "self_actions_daily_date": today,
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                self_actions_daily_count=7,
                self_actions_daily_date=today,
                _instance_metrics={"1": {"date": today}},
            )
            logs = []
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": logs.append,
            })
            real_replace = os.replace
            replace_calls = []

            def flaky_replace(source, target):
                replace_calls.append((str(source), str(target)))
                if len(replace_calls) == 1:
                    raise PermissionError(13, "sharing violation", str(target))
                return real_replace(source, target)

            with mock.patch("os.replace", side_effect=flaky_replace):
                summary = sync(
                    context,
                    counter_paths=[str(counter_path)],
                    csv_paths=[],
                    today=today,
                    force=True,
                )

            self.assertEqual(7, summary["self_actions_daily_count"])
            persisted = json.loads(counter_path.read_text(encoding="utf-8"))
            self.assertEqual(7, persisted["self_actions_daily_count"])
            self.assertEqual(2, len(replace_calls))
            self.assertTrue(any(
                "daily metrics atomic replace retry" in message
                for message in logs
            ))

    def test_csv_sync_retries_transient_permission_error(self):
        """The daily stats CSV must survive one transient replace sharing violation."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            from unittest import mock

            root = Path(temp_dir)
            counter_path = root / "daily_counters.json"
            csv_path = root / "daily_action_stats.csv"
            today = "2026-08-02"
            counter_path.write_text(json.dumps({
                "friend_help_daily_count": 4,
                "friend_help_daily_date": today,
            }), encoding="utf-8")
            csv_path.write_text(
                "date,harvest,operation,friend_steal,friend_help\n"
                "2026-08-01,0,1,0,2\n",
                encoding="utf-8",
            )
            context = types.SimpleNamespace(
                instance_id="1",
                _instance_metrics={"1": {"date": today}},
            )
            logs = []
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": logs.append,
            })
            real_replace = os.replace
            replace_calls = []

            def flaky_csv_replace(source, target):
                if str(target) == str(csv_path):
                    replace_calls.append((str(source), str(target)))
                    if len(replace_calls) == 1:
                        raise PermissionError(13, "sharing violation", str(target))
                return real_replace(source, target)

            with mock.patch("os.replace", side_effect=flaky_csv_replace):
                sync(
                    context,
                    counter_paths=[str(counter_path)],
                    csv_paths=[str(csv_path)],
                    today=today,
                    force=True,
                )

            rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
            today_rows = [row for row in rows if row.get("date") == today]
            self.assertEqual(1, len(today_rows))
            self.assertEqual("4", today_rows[0]["friend_help"])
            self.assertEqual(2, len(replace_calls))
            self.assertTrue(any(
                "daily metrics atomic replace retry" in message
                for message in logs
            ))


    def test_default_csv_sync_updates_configured_and_portable_profile_mirrors(self):
        """Default sync must keep both active QQFarmCopilot stats mirrors current."""
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            from unittest import mock

            root = Path(temp_dir)
            configured_dir = (
                root / "UserData" / "WindowsProfile" / "RoamingAppData"
                / "QQFarmCopilot"
            )
            configured_counter = configured_dir / "daily_counters.json"
            configured_csv = (
                configured_dir / "instances" / "default" / "stats"
                / "daily_action_stats.csv"
            )
            portable_csv = (
                root / "UserData" / "QQFarmCopilot" / "instances"
                / "default" / "stats" / "daily_action_stats.csv"
            )
            today = "2026-08-03"
            configured_dir.mkdir(parents=True, exist_ok=True)
            configured_counter.write_text(json.dumps({
                "friend_help_daily_count": 9,
                "friend_help_daily_date": today,
                "gui_metrics": {
                    "date": today,
                    "friend_farming_count": 9,
                    "friend_harvest_count": 4,
                },
            }), encoding="utf-8")
            for csv_path in (configured_csv, portable_csv):
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                csv_path.write_text(
                    "date,harvest,operation,friend_steal,friend_help\n"
                    f"{today},0,0,0,0\n",
                    encoding="utf-8",
                )

            context = types.SimpleNamespace(
                instance_id="1",
                _instance_metrics={"1": {"date": today}},
            )
            sync.__globals__.update({
                "__file__": str(root / "hook.py"),
                "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
                "_write": lambda _message: None,
            })

            with mock.patch.dict(os.environ, {
                "QQFARM_DAILY_COUNTERS_PATH": str(configured_counter),
            }, clear=False):
                summary = sync(
                    context,
                    counter_paths=[str(configured_counter)],
                    csv_paths=None,
                    today=today,
                    force=True,
                )

            self.assertEqual(9, summary["friend_farming_count"])
            self.assertEqual(4, summary["friend_harvest_count"])
            for csv_path in (configured_csv, portable_csv):
                with csv_path.open("r", encoding="utf-8", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                today_rows = [row for row in rows if row.get("date") == today]
                self.assertEqual(1, len(today_rows), str(csv_path))
                self.assertEqual("9", today_rows[0]["friend_help"], str(csv_path))
                self.assertEqual("4", today_rows[0]["friend_steal"], str(csv_path))


    def test_sync_bypasses_ten_second_throttle_when_business_date_changes(self):
        sync = load_function("_daily_metrics_sync_runtime")
        if sync is None:
            self.fail("_daily_metrics_sync_runtime is missing")

        with tempfile.TemporaryDirectory() as temp_dir:
            import time as time_module

            root = Path(temp_dir)
            counter_path = root / "daily_counters.json"
            csv_path = root / "daily_action_stats.csv"
            old_day = "2026-08-04"
            new_day = "2026-08-05"
            counter_path.write_text(json.dumps({
                "gui_metrics": {
                    "date": old_day,
                    "friend_farming_count": 7,
                    "friend_harvest_count": 3,
                },
                "friend_help_daily_count": 7,
                "friend_help_daily_date": old_day,
            }), encoding="utf-8")
            csv_path.write_text(
                "date,harvest,operation,friend_steal,friend_help\n"
                f"{old_day},0,0,3,7\n",
                encoding="utf-8",
            )
            context = types.SimpleNamespace(
                instance_id="1",
                _instance_metrics={
                    "1": {
                        "date": old_day,
                        "friend_farming_count": 7,
                        "friend_harvest_count": 3,
                    }
                },
            )
            sync.__globals__.update({
                "_DAILY_METRICS_LAST_SYNC_TS": time_module.time(),
                "_DAILY_METRICS_LAST_SYNC_DAY": old_day,
                "_write": lambda _message: None,
            })

            summary = sync(
                context,
                counter_paths=[str(counter_path)],
                csv_paths=[str(csv_path)],
                today=new_day,
                force=False,
            )

            self.assertEqual(new_day, summary["date"])
            self.assertEqual(new_day, context._instance_metrics["1"]["date"])
            self.assertEqual(
                new_day,
                json.loads(counter_path.read_text(encoding="utf-8"))[
                    "gui_metrics"
                ]["date"],
            )
            rows = list(csv.DictReader(
                csv_path.read_text(encoding="utf-8").splitlines()
            ))
            new_rows = [row for row in rows if row.get("date") == new_day]
            self.assertEqual(1, len(new_rows))
            self.assertEqual("0", new_rows[0]["friend_steal"])
            self.assertEqual("0", new_rows[0]["friend_help"])


if __name__ == "__main__":
    unittest.main()
