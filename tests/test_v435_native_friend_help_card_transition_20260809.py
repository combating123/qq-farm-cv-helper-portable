import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


FUNCTIONS = (
    "_qqfarm_cache_native_v225_friend_help_candidate",
    "_wrap_native_v225_friend_help_candidate_cache",
    "_wrap_native_v225_friend_help_confirmation",
)


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
    namespace = {"__file__": str(HOOK), "__name__": "v435_card_transition_test"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class NativeFriendHelpCardTransition20260809Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(*FUNCTIONS)
        self.namespace["_write"] = lambda *_args, **_kwargs: None
        self.namespace["_friend_guard_sleep"] = lambda _seconds: None
        self.namespace["_qqfarm_native_friend_help_durable_snapshot"] = (
            lambda *_args, **_kwargs: 0
        )

    def _wrapped_bot(self, *, proof):
        events = []

        class FarmBotCV:
            def __init__(self):
                self.instance_id = "1"
                self.friend_help_daily_count = 0
                self._instance_metrics = {
                    "1": {"date": "2026-08-09", "friend_farming_count": 0}
                }
                self.gui_metrics = {"date": "2026-08-09", "friend_farming_count": 0}

            def _record_friend_help_action(self):
                # Mirrors the native v2.2.5 runtime-only counter mutation that
                # must not become durable without our fresh confirmation.
                events.append("native-recorder")
                self.friend_help_daily_count = 9
                self._instance_metrics["1"]["friend_farming_count"] = 9
                self.gui_metrics["friend_farming_count"] = 9
                return "native-recorder-result"

            def process_friend_farm(self):
                events.append("native-process")
                return self._record_friend_help_action()

        captures = iter(("before-frame", "after-frame"))
        self.namespace.update({
            "_qqfarm_capture_native_friend_help_frame": lambda _bot: next(captures),
            "_friend_guard_help_button_match": lambda frame: (
                {"matched": True, "center": (210, 592)}
                if frame == "before-frame" else {"matched": False}
            ),
            # A successful native click can atomically advance the selected
            # carousel card before the 200 ms fresh confirmation frame.
            "_qqfarm_native_friend_help_card_signature": lambda frame: (
                ("friend", "A") if frame == "before-frame" else ("friend", "B")
            ),
            "_friend_help_visual_completion_proof": (
                lambda *_args, **_kwargs: bool(proof)
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
        return FarmBotCV(), events

    def test_auto_advanced_selected_card_commits_when_button_is_gone_and_visual_completion_is_proven(self):
        """Live v434 evidence: post-click carousel A -> B is a valid success transition."""
        commits = []
        self.namespace["_qqfarm_commit_native_friend_help_confirmation"] = (
            lambda context, **kwargs: commits.append((context, kwargs)) or 1
        )
        bot, events = self._wrapped_bot(proof=True)

        self.assertEqual("native-recorder-result", bot.process_friend_farm())
        self.assertEqual(["native-process", "native-recorder"], events)
        self.assertEqual(1, len(commits))
        self.assertIs(bot, commits[0][0])
        self.assertTrue(commits[0][1]["confirmed"])
        self.assertEqual(0, commits[0][1]["durable_before"])

    def test_unproven_card_transition_does_not_leave_native_gui_count_visible(self):
        """A carousel change alone never authorizes either durable or GUI history."""
        commits = []
        self.namespace["_qqfarm_commit_native_friend_help_confirmation"] = (
            lambda _context, **kwargs: commits.append(kwargs) or int(
                kwargs.get("durable_before", 0)
            )
        )
        bot, _events = self._wrapped_bot(proof=False)

        self.assertEqual("native-recorder-result", bot.process_friend_farm())
        self.assertEqual(1, len(commits))
        self.assertFalse(commits[0]["confirmed"])
        self.assertEqual(0, commits[0]["durable_before"])
        self.assertEqual(0, bot.friend_help_daily_count)
        self.assertEqual(0, bot._instance_metrics["1"]["friend_farming_count"])
        self.assertEqual(0, bot.gui_metrics["friend_farming_count"])


if __name__ == "__main__":
    unittest.main()
