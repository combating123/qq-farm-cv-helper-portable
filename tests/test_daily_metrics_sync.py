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


if __name__ == "__main__":
    unittest.main()
