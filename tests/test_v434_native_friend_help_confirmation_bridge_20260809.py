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


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v434_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


FUNCTIONS = (
    "_daily_metrics_sync_runtime",
    "_qqfarm_native_friend_help_durable_snapshot",
    "_qqfarm_commit_native_friend_help_confirmation",
    "_qqfarm_capture_native_friend_help_frame",
    "_qqfarm_native_friend_help_card_signature",
    "_qqfarm_cache_native_v225_friend_help_candidate",
    "_wrap_native_v225_friend_help_candidate_cache",
    "_wrap_native_v225_friend_help_confirmation",
    "_patch_native_v225_friend_help_confirmation_for_module",
)


class NativeFriendHelpConfirmationBridge20260809Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(*FUNCTIONS)
        self.namespace.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_DAILY_METRICS_LAST_SYNC_DAY": "",
            "_DAILY_METRICS_REPAIR_PENDING": False,
            "_write": lambda _message: None,
        })

    def test_confirmed_native_help_writes_exactly_one_from_durable_baseline_not_native_runtime(self):
        """A native in-memory 28 must become durable 1 after one proven action."""
        day = "2026-08-09"
        commit = self.namespace["_qqfarm_commit_native_friend_help_confirmation"]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "QQFarmCopilot" / "daily_counters.json"
            mirror = primary.with_name("daily_counters.hook.json")
            portable_csv = root / "portable" / "daily_action_stats.csv"
            profile_csv = root / "profile" / "daily_action_stats.csv"
            context = types.SimpleNamespace(
                instance_id="1",
                friend_help_daily_count=0,
                friend_help_daily_date=day,
                _instance_metrics={
                    "1": {"date": day, "friend_farming_count": 28}
                },
                gui_metrics={"date": day, "friend_farming_count": 28},
            )

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
            self.assertEqual(1, context.friend_help_daily_count)
            self.assertEqual(1, context._instance_metrics["1"]["friend_farming_count"])
            self.assertEqual(1, context.gui_metrics["friend_farming_count"])
            for path in (primary, mirror):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(1, payload["friend_help_daily_count"])
                self.assertEqual(1, payload["gui_metrics"]["friend_farming_count"])
                self.assertEqual(1, payload["instances"]["1"]["friend_help_daily_count"])
                self.assertEqual(
                    1,
                    payload["instances"]["1"]["gui_metrics"]["friend_farming_count"],
                )
            for path in (portable_csv, profile_csv):
                with path.open("r", encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                row = next(item for item in rows if item["date"] == day)
                self.assertEqual("1", row["friend_help"])

    def test_native_recorder_commits_only_after_cached_preproof_and_fresh_postproof(self):
        """The native recorder may mutate runtime state, but it cannot self-authorize durable history."""
        events = []
        captures = iter(("before-frame", "after-frame"))
        commits = []

        class FarmBotCV:
            def __init__(self):
                self.instance_id = "1"
                self._instance_metrics = {
                    "1": {"date": "2026-08-09", "friend_farming_count": 27}
                }
                self.gui_metrics = {"date": "2026-08-09", "friend_farming_count": 27}

            def _record_friend_help_action(self):
                events.append("native-recorder")
                self._instance_metrics["1"]["friend_farming_count"] = 28
                self.gui_metrics["friend_farming_count"] = 28
                return "native-recorder-result"

            def process_friend_farm(self):
                events.append("native-process")
                return self._record_friend_help_action()

        def help_match(frame):
            if frame == "before-frame":
                return {"matched": True, "center": (210, 592)}
            return {"matched": False}

        self.namespace.update({
            "_qqfarm_capture_native_friend_help_frame": lambda _bot: next(captures),
            "_friend_guard_help_button_match": help_match,
            "_qqfarm_native_friend_help_card_signature": lambda _frame: ("friend", "A"),
            "_friend_help_visual_completion_proof": lambda *_args, **_kwargs: True,
            "_friend_guard_sleep": lambda _seconds: None,
            "_qqfarm_native_friend_help_durable_snapshot": lambda *_args, **_kwargs: 0,
            "_qqfarm_commit_native_friend_help_confirmation": (
                lambda context, **kwargs: commits.append((context, kwargs)) or 1
            ),
        })

        cache_wrapper = self.namespace["_wrap_native_v225_friend_help_candidate_cache"]
        recorder_wrapper = self.namespace["_wrap_native_v225_friend_help_confirmation"]
        FarmBotCV.process_friend_farm, cached = cache_wrapper(
            FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
        )
        FarmBotCV._record_friend_help_action, bridged = recorder_wrapper(
            FarmBotCV._record_friend_help_action, "FarmBotCV._record_friend_help_action"
        )
        self.assertTrue(cached)
        self.assertTrue(bridged)

        bot = FarmBotCV()
        self.assertEqual("native-recorder-result", bot.process_friend_farm())
        self.assertEqual(["native-process", "native-recorder"], events)
        self.assertEqual(1, len(commits))
        self.assertIs(bot, commits[0][0])
        self.assertTrue(commits[0][1]["confirmed"])
        self.assertEqual(0, commits[0][1]["durable_before"])
        self.assertEqual(28, bot._instance_metrics["1"]["friend_farming_count"])

    def test_missing_postproof_never_commits_a_native_runtime_increment(self):
        captures = iter(("before-frame", "after-frame"))
        commits = []

        class FarmBotCV:
            def _record_friend_help_action(self):
                return "native"

            def process_friend_farm(self):
                return self._record_friend_help_action()

        self.namespace.update({
            "_qqfarm_capture_native_friend_help_frame": lambda _bot: next(captures),
            "_friend_guard_help_button_match": lambda frame: (
                {"matched": True, "center": (210, 592)}
                if frame == "before-frame" else {"matched": True, "center": (210, 592)}
            ),
            "_qqfarm_native_friend_help_card_signature": lambda _frame: ("friend", "A"),
            "_friend_help_visual_completion_proof": lambda *_args, **_kwargs: True,
            "_friend_guard_sleep": lambda _seconds: None,
            "_qqfarm_native_friend_help_durable_snapshot": lambda *_args, **_kwargs: 0,
            "_qqfarm_commit_native_friend_help_confirmation": (
                lambda _context, **kwargs: commits.append(kwargs) or int(
                    kwargs.get("durable_before", 0)
                )
            ),
        })
        cache_wrapper = self.namespace["_wrap_native_v225_friend_help_candidate_cache"]
        recorder_wrapper = self.namespace["_wrap_native_v225_friend_help_confirmation"]
        FarmBotCV.process_friend_farm, _ = cache_wrapper(
            FarmBotCV.process_friend_farm, "FarmBotCV.process_friend_farm"
        )
        FarmBotCV._record_friend_help_action, _ = recorder_wrapper(
            FarmBotCV._record_friend_help_action, "FarmBotCV._record_friend_help_action"
        )

        self.assertEqual("native", FarmBotCV().process_friend_farm())
        self.assertEqual(1, len(commits))
        self.assertFalse(commits[0]["confirmed"])
        self.assertEqual(0, commits[0]["durable_before"])

    def test_native_owner_installs_only_the_two_narrow_bridge_wrappers(self):
        patch = self.namespace["_patch_native_v225_friend_help_confirmation_for_module"]
        self.namespace["_qqfarm_legacy_wrapper_allowed"] = lambda _label: False

        class FarmBotCV:
            def process_friend_farm(self):
                return "process"

            def _record_friend_help_action(self):
                return "record"

        module = types.SimpleNamespace(
            __name__="bot.application.flows", FarmBotCV=FarmBotCV
        )
        self.assertEqual(2, patch(module, "v434-test"))
        self.assertTrue(getattr(
            FarmBotCV.process_friend_farm,
            "__qqfarm_native_v225_friend_help_candidate_cache_wrapped__",
            False,
        ))
        self.assertTrue(getattr(
            FarmBotCV._record_friend_help_action,
            "__qqfarm_native_v225_friend_help_confirmation_wrapped__",
            False,
        ))
        self.assertEqual(0, patch(module, "v434-repeat"))

        self.namespace["_qqfarm_legacy_wrapper_allowed"] = lambda _label: True

        class LegacyFarmBotCV:
            def process_friend_farm(self):
                return "legacy-process"

            def _record_friend_help_action(self):
                return "legacy-record"

        legacy_module = types.SimpleNamespace(
            __name__="bot.application.flows", FarmBotCV=LegacyFarmBotCV
        )
        self.assertEqual(0, patch(legacy_module, "v434-legacy"))
        self.assertFalse(getattr(
            LegacyFarmBotCV.process_friend_farm,
            "__qqfarm_native_v225_friend_help_candidate_cache_wrapped__",
            False,
        ))


if __name__ == "__main__":
    unittest.main()
