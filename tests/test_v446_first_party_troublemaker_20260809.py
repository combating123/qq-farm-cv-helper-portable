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
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__name__": "v446_first_party_troublemaker"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FirstPartyTroublemaker20260809Tests(unittest.TestCase):
    def test_deferred_sidecar_prefers_native_v225_batch_after_v447_cutover(self):
        namespace = load_functions("_run_deferred_friend_troublemaker")
        runner = namespace["_run_deferred_friend_troublemaker"]
        calls = []
        counts = iter((0, 1))
        frame = object()

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_troublemaker_ran = False
            friend_troublemaker_adjacent_retry_limit = 1
            _qqfarm_troublemaker_full_miss_until = 0.0

            def _run_friend_daily_troublemaker(self, _frame):
                calls.append("native-member-gated")
                return True

        scheduler = Scheduler()
        namespace.update({
            "_run_first_party_friend_troublemaker": (
                lambda context, current_frame: calls.append(
                    ("first-party-cv", context, current_frame)
                ) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_trouble_counter_snapshot": lambda _context: next(counts),

            "_write": lambda *_args, **_kwargs: None,
        })

        self.assertTrue(runner(scheduler, frame))
        self.assertEqual(
            ["native-member-gated"],
            calls,
            "v447 restores the complete native-runtime batch instead of repeated single-land clicks",
        )

    def test_first_party_cv_action_clicks_crop_then_verified_popup_action_and_records_once(self):
        namespace = load_functions("_run_first_party_friend_troublemaker")
        self.assertIn(
            "_run_first_party_friend_troublemaker",
            namespace,
            "the final CV-GUI product needs an independently owned troublemaker transaction",
        )
        runner = namespace["_run_first_party_friend_troublemaker"]
        initial_frame = types.SimpleNamespace(shape=(800, 428, 3))
        popup_frame = types.SimpleNamespace(shape=(800, 428, 3))
        settled_frame = types.SimpleNamespace(shape=(800, 428, 3))
        clicks = []
        records = []
        saves = []
        syncs = []
        captures = iter((popup_frame, settled_frame))

        class Scheduler:
            friend_trouble_daily_date = ""
            friend_trouble_daily_count = 0

            def _save_daily_counters(self):
                saves.append(self.friend_trouble_daily_count)
                return True

            def _record_friend_trouble_action(self, count):
                records.append(count)
                return True

        scheduler = Scheduler()

        def detect_popup(frame):
            if frame is popup_frame:
                return {"center": (260, 510), "source": "fixture-popup"}
            return None

        namespace.update({
            "_collect_friend_seed_land_centers_from_frame": (
                lambda frame: [(190, 610)] if frame is initial_frame else []
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda context, frame, match: clicks.append(
                    (context, frame, tuple(match["center"]))
                ) or True
            ),
            "_get_frame_from_bot": lambda _context: next(captures),
            "_detect_friend_trouble_popup_action": detect_popup,
            "_friend_guard_sleep": lambda _seconds: None,
            "_daily_business_date": lambda: "2026-08-09",
            "_friend_trouble_counter_snapshot": lambda _context: 0,
            "_daily_metrics_sync_runtime": (
                lambda context, **kwargs: syncs.append((context, kwargs)) or {
                    "friend_trouble_daily_count": context.friend_trouble_daily_count
                }
            ),
            "_write": lambda *_args, **_kwargs: None,
        })

        self.assertTrue(runner(scheduler, initial_frame))
        self.assertEqual(
            [
                (scheduler, initial_frame, (190, 610)),
                (scheduler, popup_frame, (260, 510)),
            ],
            clicks,
        )
        self.assertEqual([1], records)
        self.assertEqual([1], saves)
        self.assertEqual("2026-08-09", scheduler.friend_trouble_daily_date)
        self.assertEqual(1, scheduler.friend_trouble_daily_count)
        self.assertEqual(1, len(syncs))
        self.assertIs(scheduler, syncs[0][0])
        self.assertTrue(syncs[0][1]["force"])
        self.assertEqual("2026-08-09", syncs[0][1]["today"])
        self.assertEqual(
            ("friend_trouble_daily_count",),
            syncs[0][1]["exact_context_fields"],
        )


    def test_first_party_visual_fallback_records_one_delta_without_doubling_existing_count(self):
        namespace = load_functions("_run_first_party_friend_troublemaker")
        runner = namespace["_run_first_party_friend_troublemaker"]
        initial_frame = types.SimpleNamespace(shape=(800, 428, 3))
        popup_frame = types.SimpleNamespace(shape=(800, 428, 3))
        settled_frame = types.SimpleNamespace(shape=(800, 428, 3))
        captures = iter((popup_frame, settled_frame))
        records = []
        saves = []

        class Scheduler:
            friend_trouble_daily_date = "2026-08-11"
            friend_trouble_daily_count = 37

            def _record_friend_trouble_action(self, delta):
                records.append(delta)
                self.friend_trouble_daily_count += int(delta)
                return True

            def _save_daily_counters(self):
                saves.append(self.friend_trouble_daily_count)
                return True

        scheduler = Scheduler()
        namespace.update({
            "_collect_friend_seed_land_centers_from_frame": (
                lambda frame: [(190, 610)] if frame is initial_frame else []
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda *_args, **_kwargs: True
            ),
            "_get_frame_from_bot": lambda _context: next(captures),
            "_detect_friend_trouble_popup_action": (
                lambda frame: {"center": (260, 510)} if frame is popup_frame else None
            ),
            "_friend_guard_sleep": lambda _seconds: None,
            "_daily_business_date": lambda: "2026-08-11",
            "_friend_trouble_counter_snapshot": (
                lambda context: context.friend_trouble_daily_count
            ),
            "_daily_metrics_sync_runtime": lambda *_args, **_kwargs: {},
            "_write": lambda *_args, **_kwargs: None,
        })

        self.assertTrue(runner(scheduler, initial_frame))
        self.assertEqual([1], records)
        self.assertEqual(38, scheduler.friend_trouble_daily_count)
        self.assertTrue(all(value == 38 for value in saves))


    def test_narrow_entry_preserves_native_v225_transaction_owner(self):
        namespace = load_functions("_wrap_first_party_friend_troublemaker_entry")
        self.assertIn(
            "_wrap_first_party_friend_troublemaker_entry",
            namespace,
            "the loaded native entry needs a narrow first-party transaction wrapper",
        )
        wrapper = namespace["_wrap_first_party_friend_troublemaker_entry"]
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        native_calls = []
        first_party_calls = []

        def native_member_gate(self, current_frame):
            native_calls.append((self, current_frame))
            return "native-v225-batch"

        namespace["_run_first_party_friend_troublemaker"] = (
            lambda context, current_frame: first_party_calls.append(
                (context, current_frame)
            ) or True
        )
        wrapped, changed = wrapper(native_member_gate, "fixture._run_friend_daily_troublemaker")

        class Scheduler:
            _run_friend_daily_troublemaker = wrapped

        scheduler = Scheduler()
        self.assertTrue(changed)
        self.assertEqual(
            "native-v225-batch",
            scheduler._run_friend_daily_troublemaker(frame),
        )
        self.assertEqual([], first_party_calls)
        self.assertEqual([(scheduler, frame)], native_calls)


    def test_narrow_loaded_patcher_runs_while_native_v225_owns_other_business_paths(self):
        namespace = load_functions(
            "_wrap_first_party_friend_troublemaker_entry",
            "_patch_first_party_friend_troublemaker_loaded",
        )
        self.assertIn("_patch_first_party_friend_troublemaker_loaded", namespace)
        native_calls = []

        class FarmBotCV:
            def _run_friend_daily_troublemaker(self, frame):
                native_calls.append((self, frame))
                return False

        original = FarmBotCV.__dict__["_run_friend_daily_troublemaker"]
        module = types.ModuleType("bot.fixture_troublemaker")
        module.FarmBotCV = FarmBotCV
        namespace.update({
            "sys": types.SimpleNamespace(modules={module.__name__: module}),
            "_FIRST_PARTY_TROUBLEMAKER_PATCH_LOG_SEEN": set(),
            "_write": lambda *_args, **_kwargs: None,
        })

        changed = namespace["_patch_first_party_friend_troublemaker_loaded"]("fixture")

        self.assertTrue(changed)
        self.assertIsNot(
            original,
            FarmBotCV.__dict__["_run_friend_daily_troublemaker"],
        )
        self.assertTrue(
            getattr(
                FarmBotCV.__dict__["_run_friend_daily_troublemaker"],
                "__qqfarm_first_party_troublemaker_wrapped__",
                False,
            )
        )


if __name__ == "__main__":
    unittest.main()
