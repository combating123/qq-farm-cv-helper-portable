import ast
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURES = ROOT / "tests" / "fixtures"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    assignments = {
        "_NATIVE_V225_TROUBLE_SEED_LAND_PATCH_LOG_SEEN",
        "_NATIVE_V225_TROUBLE_BUTTON_PATCH_LOG_SEEN",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in assignments
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    messages = []
    namespace = {
        "__name__": "v449_native_v225_trouble_seed_land",
        "cv2": cv2,
        "np": np,
        "_write": messages.append,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["_messages"] = messages
    return namespace


def read_fixture(name):
    data = np.fromfile(FIXTURES / name, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_UNCHANGED)


class NativeV225TroubleSeedLand20260810Tests(unittest.TestCase):
    def test_real_planted_friend_frames_have_visual_seed_land_candidates(self):
        namespace = load_functions("_collect_friend_seed_land_centers_from_frame")
        collect = namespace["_collect_friend_seed_land_centers_from_frame"]
        expected_minimums = {
            "live-v449-planted-friend-night-mixed-20260809.png": 3,
            "live-v449-planted-friend-day-mixed-20260809.png": 3,
            "live-v449-planted-friend-night-dense-20260808.png": 5,
        }

        observed = {
            name: len(collect(read_fixture(name)))
            for name in expected_minimums
        }

        for name, minimum in expected_minimums.items():
            self.assertGreaterEqual(observed[name], minimum, (name, observed))

    def test_native_loaded_patcher_installs_planted_land_fallback(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
            "_wrap_native_v225_trouble_seed_land_collector",
            "_patch_native_v225_trouble_seed_land_for_module",
            "_patch_native_v225_trouble_seed_land_loaded",
        )
        self.assertIn("_patch_native_v225_trouble_seed_land_loaded", namespace)

        calls = []

        def native_collect(frame):
            calls.append(frame)
            return []

        module = types.SimpleNamespace(
            _collect_friend_seed_land_centers=native_collect,
        )
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.application.native_trouble": module}
        )
        frame = read_fixture("live-v449-planted-friend-night-dense-20260808.png")

        changed = namespace["_patch_native_v225_trouble_seed_land_loaded"]("test")
        centers = module._collect_friend_seed_land_centers(frame)

        self.assertEqual(["bot.application.native_trouble:1"], changed)
        self.assertEqual([frame], calls)
        self.assertGreaterEqual(len(centers), 5)
        self.assertTrue(getattr(
            module._collect_friend_seed_land_centers,
            "__qqfarm_native_v225_trouble_seed_land_wrapped__",
            False,
        ))

    def test_native_fallback_rejects_blank_frame_even_if_template_claims_land(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
            "_wrap_native_v225_trouble_seed_land_collector",
        )
        self.assertIn("_wrap_native_v225_trouble_seed_land_collector", namespace)

        def native_collect(frame):
            return [(100, 500), (150, 520), (200, 540)]

        wrapped, changed = namespace["_wrap_native_v225_trouble_seed_land_collector"](
            native_collect,
            "bot.fixture._collect_friend_seed_land_centers",
        )
        blank = np.zeros((800, 428, 3), dtype=np.uint8)

        self.assertTrue(changed)
        self.assertEqual([], wrapped(blank))


    def test_native_loaded_patcher_installs_visible_trouble_button_fallback(self):
        namespace = load_functions(
            "_detect_friend_trouble_popup_action",
            "_wrap_troublemaker_button_picker",
            "_wrap_native_v225_trouble_button_picker",
            "_patch_native_v225_trouble_button_for_module",
            "_patch_native_v225_trouble_button_loaded",
        )
        self.assertIn("_patch_native_v225_trouble_button_loaded", namespace)

        calls = []

        def native_pick(owner, frame, roi):
            calls.append((owner, frame, roi))
            return None

        module = types.SimpleNamespace(_pick_friend_trouble_button=native_pick)
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.application.native_trouble": module}
        )
        frame = read_fixture("friend_trouble_popup_action_live_sanitized.png")
        owner = object()
        roi = (100, 400, 320, 560)

        changed = namespace["_patch_native_v225_trouble_button_loaded"]("test")
        result = module._pick_friend_trouble_button(owner, frame, roi)

        self.assertEqual(["bot.application.native_trouble:1"], changed)
        self.assertEqual([(owner, frame, roi)], calls)
        self.assertIsInstance(result, dict)
        self.assertIn("center", result)
        self.assertTrue(getattr(
            module._pick_friend_trouble_button,
            "__qqfarm_native_v225_trouble_button_wrapped__",
            False,
        ))

    def test_native_zero_result_runs_one_bounded_visual_seedland_fallback(self):
        namespace = load_functions(
            "_wrap_first_party_friend_troublemaker_entry",
        )
        events = []
        bot = types.SimpleNamespace(friend_trouble_daily_count=6)
        namespace.update({
            "_friend_guard_context": lambda args, kwargs: bot,
            "_enter_vip_entitlement_context": lambda *args: [],
            "_restore_vip_entitlement_context": lambda state: 0,
            "_friend_trouble_counter_snapshot": lambda context: context.friend_trouble_daily_count,
            "_get_frame_from_bot": lambda context: "fresh-friend-frame",
            "_run_first_party_friend_troublemaker": (
                lambda context, frame: events.append((context, frame)) or True
            ),
        })
        wrapped, changed = namespace["_wrap_first_party_friend_troublemaker_entry"](
            lambda context: False,
            "fixture._run_friend_daily_troublemaker",
        )
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot))
        self.assertEqual([(bot, "fresh-friend-frame")], events)


if __name__ == "__main__":
    unittest.main()
