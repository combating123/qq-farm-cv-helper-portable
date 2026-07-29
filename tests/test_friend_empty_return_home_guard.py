import ast
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_function(name):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if not nodes:
        return None
    module = ast.Module(body=[nodes[0]], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace[name]


def load_friend_ui_namespace():
    namespace = load_functions(
        "_friend_guard_read_template",
        "_friend_guard_match_template",
        "_friend_guard_help_button_match",
        "_friend_guard_friend_ui_state",
    )
    namespace["_FRIEND_GUARD_TEMPLATE_CACHE"] = {}
    namespace["_FRIEND_HOME_TEMPLATE_PATH"] = str(
        FIXTURES / "friend_home_button.png"
    )
    namespace["_FRIEND_LIST_TEMPLATE_PATH"] = str(
        FIXTURES / "friend_list_tabs.png"
    )
    namespace["_FRIEND_HELP_ALL_TEMPLATE_PATH"] = str(
        ROOT / "portable" / "friend_help_all_button.png"
    )
    return namespace


class FriendEmptyReturnHomeGuardTests(unittest.TestCase):
    def test_two_distinct_fast_empty_rounds_trigger_return_home(self):
        decide = load_function("_friend_empty_guard_next")
        self.assertIsNotNone(decide)
        count, trigger = decide(0, 0.08, 100.0, 0.0)
        self.assertEqual((1, False), (count, trigger))
        count, trigger = decide(count, 0.06, 116.0, 100.0)
        self.assertEqual((2, True), (count, trigger))

    def test_nested_completion_in_same_round_is_not_counted_twice(self):
        decide = load_function("_friend_empty_guard_next")
        self.assertIsNotNone(decide)
        count, trigger = decide(1, 0.05, 100.4, 100.0)
        self.assertEqual((1, False), (count, trigger))

    def test_long_friend_work_resets_empty_counter(self):
        decide = load_function("_friend_empty_guard_next")
        self.assertIsNotNone(decide)
        count, trigger = decide(1, 8.0, 120.0, 100.0)
        self.assertEqual((0, False), (count, trigger))


    def test_guard_context_accepts_scheduler_object_without_go_home_method(self):
        namespace = load_functions("_friend_guard_context")
        context = type("Scheduler", (), {})()
        found = namespace["_friend_guard_context"]((context,), {})
        self.assertIs(context, found)

    def test_resolver_follows_wrapper_chain_and_prefers_process_self_farm(self):
        namespace = load_functions("_friend_guard_context", "_friend_guard_original_chain", "_resolve_friend_guard_self_action", "_resolve_friend_guard_action")
        calls = []
        context = type("Scheduler", (), {})()

        def process_self_farm(bot):
            calls.append(bot)
            return "home-ok"

        def original():
            return None

        original.__globals__["process_self_farm"] = process_self_farm

        def wrapped():
            return None

        wrapped.__qqfarm_vip_business_orig__ = original
        action, target, label = namespace["_resolve_friend_guard_action"](wrapped, (context,), {})
        original.__globals__.pop("process_self_farm", None)
        self.assertIs(action, process_self_farm)
        self.assertIs(target, context)
        self.assertEqual("global.process_self_farm", label)

    def test_resolver_prefers_bound_go_home_before_self_farm_actions(self):
        namespace = load_functions("_friend_guard_context", "_friend_guard_original_chain", "_resolve_friend_guard_self_action", "_resolve_friend_guard_action")

        class Scheduler:
            def go_home(self, game_frame):
                return "go-home"

            def process_self_farm(self, game_frame):
                return "self-farm"

        context = Scheduler()
        action, target, label = namespace["_resolve_friend_guard_action"](lambda: None, (context, object()), {})
        self.assertIs(action.__self__, context)
        self.assertEqual(context.go_home.__func__, action.__func__)
        self.assertIsNone(target)
        self.assertEqual("method.go_home", label)

    def test_resolver_prefers_global_go_home_before_bound_process_self_farm(self):
        namespace = load_functions("_friend_guard_context", "_friend_guard_original_chain", "_resolve_friend_guard_self_action", "_resolve_friend_guard_action")
        context = type("Scheduler", (), {"process_self_farm": lambda self, frame: "self-farm"})()

        def go_home(bot, game_frame):
            return "go-home"

        def original():
            return None

        original.__globals__["go_home"] = go_home
        action, target, label = namespace["_resolve_friend_guard_action"](original, (context, object()), {})
        original.__globals__.pop("go_home", None)
        self.assertIs(action, go_home)
        self.assertIs(target, context)
        self.assertEqual("global.go_home", label)

    def test_resolver_prefers_go_home_icon_handler_before_self_farm_fallback(self):
        namespace = load_functions("_friend_guard_context", "_friend_guard_original_chain", "_resolve_friend_guard_self_action", "_resolve_friend_guard_action")

        class Scheduler:
            def check_go_home_icon(self, game_frame):
                return "clicked-home"

            def process_self_farm(self, game_frame):
                return "self-farm"

        context = Scheduler()
        action, target, label = namespace["_resolve_friend_guard_action"](lambda: None, (context, object()), {})
        self.assertIs(action.__self__, context)
        self.assertEqual(context.check_go_home_icon.__func__, action.__func__)
        self.assertIsNone(target)
        self.assertEqual("method.check_go_home_icon", label)

    def test_self_fallback_resolver_selects_process_self_farm(self):
        namespace = load_functions("_friend_guard_context", "_friend_guard_original_chain", "_resolve_friend_guard_self_action")

        class Scheduler:
            def process_self_farm(self, game_frame):
                return "self-farm"

        context = Scheduler()
        action, target, label = namespace["_resolve_friend_guard_self_action"](lambda: None, (context, object()), {})
        self.assertIs(action.__self__, context)
        self.assertEqual(context.process_self_farm.__func__, action.__func__)
        self.assertIsNone(target)
        self.assertEqual("method.process_self_farm", label)

    def test_guard_falls_back_to_self_farm_when_home_icon_handler_reports_absent(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("friend route recovery direct action absent", source)
        self.assertIn("_resolve_friend_guard_self_action(fn, args, kwargs)", source)

    def test_fresh_frame_replaces_stale_bound_method_frame(self):
        namespace = load_functions("_friend_guard_args_with_frame")
        context = object()
        stale_frame = object()
        fresh_frame = object()
        call_args, call_kwargs = namespace["_friend_guard_args_with_frame"](
            context, (context, stale_frame), {}, fresh_frame
        )
        self.assertEqual((context, fresh_frame), call_args)
        self.assertEqual({}, call_kwargs)

    def test_guard_refreshes_frame_before_checking_home_icon(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("friend route recovery fresh frame", source)
        self.assertIn("_get_frame_from_bot(context)", source)
        self.assertIn("_friend_guard_args_with_frame(context, args, kwargs, fresh_frame)", source)

    def test_relaxed_home_check_temporarily_lowers_and_restores_threshold(self):
        namespace = load_functions("_invoke_friend_guard_action", "_invoke_friend_guard_relaxed_home_check")
        seen = []

        class Scheduler:
            go_home_frame_threshold = 0.70

            def check_go_home_icon(self, game_frame):
                seen.append(self.go_home_frame_threshold)
                return True

        context = Scheduler()
        frame = object()
        result = namespace["_invoke_friend_guard_relaxed_home_check"](
            context.check_go_home_icon, None, context, (context, frame), {}
        )
        self.assertTrue(result)
        self.assertEqual([0.52], seen)
        self.assertEqual(0.70, context.go_home_frame_threshold)

    def test_guard_uses_relaxed_home_template_before_self_farm_fallback(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        relaxed_pos = source.index("friend route recovery relaxed home result")
        fallback_pos = source.index("friend route recovery fallback result")
        self.assertLess(relaxed_pos, fallback_pos)
        self.assertIn("_last_friend_farm_go_home_present", source)


    def test_friend_ui_state_uses_template_matcher(self):
        namespace = load_friend_ui_namespace()
        self.assertIn("_friend_guard_read_template", namespace)
        self.assertIn("_friend_guard_match_template", namespace)

    def test_friend_ui_state_detects_home_button_template_in_bgr_frame(self):
        namespace = load_friend_ui_namespace()
        state = namespace["_friend_guard_friend_ui_state"]
        import numpy as np
        from PIL import Image
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[:, :, :] = (110, 185, 125)
        template_rgb = np.asarray(
            Image.open(FIXTURES / "friend_home_button.png").convert("RGB")
        )
        template_bgr = template_rgb[:, :, ::-1]
        h, w = template_bgr.shape[:2]
        frame[570:570 + h, 360:360 + w, :] = template_bgr
        self.assertTrue(state(frame))

    def test_friend_ui_state_accepts_live_home_button_with_soft_edge_when_help_visible(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_home_low_edge_live.png"))
        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_ui_state_accepts_runtime_blurred_home_button(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_home_runtime_blurred.png"))
        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_ui_state_accepts_live_home_button_with_very_soft_edge(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_home_very_soft_edge_live.png"))
        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_ui_state_accepts_soft_edge_home_without_help_button(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_home_soft_edge_steal_live.png"))
        self.assertIsNotNone(frame)
        self.assertFalse(namespace["_friend_guard_help_button_match"](frame)["matched"])
        self.assertTrue(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_ui_state_accepts_current_live_friend_page(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_farm_current_live_sanitized.png"))
        self.assertIsNotNone(frame)
        self.assertTrue(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_help_button_matches_current_live_friend_page(self):
        namespace = load_friend_ui_namespace()
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_farm_current_live_sanitized.png"))
        self.assertIsNotNone(frame)
        match = namespace["_friend_guard_help_button_match"](frame)
        self.assertTrue(match["matched"], match)
        self.assertEqual((213, 597), match["center"])

    def test_friend_ui_state_does_not_use_help_button_without_home_evidence(self):
        namespace = load_friend_ui_namespace()
        import numpy as np
        from PIL import Image
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[:, :, :] = (105, 190, 135)
        template_rgb = np.asarray(
            Image.open(ROOT / "portable" / "friend_help_all_button.png").convert("RGB")
        )
        template_bgr = template_rgb[:, :, ::-1]
        h, w = template_bgr.shape[:2]
        frame[560:560 + h, 180:180 + w, :] = template_bgr
        self.assertFalse(namespace["_friend_guard_friend_ui_state"](frame))

    def test_friend_ui_state_returns_unknown_for_friend_list_panel(self):
        namespace = load_friend_ui_namespace()
        state = namespace["_friend_guard_friend_ui_state"]
        import numpy as np
        from PIL import Image
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[:, :, :] = (110, 185, 125)
        template_rgb = np.asarray(
            Image.open(FIXTURES / "friend_list_tabs.png").convert("RGB")
        )
        template_bgr = template_rgb[:, :, ::-1]
        h, w = template_bgr.shape[:2]
        frame[110:110 + h, 0:w, :] = template_bgr
        self.assertIsNone(state(frame))

    def test_friend_ui_state_rejects_green_self_farm_footer(self):
        namespace = load_friend_ui_namespace()
        state = namespace["_friend_guard_friend_ui_state"]
        import numpy as np
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[:, :, :] = (105, 190, 135)
        self.assertFalse(state(frame))

    def test_friend_ui_state_rejects_warm_gold_fields_without_home_button(self):
        namespace = load_friend_ui_namespace()
        state = namespace["_friend_guard_friend_ui_state"]
        import numpy as np
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        frame[:, :, :] = (105, 190, 135)
        frame[650:800, :, :] = (80, 185, 225)
        frame[560:672, 350:426, :] = (125, 180, 190)
        self.assertFalse(state(frame))

    def test_scaled_client_point_maps_virtual_frame_to_physical_window(self):
        scale = load_function("_friend_guard_scale_point_to_client")
        self.assertIsNotNone(scale)
        self.assertEqual((593, 911), scale(394, 607, 428, 801, 644, 1202))

    def test_coordinate_home_uses_template_center_and_passes_frame_dimensions(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []
        namespace["_friend_guard_friend_ui_state"] = lambda frame: True
        namespace["_FRIEND_HOME_LAST_MATCH"] = {
            "matched": True, "center": (390, 610)
        }
        namespace["_friend_guard_post_client_click"] = (
            lambda x, y, w, h: calls.append(("client", x, y, w, h)) or True
        )
        namespace["_friend_guard_frame_to_screen"] = (
            lambda x, y, w, h: calls.append(("screen-map", x, y, w, h))
            or (700, 1200)
        )

        class Frame:
            shape = (801, 428, 3)

        class Scheduler:
            def click_at_position(self, x, y):
                calls.append(("screen-click", x, y))
                return True

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )

        self.assertTrue(result)
        self.assertEqual([("client", 390, 610, 428, 801)], calls)

    def test_coordinate_home_fallback_uses_visual_friend_state_when_marker_is_missing(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []
        namespace["_friend_guard_friend_ui_state"] = lambda frame: True
        namespace["_friend_guard_frame_to_screen"] = lambda x, y: (x, y)

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            def click_at_position(self, x, y):
                calls.append((x, y))
                return True

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertTrue(result)
        self.assertEqual([(394, 624)], calls)

    def test_coordinate_home_fallback_does_not_click_verified_self_farm_frame(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []
        namespace["_friend_guard_friend_ui_state"] = lambda frame: False

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def click_at_position(self, x, y):
                calls.append((x, y))
                return True

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertFalse(result)
        self.assertEqual([], calls)

    def test_coordinate_home_fallback_clicks_expected_frame_ratio(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def convert_to_screen_coordinate(self, x, y):
                calls.append(("convert", x, y))
                return x + 100, y + 200

            def click_at_position(self, x, y):
                calls.append(("click", x, y))

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertTrue(result)
        self.assertEqual(("convert", 394, 624), calls[0])
        self.assertEqual(("click", 494, 824), calls[1])

    def test_coordinate_home_client_click_does_not_emit_duplicate_absolute_click(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []
        namespace["_friend_guard_post_client_click"] = (
            lambda x, y: calls.append(("client", x, y)) or True
        )
        namespace["_friend_guard_frame_to_screen"] = (
            lambda x, y: (x + 100, y + 200)
        )

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def convert_to_screen_coordinate(self, x, y):
                calls.append(("convert", x, y))
                return x + 100, y + 200

            def click_at_position(self, x, y):
                calls.append(("screen", x, y))

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertTrue(result)
        self.assertEqual([("client", 394, 624)], calls)

    def test_coordinate_home_absolute_fallback_rejects_point_covered_by_other_window(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        clicks = []
        namespace.update({
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_post_client_click": lambda *args: False,
            "_friend_guard_frame_to_screen": lambda *args: (700, 1200),
            "_friend_guard_screen_point_owned_by_farm": lambda x, y: False,
        })

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            def click_at_position(self, x, y):
                clicks.append((x, y))
                return True

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )

        self.assertFalse(result)
        self.assertEqual([], clicks)

    def test_coordinate_home_fallback_supports_tuple_only_methods(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def convert_to_screen_coordinate(self, point):
                calls.append(("convert", point))
                return point[0] + 10, point[1] + 20

            def click_at_position(self, point):
                calls.append(("click", point))

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertTrue(result)
        self.assertEqual(("convert", (394, 624)), calls[0])
        self.assertEqual(("click", (404, 644)), calls[1])

    def test_coordinate_home_fallback_uses_window_origin_when_conversion_fails(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")
        calls = []
        namespace["_friend_guard_frame_to_screen"] = (
            lambda x, y: (x + 1745, y + 266)
        )

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def convert_to_screen_coordinate(self, *args):
                raise RuntimeError("conversion unavailable")

            def click_at_position(self, x, y):
                calls.append((x, y))

        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            Scheduler(), Frame()
        )
        self.assertTrue(result)
        self.assertEqual([(2139, 890)], calls)

    def test_coordinate_home_fallback_keeps_friend_marker_until_transition_is_verified(self):
        namespace = load_functions("_invoke_friend_guard_home_coordinate_click")

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            _last_friend_farm_go_home_present = True

            def click_at_position(self, x, y):
                return True

        scheduler = Scheduler()
        result = namespace["_invoke_friend_guard_home_coordinate_click"](
            scheduler, Frame()
        )
        self.assertTrue(result)
        self.assertTrue(scheduler._last_friend_farm_go_home_present)

    def test_post_click_self_refreshes_frame_and_runs_self_farm(self):
        namespace = load_functions(
            "_friend_guard_args_with_frame",
            "_invoke_friend_guard_action",
            "_invoke_friend_guard_post_click_self",
        )
        calls = []
        fresh_frame = object()
        namespace["_get_frame_from_bot"] = lambda context: fresh_frame
        namespace["_friend_guard_friend_ui_state"] = lambda frame: False
        namespace["_resolve_friend_guard_self_action"] = (
            lambda fn, args, kwargs: (
                args[0].process_self_farm,
                None,
                "method.process_self_farm",
            )
        )

        class Scheduler:
            def process_self_farm(self, game_frame):
                calls.append(game_frame)
                return "self-ok"

        scheduler = Scheduler()
        result, label = namespace["_invoke_friend_guard_post_click_self"](
            lambda: None, scheduler, (scheduler, object()), {}
        )
        self.assertEqual("self-ok", result)
        self.assertEqual("method.process_self_farm", label)
        self.assertEqual([fresh_frame], calls)

    def test_post_click_self_rejects_false_success_while_friend_ui_remains(self):
        namespace = load_functions(
            "_friend_guard_args_with_frame",
            "_invoke_friend_guard_action",
            "_invoke_friend_guard_post_click_self",
        )
        calls = []
        friend_frame = object()
        namespace["_get_frame_from_bot"] = lambda context: friend_frame
        namespace["_friend_guard_friend_ui_state"] = lambda frame: True
        namespace["_resolve_friend_guard_self_action"] = (
            lambda fn, args, kwargs: (
                args[0].process_self_farm,
                None,
                "method.process_self_farm",
            )
        )

        class Scheduler:
            _last_friend_farm_go_home_present = False

            def process_self_farm(self, game_frame):
                calls.append(game_frame)
                return True

        scheduler = Scheduler()
        result, label = namespace["_invoke_friend_guard_post_click_self"](
            lambda: None, scheduler, (scheduler, object()), {}
        )
        self.assertFalse(result)
        self.assertEqual("friend-ui-still-visible", label)
        self.assertEqual([], calls)
        self.assertTrue(scheduler._last_friend_farm_go_home_present)

    def test_guard_rearms_after_unconfirmed_home_click_instead_of_false_success(self):
        namespace = load_functions("_apply_friend_empty_return_home_guard")

        class Clock:
            @staticmethod
            def time():
                return 116.0

        class Scheduler:
            _qqfarm_friend_fast_empty_count = 1
            _qqfarm_friend_fast_empty_ts = 100.0
            _last_friend_farm_go_home_present = True

            def check_go_home_icon(self, game_frame):
                return False

            def process_self_farm(self, game_frame):
                return True

        scheduler = Scheduler()
        namespace.update({
            "time": Clock,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_empty_guard_next": lambda old, elapsed, now, last: (2, True),
            "_resolve_friend_guard_action": lambda fn, args, kwargs: (
                scheduler.check_go_home_icon, None, "method.check_go_home_icon"
            ),
            "_get_frame_from_bot": lambda context: object(),
            "_friend_guard_args_with_frame": lambda context, args, kwargs, frame: (args, kwargs),
            "_invoke_friend_guard_action": lambda action, target, args, kwargs: action(args[1]),
            "_invoke_friend_guard_relaxed_home_check": lambda *args, **kwargs: False,
            "_invoke_friend_guard_home_coordinate_click": lambda context, frame: True,
            "_invoke_friend_guard_post_click_self": lambda *args, **kwargs: (
                False, "friend-ui-still-visible"
            ),
            "_resolve_friend_guard_self_action": lambda *args, **kwargs: (
                scheduler.process_self_farm, None, "method.process_self_farm"
            ),
            "_friend_route_state_summary": lambda context: "state",
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = namespace["_apply_friend_empty_return_home_guard"](
            lambda *args, **kwargs: None,
            (scheduler, object()),
            {},
            0.5,
            "process_friend_farm",
        )
        self.assertFalse(result)
        self.assertEqual(1, scheduler._qqfarm_friend_fast_empty_count)
        self.assertEqual(116.0, scheduler._qqfarm_friend_fast_empty_ts)

    def test_guard_uses_coordinate_home_fallback_before_self_farm_fallback(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        relaxed_pos = source.index("friend route recovery relaxed home result")
        coordinate_pos = source.index("friend route recovery coordinate home result")
        fallback_pos = source.index("friend route recovery fallback result")
        self.assertLess(relaxed_pos, coordinate_pos)
        self.assertLess(coordinate_pos, fallback_pos)
        self.assertIn("_invoke_friend_guard_home_coordinate_click(context, fresh_frame)", source)

    def test_action_invoker_passes_original_frame_to_bound_self_farm_method(self):
        namespace = load_functions("_invoke_friend_guard_action")
        calls = []
        frame = object()

        class Scheduler:
            def process_self_farm(self, game_frame):
                calls.append(game_frame)
                return "home-ok"

        context = Scheduler()
        result = namespace["_invoke_friend_guard_action"](
            context.process_self_farm, None, (context, frame), {}
        )
        self.assertEqual("home-ok", result)
        self.assertEqual([frame], calls)

    def test_action_invoker_preserves_bot_and_frame_for_module_function(self):
        namespace = load_functions("_invoke_friend_guard_action")
        calls = []
        context = object()
        frame = object()

        def process_self_farm(bot, game_frame):
            calls.append((bot, game_frame))
            return "home-ok"

        result = namespace["_invoke_friend_guard_action"](
            process_self_farm, context, (context, frame), {}
        )
        self.assertEqual("home-ok", result)
        self.assertEqual([(context, frame)], calls)


    def test_route_state_summary_reports_friend_and_mode_fields(self):
        namespace = load_functions("_friend_route_state_summary")

        class Scheduler:
            friend_farm = True
            current_mode = "friend"
            unrelated = 42

            def process_self_farm(self):
                return True

        summary = namespace["_friend_route_state_summary"](Scheduler())
        self.assertIn("friend_farm=True", summary)
        self.assertIn("current_mode='friend'", summary)
        self.assertNotIn("unrelated", summary)



    def test_mark_friend_cycle_seen_records_scheduler_context(self):
        namespace = load_functions("_friend_guard_context", "_mark_friend_cycle_seen")
        self.assertIn("_mark_friend_cycle_seen", namespace)

        class Scheduler:
            pass

        scheduler = Scheduler()
        found = namespace["_mark_friend_cycle_seen"]((scheduler, object()), {})
        self.assertIs(scheduler, found)
        self.assertTrue(scheduler._qqfarm_friend_cycle_seen)

    def test_friend_action_probe_prioritizes_one_click_steal_before_help(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_actions_before_home",
        )
        self.assertIn("_invoke_friend_actions_before_home", namespace)
        frame = object()
        calls = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                calls.append(("steal", game_frame))
                return True

            def check_help_all_entry(self, game_frame):
                calls.append(("help", game_frame))
                return True

        scheduler = Scheduler()
        namespace["_write"] = lambda message: None
        acted, label = namespace["_invoke_friend_actions_before_home"](
            scheduler, frame
        )
        self.assertTrue(acted)
        self.assertEqual("method.check_steal_all_icon", label)
        self.assertEqual([("steal", frame)], calls)

    def test_friend_action_probe_falls_through_to_one_click_help(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_actions_before_home",
        )
        self.assertIn("_invoke_friend_actions_before_home", namespace)
        frame = object()
        calls = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                calls.append(("steal", game_frame))
                return False

            def check_help_all_entry(self, game_frame):
                calls.append(("help", game_frame))
                return True

        scheduler = Scheduler()
        namespace["_write"] = lambda message: None
        acted, label = namespace["_invoke_friend_actions_before_home"](
            scheduler, frame
        )
        self.assertTrue(acted)
        self.assertEqual("method.check_help_all_entry", label)
        self.assertEqual([("steal", frame), ("help", frame)], calls)

    def test_friend_action_probe_uses_visual_help_fallback_after_native_miss(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_visual_actions_before_home",
            "_invoke_friend_actions_before_home",
        )
        frame = object()
        calls = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                return False

            def check_help_all_entry(self, game_frame):
                return False

        scheduler = Scheduler()
        namespace.update({
            "_invoke_friend_guard_help_visual_click": (
                lambda context, value: calls.append(value) or True
            ),
            "_write": lambda message: None,
        })
        acted, label = namespace["_invoke_friend_actions_before_home"](
            scheduler, frame
        )
        self.assertTrue(acted)
        self.assertEqual("visual.friend_help_all", label)
        self.assertEqual([frame], calls)

    def test_guard_dog_visual_help_blocks_before_click_when_gate_rejects(self):
        namespace = load_functions("_invoke_friend_guard_help_visual_click")
        frame = object()
        clicks = []
        namespace.update({
            "_friend_guard_help_button_match": (
                lambda value: {"matched": True, "center": (213, 597)}
            ),
            "_friend_guard_help_action_allowed": (
                lambda context, value, center: False
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda *args: clicks.append(args) or True
            ),
            "_write": lambda message: None,
        })

        class Scheduler:
            pass

        scheduler = Scheduler()
        result = namespace["_invoke_friend_guard_help_visual_click"](
            scheduler, frame
        )

        self.assertFalse(result)
        self.assertEqual([], clicks)
        self.assertTrue(
            getattr(scheduler, "_qqfarm_guard_dog_help_skipped", False)
        )

    def test_friend_guard_list_prequalified_entry_allows_help_without_native_predicate(self):
        namespace = load_functions("_friend_guard_help_action_allowed")
        gate = namespace["_friend_guard_help_action_allowed"]
        resolver_calls = []
        context = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_resolve_friend_guard_native_callable": (
                lambda *args: resolver_calls.append(args) or (None, "")
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(gate(context, object(), (213, 597)))
        self.assertEqual([], resolver_calls)

    def test_runtime_log_marks_friend_guard_list_entry_prequalified(self):
        namespace = load_functions("_note_runtime_cycle_branch")
        context = types.SimpleNamespace()
        namespace.update({
            "_ACTIVE_RUN_CYCLE_CONTEXT": context,
            "_friend_watchdog_now": lambda: 123.5,
        })

        result = namespace["_note_runtime_cycle_branch"](
            "护主犬筛选：可帮忙务农 命中好友护主列表，允许进入帮忙"
        )

        self.assertEqual("friend-guard-prequalified", result)
        self.assertTrue(context._qqfarm_guard_list_prequalified)
        self.assertEqual(123.5, context._qqfarm_guard_list_prequalified_ts)
    def test_friend_guard_list_prequalification_expires_after_bounded_window(self):
        namespace = load_functions("_friend_guard_list_prequalified_entry_active")
        active = namespace.get("_friend_guard_list_prequalified_entry_active")
        if active is None:
            self.fail("_friend_guard_list_prequalified_entry_active is missing")
        context = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )

        self.assertTrue(active(context, now_ts=150.0, max_age_seconds=60.0))
        self.assertFalse(active(context, now_ts=161.0, max_age_seconds=60.0))

    def test_friend_guard_prequalification_reset_clears_previous_cycle(self):
        namespace = load_functions("_friend_guard_clear_prequalification")
        clear = namespace.get("_friend_guard_clear_prequalification")
        if clear is None:
            self.fail("_friend_guard_clear_prequalification is missing")
        context = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )

        self.assertTrue(clear(context))
        self.assertFalse(context._qqfarm_guard_list_prequalified)
        self.assertEqual(0.0, context._qqfarm_guard_list_prequalified_ts)
    def test_guard_dog_help_gate_uses_native_bottom_predicate(self):
        namespace = load_functions("_friend_guard_help_action_allowed")
        gate = namespace.get("_friend_guard_help_action_allowed")
        if gate is None:
            self.fail("_friend_guard_help_action_allowed is missing")
        calls = []
        frame = object()
        context = object()

        def predicate(bot, game_frame, center, label):
            calls.append((bot, game_frame, center, label))
            return False

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_resolve_friend_guard_native_callable": (
                lambda bot, name: (predicate, "checks_friend." + name)
            ),
            "_write": lambda message: None,
        })

        allowed = gate(context, frame, (213, 597))

        self.assertFalse(allowed)
        self.assertEqual(
            [(context, frame, (213, 597), "visual.friend_help_all")],
            calls,
        )

    def test_guard_dog_help_gate_allows_help_when_filter_is_disabled(self):
        namespace = load_functions("_friend_guard_help_action_allowed")
        gate = namespace.get("_friend_guard_help_action_allowed")
        if gate is None:
            self.fail("_friend_guard_help_action_allowed is missing")
        resolver_calls = []
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: False,
            "_resolve_friend_guard_native_callable": (
                lambda *args: resolver_calls.append(args) or (None, "")
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(gate(object(), object(), (213, 597)))
        self.assertEqual([], resolver_calls)

    def test_avatar_badge_verified_row_allows_help_without_native_predicate(self):
        namespace = load_functions("_friend_guard_help_action_allowed")
        gate = namespace["_friend_guard_help_action_allowed"]
        resolver_calls = []
        context = types.SimpleNamespace(
            _qqfarm_guard_row_verified=True,
            _qqfarm_guard_row_verified_ts=100.0,
        )
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_guard_verified_entry_active": lambda owner: True,
            "_resolve_friend_guard_native_callable": (
                lambda *args: resolver_calls.append(args) or (None, "")
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(gate(context, object(), (213, 597)))
        self.assertEqual([], resolver_calls)

    def test_friend_guard_verified_entry_expires_after_bounded_window(self):
        active = load_function("_friend_guard_verified_entry_active")
        self.assertIsNotNone(active)
        context = types.SimpleNamespace(
            _qqfarm_guard_row_verified=True,
            _qqfarm_guard_row_verified_ts=100.0,
        )
        active.__globals__.update({"_friend_watchdog_now": lambda: 190.0})

        self.assertTrue(active(context, now_ts=150.0, max_age_seconds=60.0))
        self.assertFalse(active(context, now_ts=161.0, max_age_seconds=60.0))

    def test_guard_dog_native_resolver_finds_predicate_from_check_method_globals(self):
        namespace = load_functions("_resolve_friend_guard_native_callable")
        resolver = namespace.get("_resolve_friend_guard_native_callable")
        if resolver is None:
            self.fail("_resolve_friend_guard_native_callable is missing")

        def predicate(bot, frame, center, label):
            return True

        method_globals = {"_has_guard_dog_for_bottom_help_action": predicate}
        method_code = (lambda self, frame: None).__code__
        check_method = types.FunctionType(method_code, method_globals)

        class Scheduler:
            check_friend_farm_bottom_help_all_entry = check_method

        found, source = resolver(
            Scheduler(), "_has_guard_dog_for_bottom_help_action"
        )

        self.assertIs(predicate, found)
        self.assertIn("check_friend_farm_bottom_help_all_entry", source)

    def test_visual_friend_help_stops_at_durable_daily_quota(self):
        namespace = load_functions("_invoke_friend_guard_help_visual_click")
        clicks = []
        logs = []
        frame = object()
        namespace.update({
            "_friend_help_counter_snapshot": lambda context: 500,
            "_friend_guard_help_button_match": (
                lambda candidate: {"matched": True, "center": (213, 597)}
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda context, candidate, match: clicks.append(match) or True
            ),
            "_friend_guard_sleep": lambda seconds: None,
            "_get_frame_from_bot": lambda context: frame,
            "_write": lambda message: logs.append(message),
        })
        scheduler = types.SimpleNamespace(friend_help_daily_limit=500)

        result = namespace["_invoke_friend_guard_help_visual_click"](
            scheduler, frame
        )

        self.assertFalse(result)
        self.assertEqual([], clicks)
        self.assertTrue(scheduler._qqfarm_friend_help_quota_exhausted)
        self.assertTrue(any("daily quota exhausted" in message for message in logs))

    def test_help_visual_click_verifies_button_disappears_after_click(self):
        namespace = load_functions("_invoke_friend_guard_help_visual_click")
        self.assertIn("_invoke_friend_guard_help_visual_click", namespace)
        frame = object()
        after = object()
        visible = {"matched": True, "center": (212, 598)}
        gone = {"matched": False, "center": None}
        matches = []
        clicks = []
        sleeps = []
        namespace.update({
            "_friend_guard_help_button_match": (
                lambda value: matches.append(value) or (visible if value is frame else gone)
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda context, value, found: clicks.append((value, found)) or True
            ),
            "_get_frame_from_bot": lambda context: after,
            "_friend_guard_sleep": lambda seconds: sleeps.append(seconds),
            "_write": lambda message: None,
        })
        result = namespace["_invoke_friend_guard_help_visual_click"](object(), frame)
        self.assertTrue(result)
        self.assertEqual([frame, after], matches)
        self.assertEqual([(frame, visible)], clicks)
        self.assertEqual(1, len(sleeps))

    def test_help_visual_click_retries_until_button_disappears(self):
        namespace = load_functions("_invoke_friend_guard_help_visual_click")
        initial = object()
        after_first = object()
        after_second = object()
        visible = {"matched": True, "center": (212, 598)}
        gone = {"matched": False, "center": None}
        frames = iter((after_first, after_second))
        clicks = []
        namespace.update({
            "_friend_guard_help_button_match": (
                lambda value: gone if value is after_second else visible
            ),
            "_invoke_friend_guard_match_coordinate_click": (
                lambda context, value, found: clicks.append(value) or True
            ),
            "_get_frame_from_bot": lambda context: next(frames),
            "_friend_guard_sleep": lambda seconds: None,
            "_write": lambda message: None,
        })
        result = namespace["_invoke_friend_guard_help_visual_click"](object(), initial)
        self.assertTrue(result)
        self.assertEqual([initial, after_first], clicks)

    def test_help_visual_click_does_not_report_success_while_button_remains(self):
        namespace = load_functions("_invoke_friend_guard_help_visual_click")
        initial = object()
        refreshes = [object(), object(), object()]
        visible = {"matched": True, "center": (212, 598)}
        clicks = []
        namespace.update({
            "_friend_guard_help_button_match": lambda value: visible,
            "_invoke_friend_guard_match_coordinate_click": (
                lambda context, value, found: clicks.append(value) or True
            ),
            "_get_frame_from_bot": lambda context: refreshes.pop(0),
            "_friend_guard_sleep": lambda seconds: None,
            "_write": lambda message: None,
        })
        result = namespace["_invoke_friend_guard_help_visual_click"](object(), initial)
        self.assertFalse(result)
        self.assertEqual(3, len(clicks))

    def test_visual_watchdog_waits_for_a_real_second_friend_action_cycle(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        clicks = []
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": lambda context, value: (False, ""),
            "_invoke_friend_actions_before_home": lambda context, value: (False, ""),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (True, "method.process_self_farm")
            ),
            "_write": lambda message: None,
        })

        class Clock:
            @staticmethod
            def sleep(seconds):
                return None

        namespace["time"] = Clock

        class Scheduler:
            _qqfarm_visual_friend_count = 1
            _qqfarm_friend_cycle_seen = False

        scheduler = Scheduler()
        passive = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(passive)
        self.assertEqual([], clicks)
        self.assertEqual(1, scheduler._qqfarm_visual_friend_count)

        scheduler._qqfarm_friend_cycle_seen = True
        active = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertTrue(active)
        self.assertEqual([frame], clicks)

    def test_visual_watchdog_skips_slow_native_probe_when_visual_probe_is_available(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        visual_probes = []
        native_probes = []
        chain_calls = []
        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_visual_actions_before_home": (
                lambda context, value: visual_probes.append(value) or (False, "")
            ),
            "_invoke_friend_actions_before_home": (
                lambda context, value: native_probes.append(value) or (False, "")
            ),
            "_run_friend_continuation_chain": (
                lambda context, value, label="": chain_calls.append((value, label))
                or {
                    "moves": 0,
                    "actions": 0,
                    "last_label": label,
                    "frame": value,
                    "exhausted": False,
                    "reason": "friend-surface-not-ready",
                }
            ),
            "_friend_chain_should_block_troublemaker": lambda context: True,
            "_write": lambda message: None,
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_visual_friend_count=0,
        )

        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )

        self.assertFalse(result)
        self.assertEqual([frame], visual_probes)
        self.assertEqual([], native_probes)
        self.assertEqual([(frame, "")], chain_calls)

    def test_visual_watchdog_rechecks_actions_then_returns_home_after_a_completed_action(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        probes = []
        clicks = []
        namespace.update({
            "_friend_watchdog_now": lambda: 110.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": (
                lambda context, value: probes.append(value) or (False, "")
            ),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (True, "method.process_self_farm")
            ),
            "_write": lambda message: None,
        })

        class Clock:
            @staticmethod
            def sleep(seconds):
                return None

        namespace["time"] = Clock

        class Scheduler:
            _qqfarm_visual_friend_count = 1
            _qqfarm_friend_cycle_seen = False
            _qqfarm_friend_action_last_ts = 100.0
            _qqfarm_friend_page_seen_ts = 90.0

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertTrue(result)
        self.assertEqual([frame], probes)
        self.assertEqual([frame], clicks)

    def test_visual_watchdog_timeout_probes_then_recovers_when_friend_branch_stops(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        probes = []
        clicks = []
        namespace.update({
            "_friend_watchdog_now": lambda: 130.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": (
                lambda context, value: probes.append(value) or (False, "")
            ),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (True, "method.process_self_farm")
            ),
            "_write": lambda message: None,
        })

        class Clock:
            @staticmethod
            def sleep(seconds):
                return None

        namespace["time"] = Clock

        class Scheduler:
            _qqfarm_visual_friend_count = 1
            _qqfarm_friend_cycle_seen = False
            _qqfarm_friend_action_last_ts = 0.0
            _qqfarm_friend_page_seen_ts = 100.0

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertTrue(result)
        self.assertEqual([frame], probes)
        self.assertEqual([frame], clicks)

    def test_fast_empty_guard_drops_stale_friend_list_strike_on_first_friend_page_pass(self):
        namespace = load_functions("_apply_friend_empty_return_home_guard")
        calls = []
        frame = object()

        class Clock:
            @staticmethod
            def time():
                return 116.0

        class Scheduler:
            _qqfarm_friend_fast_empty_count = 1
            _qqfarm_friend_fast_empty_ts = 100.0

        scheduler = Scheduler()
        namespace.update({
            "time": Clock,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_empty_guard_next": lambda old, elapsed, now, last: (2, True),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_resolve_friend_guard_action": lambda fn, args, kwargs: (
                (lambda: calls.append("home") or True), None, "method.go_home"
            ),
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action()
            ),
            "_friend_route_state_summary": lambda context: "state",
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = namespace["_apply_friend_empty_return_home_guard"](
            lambda *args, **kwargs: None,
            (scheduler, frame),
            {},
            0.8,
            "process_friend_farm",
        )
        self.assertFalse(result)
        self.assertEqual([], calls)
        self.assertEqual(1, scheduler._qqfarm_friend_fast_empty_count)

    def test_radish_safety_patch_matches_obfuscated_friend_modules_by_capability(self):
        namespace = load_functions(
            "_friend_radish_wrapper_has_marker",
            "_wrap_friend_skip_feature_gate_func",
            "_wrap_friend_skip_cache_func",
            "_patch_friend_radish_behavior_for_module",
        )
        namespace["_write"] = lambda message: None
        namespace["_throttled_write"] = lambda *args, **kwargs: None

        class ObfuscatedChecksModule:
            __name__ = "bot._qfixture.checks_friend"

            @staticmethod
            def _is_radish_skip_feature_enabled(bot):
                return True

            @staticmethod
            def _is_friend_row_in_radish_skip_cache(bot, row_key):
                return True

            @staticmethod
            def mark_friend_row_as_radish_skip(bot, row_key, ttl_seconds):
                return True

        module = ObfuscatedChecksModule()
        changed = namespace["_patch_friend_radish_behavior_for_module"](
            module, "test"
        )
        self.assertEqual(3, changed)
        self.assertFalse(module._is_radish_skip_feature_enabled(object()))
        self.assertFalse(module._is_friend_row_in_radish_skip_cache(object(), "row"))
        self.assertFalse(module.mark_friend_row_as_radish_skip(object(), "row", 600))

    def test_radish_safety_loader_scans_obfuscated_bot_modules(self):
        namespace = load_functions(
            "_friend_radish_wrapper_has_marker",
            "_wrap_friend_skip_feature_gate_func",
            "_wrap_friend_skip_cache_func",
            "_patch_friend_radish_behavior_for_module",
            "_patch_friend_radish_behavior_loaded",
        )
        namespace["_write"] = lambda message: None
        namespace["_throttled_write"] = lambda *args, **kwargs: None

        class ObfuscatedActionsModule:
            __name__ = "bot._qfixture.actions_friend"

            @staticmethod
            def _is_friend_skip_radish_enabled(bot):
                return True

            @staticmethod
            def mark_friend_row_as_radish_skip(bot, row_key, ttl_seconds):
                return True

        module = ObfuscatedActionsModule()

        class FakeSys:
            modules = {module.__name__: module}

        namespace["sys"] = FakeSys
        changed = namespace["_patch_friend_radish_behavior_loaded"]("test")
        self.assertEqual([module.__name__ + ":2"], changed)
        self.assertFalse(module._is_friend_skip_radish_enabled(object()))

    def test_visual_watchdog_second_confirmed_friend_frame_clicks_home_and_runs_self(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        self.assertIn("_apply_visual_friend_route_watchdog", namespace)
        clicks = []
        self_calls = []
        frame = object()
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (
                    self_calls.append(context) or True,
                    "method.process_self_farm",
                )
            ),
            "_write": lambda message: None,
        })

        class Clock:
            @staticmethod
            def sleep(seconds):
                return None

        namespace["time"] = Clock

        class Scheduler:
            _qqfarm_visual_friend_count = 0
            _qqfarm_friend_cycle_seen = True

        scheduler = Scheduler()
        first = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        scheduler._qqfarm_friend_cycle_seen = True
        second = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(first)
        self.assertTrue(second)
        self.assertEqual([frame], clicks)
        self.assertEqual([scheduler], self_calls)
        self.assertEqual(0, scheduler._qqfarm_visual_friend_count)

    def test_visual_watchdog_accepts_verified_home_when_self_action_has_no_work(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        events = []
        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": lambda context, value: (False, ""),
            "_invoke_friend_guard_home_coordinate_click": lambda context, value: True,
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (False, "method.process_self_farm")
            ),
            "_set_friend_chain_fast_interval": (
                lambda context, active: events.append(("fast", active)) or True
            ),
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
            "_write": lambda message: events.append(("log", message)),
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        class Scheduler:
            _qqfarm_visual_friend_count = 1
            _qqfarm_friend_cycle_seen = True
            _last_friend_farm_go_home_present = True
            _qqfarm_friend_branch_last_ts = 90.0

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )

        self.assertTrue(result)
        self.assertEqual(0, scheduler._qqfarm_visual_friend_count)
        self.assertFalse(scheduler._last_friend_farm_go_home_present)
        self.assertEqual(0.0, scheduler._qqfarm_friend_branch_last_ts)
        self.assertIn(("fast", False), events)


    def test_visual_watchdog_does_not_treat_self_page_as_home_button(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        self.assertIn("_apply_visual_friend_route_watchdog", namespace)
        self_calls = []
        frame = object()
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: False,
            "_invoke_friend_guard_post_click_self": (
                lambda fn, context, args, kwargs: (
                    self_calls.append(context) or True,
                    "method.process_self_farm",
                )
            ),
            "_write": lambda message: None,
        })

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_self_after_friend_count = 0

        scheduler = Scheduler()
        first = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        scheduler._qqfarm_friend_cycle_seen = True
        second = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(first)
        self.assertFalse(second)
        self.assertEqual([], self_calls)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)

    def test_visual_watchdog_resets_counter_on_self_frame(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        self.assertIn("_apply_visual_friend_route_watchdog", namespace)
        namespace.update({
            "_get_frame_from_bot": lambda context: object(),
            "_friend_guard_friend_ui_state": lambda value: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            _qqfarm_visual_friend_count = 1

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(result)
        self.assertEqual(0, scheduler._qqfarm_visual_friend_count)

    def test_runtime_log_tail_infers_the_latest_cycle_branch(self):
        import tempfile

        infer = load_function("_infer_cycle_branch_from_runtime_log")
        self.assertTrue(callable(infer))
        friend_line = "\u6b63\u5728\u68c0\u67e5\u597d\u53cb\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1"
        self_line = "\u6b63\u5728\u68c0\u67e5\u81ea\u5bb6\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1"
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "runtime.log"
            log_path.write_text(self_line + "\n" + friend_line + "\n", encoding="utf-8")
            self.assertEqual("friend", infer(paths=[str(log_path)]))
            log_path.write_text(friend_line + "\n" + self_line + "\n", encoding="utf-8")
            self.assertEqual("self", infer(paths=[str(log_path)]))

    def test_runtime_diag_wrapper_falls_back_to_log_tail_branch_hint(self):
        namespace = load_functions("_wrap_runtime_diag_method")

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        class Scheduler:
            pass

        scheduler = Scheduler()
        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "state",
            "_restore_runtime_business_switches": lambda context: 0,
            "_run_share_prompt_recovery": lambda context: False,
            "_get_frame_from_bot": lambda context: object(),
            "_friend_list_visit_button_rows": lambda frame: [],
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: None,
            "_infer_cycle_branch_from_runtime_log": lambda: "friend",
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda context: "ok", "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)
        self.assertEqual("ok", wrapped(scheduler))
        self.assertEqual("friend", scheduler._qqfarm_cycle_branch_hint)

    def test_runtime_cycle_branch_marker_records_friend_and_self_log_messages(self):
        note = load_function("_note_runtime_cycle_branch")
        self.assertTrue(callable(note))

        class Scheduler:
            pass

        scheduler = Scheduler()
        note.__globals__["_ACTIVE_RUN_CYCLE_CONTEXT"] = scheduler
        self.assertEqual(
            "friend",
            note("\u6b63\u5728\u68c0\u67e5\u597d\u53cb\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1"),
        )
        self.assertEqual("friend", scheduler._qqfarm_cycle_branch_hint)
        self.assertEqual(
            "self",
            note("\u6b63\u5728\u68c0\u67e5\u81ea\u5bb6\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1"),
        )
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)

    def test_runtime_diag_wrapper_exposes_current_context_to_branch_marker(self):
        namespace = load_functions(
            "_note_runtime_cycle_branch",
            "_wrap_runtime_diag_method",
        )
        self.assertTrue(callable(namespace.get("_note_runtime_cycle_branch")))
        events = []

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        class Scheduler:
            pass

        scheduler = Scheduler()

        def original(context):
            events.append(namespace["_note_runtime_cycle_branch"](
                "\u6b63\u5728\u68c0\u67e5\u597d\u53cb\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1"
            ))
            return "ok"

        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "state",
            "_restore_runtime_business_switches": lambda context: 0,
            "_run_share_prompt_recovery": lambda context: False,
            "_get_frame_from_bot": lambda context: object(),
            "_friend_list_visit_button_rows": lambda frame: [],
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: None,
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original, "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)
        self.assertEqual("ok", wrapped(scheduler))
        self.assertEqual(["friend"], events)
        self.assertEqual("friend", scheduler._qqfarm_cycle_branch_hint)
        self.assertIsNone(namespace.get("_ACTIVE_RUN_CYCLE_CONTEXT"))

    def test_visual_watchdog_retries_friend_entry_when_friend_branch_stays_on_home(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        recoveries = []
        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_invoke_friend_branch_from_home": (
                lambda context, candidate: recoveries.append(candidate) or True
            ),
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_FRIEND_HOME_LAST_MATCH": {},
            "_FRIEND_LIST_LAST_MATCH": {},
            "_write": lambda message: None,
        })

        class Scheduler:
            _qqfarm_cycle_branch_hint = "friend"
            _qqfarm_friend_cycle_seen = False
            _qqfarm_visual_friend_count = 0

        scheduler = Scheduler()
        self.assertFalse(namespace["_apply_visual_friend_route_watchdog"](
            lambda *args, **kwargs: None, scheduler, "FarmBotCV.run_cycle"
        ))
        self.assertEqual([], recoveries)
        self.assertFalse(namespace["_apply_visual_friend_route_watchdog"](
            lambda *args, **kwargs: None, scheduler, "FarmBotCV.run_cycle"
        ))
        self.assertEqual([frame], recoveries)

    def test_friend_branch_home_recovery_never_reenters_friend_dispatcher(self):
        recover = load_function("_invoke_friend_branch_from_home")
        self.assertTrue(callable(recover))
        frame = object()
        calls = []

        class Scheduler:
            def check_friend_help_request_entry(self, game_frame):
                calls.append(("help-entry", game_frame))
                return False

            def check_friend_icon(self, game_frame):
                calls.append(("friend-icon", game_frame))
                return False

            def process_friend_farm(self, game_frame):
                calls.append(("processor", game_frame))
                return True

        scheduler = Scheduler()
        recover.__globals__.update({
            "_guard_dog_ui_config_enabled": lambda: False,
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })
        self.assertFalse(recover(scheduler, frame))
        self.assertEqual(
            [("help-entry", frame), ("friend-icon", frame)],
            calls,
        )

    def test_runtime_diag_wrapper_runs_visual_watchdog_after_cycle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        calls = []

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "state",
            "_apply_visual_friend_route_watchdog": (
                lambda fn, context, label: calls.append((fn, context, label))
            ),
        })

        context = object()
        original = lambda self: "ok"
        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original, "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)
        self.assertEqual("ok", wrapped(context))
        self.assertEqual([(original, context, "FarmBotCV.run_cycle")], calls)

    def test_runtime_diag_wrapper_handles_current_friend_list_before_original_cycle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        calls = []
        namespace.update({
            "time": type("Clock", (), {"time": staticmethod(lambda: 100.0)}),
            "_restore_runtime_business_switches": lambda context: 0,
            "_run_share_prompt_recovery": lambda context: None,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_list_visit_button_rows": lambda candidate: [
                {"center": (365, 289)},
                {"center": (365, 383)},
                {"center": (365, 478)},
            ],
            "_handle_friend_list_surface": (
                lambda context, candidate: calls.append(("list", context, candidate)) or "visited"
            ),
            "_write": lambda message: calls.append(("log", message)),
        })

        context = object()
        original = lambda self: calls.append(("original", self)) or "original-result"
        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original, "FarmBotCV.run_cycle"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(context))
        self.assertIn(("list", context, frame), calls)
        self.assertNotIn(("original", context), calls)

    def test_process_friend_wrapper_contains_return_home_guard(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("_apply_friend_empty_return_home_guard", source)
        self.assertIn("go_home", source)
        self.assertIn("_apply_friend_empty_return_home_guard(\n                        fn, a, k", source)
        self.assertIn("v70-friend-help-click-verify", source)


    def test_friend_action_probe_uses_visual_steal_before_visual_help(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_visual_actions_before_home",
            "_invoke_friend_actions_before_home",
        )
        frame = object()
        visual_calls = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                return False
            def check_steal_one_icon(self, game_frame):
                return False
            def check_steal_icon(self, game_frame):
                return False
            def check_help_all_entry(self, game_frame):
                return False

        namespace.update({
            "_invoke_friend_guard_steal_visual_click": (
                lambda context, value: visual_calls.append("steal") or True
            ),
            "_invoke_friend_guard_help_visual_click": (
                lambda context, value: visual_calls.append("help") or True
            ),
            "_write": lambda message: None,
        })
        acted, label = namespace["_invoke_friend_actions_before_home"](Scheduler(), frame)
        self.assertTrue(acted)
        self.assertEqual("visual.friend_steal_all", label)
        self.assertEqual(["steal"], visual_calls)

    def test_friend_next_entry_prefers_matching_action_type(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_next_actionable_entry",
        )
        self.assertTrue(callable(namespace.get("_invoke_friend_next_actionable_entry")))
        frame = object()
        calls = []

        class Scheduler:
            def check_friend_farm_bottom_steal_entry(self, game_frame):
                calls.append(("steal", game_frame))
                return True
            def check_friend_farm_bottom_help_all_entry(self, game_frame):
                calls.append(("help", game_frame))
                return True

        namespace["_write"] = lambda message: None
        moved, label = namespace["_invoke_friend_next_actionable_entry"](
            Scheduler(), frame, "visual.friend_steal_all"
        )
        self.assertTrue(moved)
        self.assertEqual("method.check_friend_farm_bottom_steal_entry", label)
        self.assertEqual([("steal", frame)], calls)

    def test_visual_watchdog_moves_to_next_friend_after_action(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        self.assertTrue(callable(namespace.get("_apply_visual_friend_route_watchdog")))
        frame = object()
        next_calls = []
        home_clicks = []
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": (
                lambda context, value: (True, "visual.friend_help_all")
            ),
            "_invoke_friend_next_actionable_entry": (
                lambda context, value, label="": next_calls.append((value, label)) or (True, "method.check_friend_farm_bottom_help_all_entry")
            ),
            "_set_friend_chain_fast_interval": lambda context, active: setattr(context, "chain_fast", active),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: home_clicks.append(value) or True
            ),
            "_write": lambda message: None,
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
            "_friend_watchdog_now": lambda: 100.0,
        })

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(result)
        self.assertEqual([(frame, "visual.friend_help_all")], next_calls)
        self.assertEqual([], home_clicks)
        self.assertTrue(scheduler.chain_fast)


    def test_visual_watchdog_runs_continuation_chain_after_action(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        chain_calls = []
        home_clicks = []
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": (
                lambda context, value: (True, "visual.friend_help_all")
            ),
            "_run_friend_continuation_chain": (
                lambda context, value, label="": chain_calls.append((value, label))
                or {"moves": 2, "actions": 2, "last_label": label, "frame": value}
            ),
            "_set_friend_chain_fast_interval": lambda context, active: setattr(context, "chain_fast", active),
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: home_clicks.append(value) or True
            ),
            "_write": lambda message: None,
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
            "_friend_watchdog_now": lambda: 100.0,
        })

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0

        scheduler = Scheduler()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )
        self.assertFalse(result)
        self.assertEqual([(frame, "visual.friend_help_all")], chain_calls)
        self.assertEqual([], home_clicks)
        self.assertTrue(scheduler.chain_fast)


    def test_visual_watchdog_goes_home_immediately_after_chain_reaches_first_no_action_friend(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        current_frame = object()
        exhausted_frame = object()
        captures = iter((current_frame, current_frame))
        home_clicks = []
        chain_calls = []
        namespace.update({
            "_get_frame_from_bot": lambda context: next(captures, current_frame),
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": (
                lambda context, value: (True, "visual.friend_help_all")
            ),
            "_run_friend_continuation_chain": (
                lambda context, value, label="": chain_calls.append((value, label))
                or {
                    "moves": 1,
                    "actions": 0,
                    "last_label": label,
                    "frame": exhausted_frame,
                    "exhausted": True,
                    "reason": "first-no-action-friend",
                }
            ),
            "_set_friend_chain_fast_interval": lambda context, active: None,
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: home_clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda *args, **kwargs: (True, "method.process_self_farm")
            ),
            "_write": lambda message: None,
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
            "_friend_watchdog_now": lambda: 100.0,
        })

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0

        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, Scheduler(), "FarmBotCV.run_cycle"
        )

        self.assertTrue(result)
        self.assertEqual([(current_frame, "visual.friend_help_all")], chain_calls)
        self.assertEqual([exhausted_frame], home_clicks)


    def test_visual_watchdog_goes_home_when_passive_chain_reaches_first_no_action_friend(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        current_frame = object()
        exhausted_frame = object()
        home_clicks = []
        chain_calls = []
        namespace.update({
            "_get_frame_from_bot": lambda context: current_frame,
            "_friend_guard_friend_ui_state": lambda value: True,
            "_invoke_friend_actions_before_home": lambda context, value: (False, ""),
            "_run_friend_continuation_chain": (
                lambda context, value, label="": chain_calls.append((value, label))
                or {
                    "moves": 1,
                    "actions": 0,
                    "last_label": label,
                    "frame": exhausted_frame,
                    "exhausted": True,
                    "reason": "first-no-action-friend",
                }
            ),
            "_set_friend_chain_fast_interval": lambda context, active: None,
            "_invoke_friend_guard_home_coordinate_click": (
                lambda context, value: home_clicks.append(value) or True
            ),
            "_invoke_friend_guard_post_click_self": (
                lambda *args, **kwargs: (True, "method.process_self_farm")
            ),
            "_write": lambda message: None,
            "_FRIEND_HOME_LAST_MATCH": {"matched": True},
            "_FRIEND_LIST_LAST_MATCH": {"matched": False},
            "_friend_watchdog_now": lambda: 100.0,
        })

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0
            _qqfarm_friend_action_last_label = "visual.friend_help_all"

        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, Scheduler(), "FarmBotCV.run_cycle"
        )

        self.assertTrue(result)
        self.assertEqual([(current_frame, "visual.friend_help_all")], chain_calls)
        self.assertEqual([exhausted_frame], home_clicks)


    def test_live_sanitized_help_button_matches_current_client_render(self):
        namespace = load_functions(
            "_friend_guard_read_template",
            "_friend_guard_match_template",
            "_friend_guard_help_button_match",
        )
        import cv2
        namespace["_FRIEND_GUARD_TEMPLATE_CACHE"] = {}
        namespace["_FRIEND_HELP_ALL_TEMPLATE_PATH"] = str(
            ROOT / "portable" / "friend_help_all_button.png"
        )
        frame = cv2.imread(str(FIXTURES / "friend_help_all_live_sanitized.png"))

        self.assertIsNotNone(frame)
        match = namespace["_friend_guard_help_button_match"](frame)
        self.assertTrue(match["matched"], match)
    def test_visual_action_templates_distinguish_steal_from_help(self):
        namespace = load_functions(
            "_friend_guard_read_template",
            "_friend_guard_match_template",
            "_friend_guard_help_button_match",
            "_friend_guard_steal_button_match",
        )
        import cv2
        namespace["_FRIEND_GUARD_TEMPLATE_CACHE"] = {}
        namespace["_FRIEND_HELP_ALL_TEMPLATE_PATH"] = str(
            ROOT / "portable" / "friend_help_all_button.png"
        )
        namespace["_FRIEND_STEAL_ALL_TEMPLATE_PATH"] = str(
            ROOT / "portable" / "friend_steal_all_button.png"
        )
        help_frame = cv2.imread(str(ROOT.parents[1] / "verification-evidence" / "v67-stuck-friend-client.png"))
        if help_frame is None:
            help_frame = cv2.imread(str(FIXTURES / "friend_home_low_edge_live.png"))
        steal_frame = cv2.imread(str(FIXTURES / "friend_steal_all_live.png"))
        self.assertIsNotNone(steal_frame)
        self.assertTrue(namespace["_friend_guard_steal_button_match"](steal_frame)["matched"])
        self.assertFalse(namespace["_friend_guard_help_button_match"](steal_frame)["matched"])
        if help_frame is not None:
            self.assertTrue(namespace["_friend_guard_help_button_match"](help_frame)["matched"])
            self.assertFalse(namespace["_friend_guard_steal_button_match"](help_frame)["matched"])


    def test_friend_continuation_stops_before_navigation_when_help_quota_exhausted(self):
        namespace = load_functions(
            "_friend_help_quota_active",
            "_run_friend_continuation_chain",
        )
        moves = []
        frame = object()
        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda context, candidate, label="": moves.append(candidate) or (True, "next")
            ),
            "_invoke_friend_actions_before_home": lambda context, candidate: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_help_quota_exhausted=True
        )

        result = namespace["_run_friend_continuation_chain"](scheduler, frame)

        self.assertTrue(result["exhausted"])
        self.assertEqual("friend-help-quota-exhausted", result["reason"])
        self.assertEqual(0, result["moves"])
        self.assertEqual([], moves)

    def test_friend_continuation_chain_processes_multiple_bottom_entries(self):
        namespace = load_functions("_run_friend_continuation_chain")
        self.assertTrue(callable(namespace.get("_run_friend_continuation_chain")))
        frames = [object(), object(), object(), object()]
        moves = []
        actions = []

        def move_next(context, frame, label=""):
            moves.append((frame, label))
            return ((True, "next") if len(moves) <= 2 else (False, ""))

        def act(context, frame):
            actions.append(frame)
            return True, "visual.friend_help_all"

        captures = iter(frames[1:])
        namespace.update({
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_actions_before_home": act,
            "_get_frame_from_bot": lambda context: next(captures, frames[-1]),
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 12

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frames[0], "visual.friend_steal_all"
        )
        self.assertEqual(2, result["moves"])
        self.assertEqual(2, result["actions"])
        self.assertEqual(3, len(moves))
        self.assertEqual(2, len(actions))


    def test_runtime_diag_wrapper_runs_share_prompt_recovery_before_and_after_cycle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        calls = []

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        context = object()
        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "state",
            "_restore_runtime_business_switches": lambda value: 0,
            "_run_share_prompt_recovery": lambda value: calls.append(value) or False,
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: None,
        })

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda self: "ok", "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)
        self.assertEqual("ok", wrapped(context))
        self.assertEqual([context, context], calls)

    def test_runtime_diag_wrapper_restores_friend_switches_before_cycle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        events = []

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        class Scheduler:
            enable_process_friend = False

        scheduler = Scheduler()

        def restore(context):
            context.enable_process_friend = True
            events.append("restored")
            return 1

        def original(context):
            events.append(("original", context.enable_process_friend))
            return "ok"

        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "state",
            "_restore_runtime_business_switches": restore,
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: None,
        })

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original, "FarmBotCV.run_cycle"
        )
        self.assertTrue(changed)
        self.assertEqual("ok", wrapped(scheduler))
        self.assertEqual(["restored", ("original", True)], events)

    def test_run_cycle_diagnostics_do_not_serialize_full_runtime_state_each_round(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        state_calls = []

        class Clock:
            values = iter((100.0, 101.0))

            @classmethod
            def time(cls):
                return next(cls.values)

        namespace.update({
            "time": Clock,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: state_calls.append(value) or "state",
            "_restore_runtime_business_switches": lambda context: 0,
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: None,
        })

        wrapped, _ = namespace["_wrap_runtime_diag_method"](
            lambda self: "ok", "FarmBotCV.run_cycle"
        )
        self.assertEqual("ok", wrapped(object()))
        self.assertEqual([], state_calls)

    def test_friend_continuation_waits_for_delayed_action_after_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frames = [object(), object(), object(), object(), object(), object()]
        move_calls = []
        action_calls = []

        def move_next(context, frame, label=""):
            move_calls.append((frame, label))
            return ((True, "next") if len(move_calls) == 1 else (False, ""))

        def act(context, frame):
            action_calls.append(frame)
            if len(action_calls) < 12:
                return False, ""
            return True, "visual.friend_help_all"

        captures = iter(frames[1:])
        namespace.update({
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_actions_before_home": act,
            "_get_frame_from_bot": lambda context: next(captures, frames[-1]),
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 12

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frames[0], "visual.friend_steal_all"
        )
        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertGreaterEqual(len(action_calls), 12)


    def test_visual_watchdog_trusts_real_friend_branch_when_template_is_unreadable(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        events = []
        frame = object()

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0
            _last_friend_farm_go_home_present = True

        scheduler = Scheduler()
        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: False,
            "_invoke_friend_actions_before_home": lambda context, value: events.append("probe") or (True, "method.check_steal_all_icon"),
            "_run_friend_continuation_chain": lambda context, value, label: events.append(("chain", label)) or {
                "moves": 2,
                "actions": 2,
                "last_label": "method.check_friend_farm_bottom_steal_entry",
                "exhausted": False,
            },
            "_set_friend_chain_fast_interval": lambda context, active: events.append(("fast", active)) or True,
            "_FRIEND_HOME_LAST_MATCH": {},
            "_FRIEND_LIST_LAST_MATCH": {},
            "_write": lambda message: None,
        })

        self.assertFalse(namespace["_apply_visual_friend_route_watchdog"](
            lambda *args, **kwargs: None, scheduler, "FarmBotCV.run_cycle"
        ))
        self.assertIn("probe", events)
        self.assertIn(("chain", "method.check_steal_all_icon"), events)

    def test_friend_continuation_probes_action_when_visual_state_is_false_after_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frames = [object(), object(), object()]
        move_calls = []
        action_calls = []

        def move_next(context, frame, label=""):
            move_calls.append((frame, label))
            return ((True, "next") if len(move_calls) == 1 else (False, ""))

        def act(context, frame):
            action_calls.append(frame)
            return True, "method.check_steal_all_icon"

        captures = iter(frames[1:])
        namespace.update({
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_actions_before_home": act,
            "_get_frame_from_bot": lambda context: next(captures, frames[-1]),
            "_friend_guard_friend_ui_state": lambda frame: False,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 12
            _last_friend_farm_go_home_present = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frames[0], "method.check_steal_all_icon"
        )
        self.assertEqual(1, result["moves"])
        self.assertEqual(0, result["actions"])
        self.assertEqual(0, len(action_calls))
        self.assertEqual("friend-surface-not-ready", result["reason"])




    def test_friend_action_probe_skips_native_single_icon_on_unreadable_friend_frame(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_invoke_friend_actions_before_home",
        )
        frame = object()
        native_calls = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                return False

            def check_steal_one_icon(self, game_frame):
                native_calls.append("single")
                return True

            def check_steal_icon(self, game_frame):
                native_calls.append("steal")
                return True

            def check_help_all_entry(self, game_frame):
                native_calls.append("help")
                return True

        namespace.update({
            "_friend_guard_friend_ui_state": lambda value: False,
            "_invoke_friend_guard_steal_visual_click": lambda *args: False,
            "_invoke_friend_guard_help_visual_click": lambda *args: False,
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_actions_before_home"](
            Scheduler(), frame
        )
        self.assertFalse(acted)
        self.assertEqual("", label)
        self.assertEqual([], native_calls)

    def test_visual_watchdog_keeps_friend_when_navigation_is_not_confirmed(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        events = []

        class Scheduler:
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 0
            _last_friend_farm_go_home_present = True

            def check_go_home_icon(self, game_frame):
                events.append(("home", game_frame))
                return True

        scheduler = Scheduler()
        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda value: False,
            "_invoke_friend_actions_before_home": lambda context, value: (False, ""),
            "_run_friend_continuation_chain": lambda context, value, label: {
                "moves": 0,
                "actions": 0,
                "last_label": label,
                "exhausted": False,
                "reason": "navigation-not-confirmed",
            },
            "_invoke_friend_guard_action": lambda action, target, args, kwargs: action(args[-1]),
            "_invoke_friend_guard_post_click_self": lambda *args, **kwargs: (True, "method.process_self_farm"),
            "_set_friend_chain_fast_interval": lambda context, active: events.append(("fast", active)) or True,
            "_FRIEND_HOME_LAST_MATCH": {},
            "_FRIEND_LIST_LAST_MATCH": {},
            "_write": lambda message: None,
            "time": type("Clock", (), {"sleep": staticmethod(lambda seconds: None)}),
        })

        self.assertFalse(namespace["_apply_visual_friend_route_watchdog"](
            lambda *args, **kwargs: None, scheduler, "FarmBotCV.run_cycle"
        ))
        self.assertNotIn(("home", frame), events)
        self.assertNotIn(("fast", False), events)

    def test_friend_action_probe_masks_bottom_friend_strip_before_template_checks(self):
        import numpy as np

        namespace = load_functions(
            "_friend_action_frame_without_bottom_bar",
            "_invoke_friend_guard_action",
            "_invoke_friend_actions_before_home",
        )
        frame = np.full((100, 80, 3), 255, dtype=np.uint8)
        seen = []

        class Scheduler:
            def check_steal_all_icon(self, game_frame):
                seen.append(game_frame.copy())
                return False

            def check_steal_one_icon(self, game_frame):
                return False

            def check_steal_icon(self, game_frame):
                return False

            def check_help_all_entry(self, game_frame):
                return False

        namespace.update({
            "_write": lambda message: None,
            "_invoke_friend_guard_steal_visual_click": lambda *args: False,
            "_invoke_friend_guard_help_visual_click": lambda *args: False,
        })
        namespace["_invoke_friend_actions_before_home"](Scheduler(), frame)

        self.assertEqual(1, len(seen))
        self.assertGreater(int(seen[0][:80].mean()), 200)
        self.assertEqual(0, int(seen[0][86:].max()))

    def test_friend_continuation_stops_when_bottom_navigation_does_not_change_page(self):
        import numpy as np

        namespace = load_functions(
            "_friend_navigation_signature",
            "_friend_navigation_change_score",
            "_run_friend_continuation_chain",
        )
        frame = np.zeros((120, 80, 3), dtype=np.uint8)
        frame[:25, :35] = 120
        frame[100:, :] = 200
        moves = []
        actions = []

        def move_next(context, value, label=""):
            moves.append(value)
            return ((True, "next") if len(moves) == 1 else (False, ""))

        namespace.update({
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_actions_before_home": lambda context, value: actions.append(value) or (True, "method.check_steal_one_icon"),
            "_get_frame_from_bot": lambda context: frame.copy(),
            "_friend_guard_friend_ui_state": lambda value: False,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 12

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "method.check_steal_one_icon"
        )
        self.assertEqual(0, result["moves"])
        self.assertEqual(0, result["actions"])
        self.assertEqual("navigation-not-confirmed", result["reason"])
        self.assertEqual([], actions)

    def test_friend_continuation_refreshes_branch_evidence_after_processing_moves(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frames = [object(), object(), object()]
        move_calls = []

        def move_next(context, frame, label=""):
            move_calls.append((frame, label))
            return ((True, "next") if len(move_calls) == 1 else (False, ""))

        captures = iter(frames[1:])
        namespace.update({
            "time": type("Clock", (), {"time": staticmethod(lambda: 321.0)}),
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_actions_before_home": lambda context, frame: (True, "method.check_steal_one_icon"),
            "_get_frame_from_bot": lambda context: next(captures, frames[-1]),
            "_friend_guard_friend_ui_state": lambda frame: False,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 12
            _qqfarm_visual_friend_count = 0
            _qqfarm_friend_branch_last_ts = 0.0
            _last_friend_farm_go_home_present = False

        scheduler = Scheduler()
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frames[0], "method.check_steal_one_icon"
        )
        self.assertEqual(1, result["moves"])
        self.assertEqual(321.0, scheduler._qqfarm_friend_branch_last_ts)
        self.assertEqual(1, scheduler._qqfarm_visual_friend_count)
        self.assertTrue(scheduler._last_friend_farm_go_home_present)

    def test_friend_next_entry_masks_the_current_selected_carousel_card(self):
        namespace = load_functions(
            "_invoke_friend_guard_action",
            "_friend_navigation_frame_without_selected_card",
            "_invoke_friend_next_actionable_entry",
        )
        import numpy as np

        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        green = np.array([45, 220, 85], dtype=np.uint8)
        frame[684:689, 166:263] = green
        frame[758:763, 166:263] = green
        frame[684:763, 166:171] = green
        frame[684:763, 258:263] = green
        frame[720, 210] = (11, 22, 33)
        frame[720, 330] = (44, 55, 66)
        probed = []

        class Scheduler:
            enable_friend_steal = True
            enable_friend_help = True

            def check_friend_farm_bottom_steal_entry(self, game_frame):
                probed.append(game_frame.copy())
                return True

        namespace["_write"] = lambda message: None
        moved, label = namespace["_invoke_friend_next_actionable_entry"](
            Scheduler(), frame, "visual.friend_steal_all"
        )

        self.assertTrue(moved)
        self.assertEqual("method.check_friend_farm_bottom_steal_entry", label)
        self.assertEqual(1, len(probed))
        self.assertTrue(np.all(probed[0][720, 210] == 0))
        self.assertTrue(np.array_equal(probed[0][720, 330], np.array([44, 55, 66], dtype=np.uint8)))
        self.assertTrue(np.array_equal(frame[720, 210], np.array([11, 22, 33], dtype=np.uint8)))

    def test_visual_friend_action_uses_client_click_without_second_absolute_click(self):
        namespace = load_functions("_invoke_friend_guard_match_coordinate_click")
        calls = []
        namespace["_friend_guard_post_client_click"] = (
            lambda x, y, w, h: calls.append(("client", x, y, w, h)) or True
        )
        namespace["_friend_guard_frame_to_screen"] = (
            lambda x, y, w, h: calls.append(("map", x, y, w, h)) or (900, 1400)
        )
        namespace["_write"] = lambda message: None

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            def click_at_position(self, x, y):
                calls.append(("absolute", x, y))
                return True

        result = namespace["_invoke_friend_guard_match_coordinate_click"](
            Scheduler(), Frame(), {"center": (222, 622)}
        )

        self.assertTrue(result)
        self.assertEqual([("client", 222, 622, 428, 800)], calls)

    def test_visual_friend_action_absolute_fallback_rejects_point_covered_by_other_window(self):
        namespace = load_functions("_invoke_friend_guard_match_coordinate_click")
        clicks = []
        namespace.update({
            "_friend_guard_post_client_click": lambda *args: False,
            "_friend_guard_frame_to_screen": lambda *args: (900, 1400),
            "_friend_guard_screen_point_owned_by_farm": lambda x, y: False,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        class Scheduler:
            def click_at_position(self, x, y):
                clicks.append((x, y))
                return True

        result = namespace["_invoke_friend_guard_match_coordinate_click"](
            Scheduler(), Frame(), {"center": (222, 622)}
        )

        self.assertFalse(result)
        self.assertEqual([], clicks)

    def test_friend_radish_diagnostics_are_disabled_during_normal_timer_ticks(self):
        namespace = load_functions("_friend_radish_diag_dump")
        writes = []
        fake_module = types.SimpleNamespace(
            __name__="bot.synthetic",
            process_friend_farm=lambda: None,
            _friend_row_cache={"row": "value"},
        )
        namespace.update({
            "sys": types.SimpleNamespace(modules={"bot.synthetic": fake_module}),
            "_FRIEND_RADISH_DIAG_SEEN": set(),
            "_friend_diag_code_details": lambda obj: "details",
            "_write": writes.append,
        })

        self.assertEqual(0, namespace["_friend_radish_diag_dump"]("qt-safe-tick"))
        self.assertEqual([], writes)



    def test_selected_friend_card_detector_rejects_decoration_panel(self):
        import cv2

        namespace = load_functions("_friend_selected_carousel_card_bounds")
        frame = cv2.imread(str(FIXTURES / "decoration_panel_428x800.png"))

        self.assertIsNotNone(frame)
        self.assertIsNone(
            namespace["_friend_selected_carousel_card_bounds"](frame)
        )

    def test_adjacent_friend_navigation_rejects_non_friend_surface_with_green_card(self):
        import cv2

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = cv2.imread(str(FIXTURES / "decoration_panel_428x800.png"))
        clicks = []
        context = types.SimpleNamespace(
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_last_selected_bounds={
                "left": 196,
                "right": 306,
                "top": 656,
                "bottom": 775,
                "width": 110,
                "height": 119,
            },
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_friend_selected_carousel_card_bounds": lambda candidate: {
                "left": 196,
                "right": 306,
                "top": 656,
                "bottom": 775,
                "width": 110,
                "height": 119,
            },
            "_friend_adjacent_card_center": lambda candidate: (365, 716),
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertFalse(moved)
        self.assertEqual("", label)
        self.assertEqual([], clicks)
        self.assertIsNone(
            getattr(context, "_qqfarm_friend_chain_last_selected_bounds", None)
        )

    def test_adjacent_friend_navigation_clicks_right_of_selected_card(self):
        import numpy as np

        namespace = load_functions(
            "_friend_selected_carousel_card_bounds",
            "_friend_adjacent_card_center",
            "_invoke_friend_adjacent_card_navigation",
        )
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        green = np.array([45, 220, 85], dtype=np.uint8)
        frame[684:689, 166:263] = green
        frame[758:763, 166:263] = green
        frame[684:763, 166:171] = green
        frame[684:763, 258:263] = green
        clicks = []
        namespace.update({
            "_friend_guard_post_client_click": (
                lambda x, y, w, h: clicks.append((x, y, w, h)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            types.SimpleNamespace(), frame
        )

        self.assertTrue(moved)
        self.assertEqual("visual.adjacent-friend-card", label)
        self.assertEqual(1, len(clicks))
        x, y, width, height = clicks[0]
        self.assertEqual((428, 800), (width, height))
        self.assertTrue(300 <= x <= 325)
        self.assertTrue(710 <= y <= 740)

    def test_adjacent_friend_navigation_never_moves_back_to_the_left_friend(self):
        namespace = load_functions("_friend_adjacent_card_center")

        class Frame:
            shape = (800, 428, 3)

        namespace["_friend_selected_carousel_card_bounds"] = lambda frame: {
            "left": 325,
            "right": 421,
            "top": 682,
            "bottom": 760,
            "width": 96,
            "height": 78,
        }

        self.assertIsNone(namespace["_friend_adjacent_card_center"](Frame()))

    def test_friend_continuation_uses_adjacent_card_when_native_navigation_is_false_positive(self):
        import numpy as np

        namespace = load_functions(
            "_friend_navigation_signature",
            "_friend_navigation_change_score",
            "_run_friend_continuation_chain",
        )
        before = np.zeros((120, 80, 3), dtype=np.uint8)
        before[:25, :35] = 90
        after = before.copy()
        after[:25, :35] = 220
        state = {"fallback": False, "moves": 0}
        fallback_calls = []
        action_calls = []

        def move_next(context, frame, label=""):
            state["moves"] += 1
            return ((True, "native-next") if state["moves"] == 1 else (False, ""))

        def adjacent(context, frame):
            fallback_calls.append(frame)
            if len(fallback_calls) > 1:
                return False, ""
            state["fallback"] = True
            return True, "visual.adjacent-friend-card"

        namespace.update({
            "_invoke_friend_next_actionable_entry": move_next,
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_actions_before_home": (
                lambda context, frame: action_calls.append(frame)
                or (True, "visual.friend_help_all")
            ),
            "_get_frame_from_bot": (
                lambda context: after.copy() if state["fallback"] else before.copy()
            ),
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 3
            friend_chain_action_poll_limit = 12
            friend_chain_primary_navigation_poll_limit = 4

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), before, "method.check_steal_one_icon"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertGreaterEqual(len(fallback_calls), 1)
        self.assertEqual(1, len(action_calls))

    def test_friend_continuation_uses_adjacent_card_when_native_reports_no_next_entry(self):
        import numpy as np

        namespace = load_functions(
            "_friend_navigation_signature",
            "_friend_navigation_change_score",
            "_run_friend_continuation_chain",
        )
        before = np.zeros((120, 80, 3), dtype=np.uint8)
        before[:25, :35] = 70
        after = before.copy()
        after[:25, :35] = 210
        state = {"fallback": False}
        fallback_calls = []

        def adjacent(context, frame):
            fallback_calls.append(frame)
            if len(fallback_calls) > 1:
                return False, ""
            state["fallback"] = True
            return True, "visual.adjacent-friend-card"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_actions_before_home": (
                lambda context, frame: (True, "visual.friend_steal_all")
            ),
            "_get_frame_from_bot": (
                lambda context: after.copy() if state["fallback"] else before.copy()
            ),
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 3
            friend_chain_action_poll_limit = 12
            friend_chain_primary_navigation_poll_limit = 4

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), before, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertGreaterEqual(len(fallback_calls), 1)


    def test_carousel_selection_change_requires_a_meaningful_horizontal_shift(self):
        changed = load_function("_friend_carousel_selection_changed")
        self.assertTrue(callable(changed))
        before = {"left": 20, "right": 116, "top": 682, "bottom": 760, "width": 96}
        residue = {"left": 23, "right": 119, "top": 682, "bottom": 760, "width": 96}
        next_card = {"left": 124, "right": 220, "top": 682, "bottom": 760, "width": 96}
        self.assertFalse(changed(before, residue, 428))
        self.assertTrue(changed(before, next_card, 428))

    def test_friend_continuation_does_not_use_visible_action_as_immediate_navigation_proof(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        sleeps = []
        action_calls = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": lambda *args, **kwargs: (True, "visual.adjacent-friend-card"),
            "_invoke_friend_actions_before_home": (
                lambda context, candidate: action_calls.append(candidate)
                or (True, "visual.friend_help_all")
            ),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: sleeps.append(float(seconds)),
            "_friend_navigation_signature": lambda candidate: (100, 100, 100),
            "_friend_navigation_change_score": lambda signature, candidate: 0.0,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 12
            friend_chain_primary_navigation_poll_limit = 4

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "method.check_steal_one_icon"
        )

        self.assertEqual(0, result["moves"])
        self.assertEqual(0, result["actions"])
        self.assertEqual("navigation-not-confirmed", result["reason"])
        self.assertEqual(0, len(action_calls))

    def test_friend_continuation_uses_carousel_selection_change_when_visual_signature_is_static(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        state = {"moves": 0}
        actions = []

        def adjacent(context, candidate):
            state["moves"] += 1
            if state["moves"] <= 3:
                return True, "visual.adjacent-friend-card"
            return False, ""

        def action(context, candidate):
            actions.append(state["moves"])
            return True, "visual.friend_help_all"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_actions_before_home": action,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: (80, 80, 80),
            "_friend_navigation_change_score": lambda signature, candidate: 0.0,
            "_friend_selected_carousel_card_bounds": lambda candidate: {
                "left": state["moves"] * 100,
                "right": (state["moves"] * 100) + 90,
                "top": 680,
                "bottom": 760,
                "width": 90,
                "height": 80,
            },
            "_friend_carousel_selection_changed": (
                lambda before, after, width=428: abs(
                    ((after["left"] + after["right"]) / 2.0)
                    - ((before["left"] + before["right"]) / 2.0)
                ) >= 40
            ),
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 6
            friend_chain_action_poll_limit = 10
            friend_chain_primary_navigation_poll_limit = 3

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_steal_all"
        )

        self.assertEqual(3, result["moves"])
        self.assertEqual(3, result["actions"])
        self.assertEqual([1, 2, 3], actions)
        self.assertTrue(result["exhausted"])
        self.assertEqual("no-next-bottom-card", result["reason"])



    def test_friend_action_probe_prefers_fast_visual_button_before_native_scans(self):
        namespace = load_functions(
            "_invoke_friend_visual_actions_before_home",
            "_invoke_friend_actions_before_home",
        )
        frame = object()
        events = []

        class Scheduler:
            def check_steal_all_icon(self, candidate):
                events.append("native-steal-all")
                return False

            def check_steal_one_icon(self, candidate):
                events.append("native-steal-one")
                return False

            def check_steal_icon(self, candidate):
                events.append("native-steal")
                return False

            def check_help_all_entry(self, candidate):
                events.append("native-help")
                return False

        namespace.update({
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[1])
            ),
            "_invoke_friend_guard_steal_visual_click": (
                lambda context, candidate: events.append("visual-steal") or False
            ),
            "_invoke_friend_guard_help_visual_click": (
                lambda context, candidate: events.append("visual-help") or True
            ),
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_actions_before_home"](
            Scheduler(), frame
        )

        self.assertTrue(acted)
        self.assertEqual("visual.friend_help_all", label)
        self.assertEqual(["visual-steal", "visual-help"], events)

    def test_friend_adjacent_navigation_does_not_guess_when_selected_border_is_unreadable(self):
        import numpy as np

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        clicks = []
        context = types.SimpleNamespace(
            _qqfarm_friend_action_last_label="visual.friend_help_all",
            _qqfarm_visual_friend_count=1,
        )
        namespace.update({
            "_friend_selected_carousel_card_bounds": lambda candidate: None,
            "_friend_adjacent_card_center": lambda candidate: None,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertFalse(moved)
        self.assertEqual("", label)
        self.assertEqual([], clicks)

    def test_friend_continuation_never_reopens_friend_list_inside_farm(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: events.append("native-friend-list")
                or (True, "method.native")
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("adjacent") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = False

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual(["adjacent"], events)
        self.assertEqual("no-next-bottom-card", result["reason"])

    def test_friend_continuation_drains_help_before_clicking_adjacent_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        state = {"help_done": False}

        def visual_action(context, candidate):
            if not state["help_done"]:
                state["help_done"] = True
                events.append("help-current-friend")
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: events.append("native-friend-list")
                or (False, "")
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("adjacent") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True
            friend_chain_idle_confirmations = 2

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_steal_all"
        )

        self.assertEqual(["help-current-friend", "adjacent"], events)
        self.assertEqual(1, result["actions"])
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_native_home_blocked_after_compiled_action_advances_to_adjacent_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 2
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_idle_confirmations = 2
            _qqfarm_friend_chain_native_home_blocked = True

        scheduler = Scheduler()
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertEqual(["adjacent"], moves)
        self.assertTrue(result["exhausted"])
        self.assertEqual("no-next-bottom-card", result["reason"])
        self.assertFalse(
            getattr(scheduler, "_qqfarm_friend_chain_native_home_blocked", True)
        )

    def test_friend_continuation_does_not_mark_unready_page_as_no_action(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []
        state_calls = {"count": 0}

        def friend_state(candidate):
            state_calls["count"] += 1
            # The current friend is stable long enough to permit the adjacent
            # click; the newly visited page then remains unreadable/loading.
            return state_calls["count"] <= 2

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent")
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": friend_state,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 2
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True
            friend_chain_idle_confirmations = 2

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual(["adjacent"], moves)
        self.assertFalse(result["exhausted"])
        self.assertEqual("friend-surface-not-ready", result["reason"])

    def test_friend_continuation_prefers_adjacent_card_when_fast_chain_is_enabled(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: events.append("native") or (False, "")
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("adjacent")
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_actions_before_home": (
                lambda context, candidate: (True, "visual.friend_help_all")
            ),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertEqual(["adjacent"], events)

    def test_friend_continuation_skips_slow_native_probe_when_visual_probe_is_available(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        calls = {"visual": 0, "native": 0}

        def visual_probe(context, candidate):
            calls["visual"] += 1
            return False, ""

        def native_probe(context, candidate):
            calls["native"] += 1
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_probe,
            "_invoke_friend_actions_before_home": native_probe,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: (100, 100, 100),
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual("first-no-action-friend", result["reason"])
        self.assertGreaterEqual(calls["visual"], 2)
        self.assertEqual(
            0,
            calls["native"],
            "a verified visual friend surface must not enter the multi-second native scan",
        )

    def test_native_help_claim_is_unverified_while_help_button_remains_visible(self):
        namespace = load_functions("_invoke_friend_actions_before_home")
        frame = object()
        messages = []
        captures = []

        class Scheduler:
            def check_help_all_entry(self, candidate):
                return True

        scheduler = Scheduler()
        namespace.update({
            "_invoke_friend_visual_actions_before_home": (
                lambda owner, candidate: (False, "")
            ),
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_friend_help_counter_snapshot": lambda owner: 10,
            "_get_frame_from_bot": (
                lambda owner: captures.append(frame) or frame
            ),
            "_friend_guard_help_button_match": (
                lambda candidate: {"matched": True, "center": (210, 640)}
            ),
            "_friend_guard_sleep": lambda seconds: None,
            "_write": messages.append,
        })

        acted, label = namespace["_invoke_friend_actions_before_home"](
            scheduler, frame
        )

        self.assertFalse(acted)
        self.assertEqual("", label)
        self.assertTrue(scheduler._qqfarm_friend_native_action_unverified)
        self.assertGreaterEqual(len(captures), 1)
        self.assertTrue(any("unverified" in message for message in messages))

    def test_first_friend_does_not_navigate_after_unverified_native_help_claim(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []

        def native_probe(owner, candidate):
            owner._qqfarm_friend_native_action_unverified = True
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent")
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": (
                lambda owner, candidate: (False, "")
            ),
            "_invoke_friend_actions_before_home": native_probe,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=2,
            friend_chain_action_poll_limit=8,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=4,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertEqual([], moves)
        self.assertEqual(0, result["moves"])
        self.assertFalse(result["exhausted"])
        self.assertEqual("initial-native-action-unverified", result["reason"])
        self.assertTrue(scheduler._qqfarm_friend_chain_pending)

    def test_guard_list_first_friend_runs_native_probe_before_advancing_after_visual_miss(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        calls = {"visual": 0, "native": 0}

        def visual_probe(context, candidate):
            calls["visual"] += 1
            events.append("visual")
            return False, ""

        def native_probe(context, candidate):
            calls["native"] += 1
            events.append("native-help")
            return True, "native.friend_help_all"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("navigate") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": visual_probe,
            "_invoke_friend_actions_before_home": native_probe,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda context: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=8,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=4,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertGreaterEqual(calls["visual"], 2)
        self.assertEqual(1, calls["native"])
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("native.friend_help_all", result["last_label"])
        if "navigate" in events:
            self.assertLess(events.index("native-help"), events.index("navigate"))
    def test_friend_continuation_runs_expensive_native_action_probe_only_once_per_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        calls = {"visual": 0, "native": 0}

        def visual_probe(context, candidate):
            calls["visual"] += 1
            return False, ""

        def native_probe(context, candidate):
            calls["native"] += 1
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_probe,
            "_invoke_friend_actions_before_home": native_probe,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: (100, 100, 100),
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True
            friend_chain_allow_native_action_fallback = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual("first-no-action-friend", result["reason"])
        self.assertGreaterEqual(calls["visual"], 2)
        self.assertEqual(1, calls["native"])


    def test_unreadable_friend_frame_skips_every_expensive_native_probe_after_visual_miss(self):
        namespace = load_functions(
            "_invoke_friend_visual_actions_before_home",
            "_invoke_friend_actions_before_home",
        )
        frame = object()
        native_calls = []

        class Scheduler:
            def check_steal_all_icon(self, candidate):
                native_calls.append("steal-all")
                return False

            def check_steal_one_icon(self, candidate):
                native_calls.append("steal-one")
                return False

            def check_steal_icon(self, candidate):
                native_calls.append("steal")
                return False

            def check_help_all_entry(self, candidate):
                native_calls.append("help")
                return False

        namespace.update({
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_invoke_friend_guard_steal_visual_click": lambda *args: False,
            "_invoke_friend_guard_help_visual_click": lambda *args: False,
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[1])
            ),
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_actions_before_home"](
            Scheduler(), frame
        )

        self.assertFalse(acted)
        self.assertEqual("", label)
        self.assertEqual([], native_calls)

    def test_guard_list_initial_no_action_friend_advances_to_next_actionable_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        first_frame = object()
        second_frame = object()
        third_frame = object()
        moves = []
        captures = iter((
            first_frame, first_frame, first_frame, first_frame,
            first_frame, first_frame, first_frame, first_frame,
            first_frame, first_frame, first_frame, first_frame,
            second_frame,
            second_frame, second_frame, second_frame,
            third_frame, third_frame, third_frame,
        ))
        acted_second = {"value": False}

        def visual_action(context, candidate):
            if candidate is second_frame and not acted_second["value"]:
                acted_second["value"] = True
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_friend_guard_list_refresh_prequalification": lambda *args: True,
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: moves.append(candidate)
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: next(captures, third_frame),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=3,
            friend_chain_action_poll_limit=8,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
            _qqfarm_guard_list_prequalified=True,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, first_frame, ""
        )

        self.assertGreaterEqual(len(moves), 2)
        self.assertIs(first_frame, moves[0])
        self.assertGreaterEqual(result["actions"], 1)
        self.assertTrue(result["exhausted"])
        self.assertEqual("first-no-action-friend", result["reason"])

    def test_friend_continuation_advances_list_cursor_by_bottom_carousel_moves(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: moves.append(candidate)
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=2,
            friend_chain_action_poll_limit=8,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            _qqfarm_friend_list_visit_cursor=1,
            _qqfarm_friend_list_visible_candidate_count=5,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(2, scheduler._qqfarm_friend_list_visit_cursor)
    def test_friend_continuation_stops_at_first_verified_no_action_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []

        def adjacent(context, candidate):
            moves.append(len(moves) + 1)
            return True, "visual.adjacent-friend-card"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 3
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual([1], moves)
        self.assertEqual(1, result["moves"])
        self.assertEqual(0, result["actions"])
        self.assertTrue(result["exhausted"])
        self.assertEqual("first-no-action-friend", result["reason"])

    def test_friend_continuation_processes_current_top_friend_before_moving_next(self):
        namespace = load_functions("_run_friend_continuation_chain")
        current_frame = object()
        next_frame = object()
        events = []
        current_action_calls = []

        def visual_action(context, candidate):
            current_action_calls.append(candidate)
            if candidate is current_frame:
                events.append(("action", candidate))
                return True, "visual.friend_help_all"
            return False, ""

        def adjacent(context, candidate):
            events.append(("move", candidate))
            return True, "visual.adjacent-friend-card"

        captures = iter((next_frame, next_frame, next_frame, next_frame))
        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: next(captures, next_frame),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 2
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), current_frame, ""
        )

        self.assertIs(current_frame, current_action_calls[0])
        self.assertEqual("action", events[0][0])
        self.assertEqual("move", events[1][0])
        self.assertGreaterEqual(result["actions"], 1)


    def test_friend_continuation_reads_adjacent_preference_from_active_config_when_context_lacks_attribute(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        acted = {"done": False}

        def visual_action(*args):
            if "adjacent" in events and not acted["done"]:
                acted["done"] = True
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: events.append("native") or (False, "")
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("adjacent")
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_active_bot_sections": lambda: ("bot", "instance.1.bot"),
            "_cfg_get": (
                lambda sections, key, default: "True"
                if key == "friend_chain_prefer_adjacent_navigation"
                else default
            ),
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertEqual(["adjacent"], events)


    def test_fast_visual_friend_action_rejects_self_farm_without_friend_surface_evidence(self):
        namespace = load_functions("_invoke_friend_visual_actions_before_home")
        frame = object()
        calls = []
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_friend_selected_carousel_card_bounds": lambda candidate: None,
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_invoke_friend_guard_steal_visual_click": (
                lambda *args: calls.append("steal") or False
            ),
            "_invoke_friend_guard_help_visual_click": (
                lambda *args: calls.append("help") or True
            ),
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_visual_actions_before_home"](
            types.SimpleNamespace(), frame
        )

        self.assertFalse(acted)
        self.assertEqual("", label)
        self.assertEqual([], calls)

    def test_fast_visual_friend_action_accepts_verified_friend_surface(self):
        namespace = load_functions("_invoke_friend_visual_actions_before_home")
        frame = object()
        calls = []
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_selected_carousel_card_bounds": lambda candidate: None,
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_invoke_friend_guard_steal_visual_click": (
                lambda *args: calls.append("steal") or False
            ),
            "_invoke_friend_guard_help_visual_click": (
                lambda *args: calls.append("help") or True
            ),
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_visual_actions_before_home"](
            types.SimpleNamespace(), frame
        )

        self.assertTrue(acted)
        self.assertEqual("visual.friend_help_all", label)
        self.assertEqual(["steal", "help"], calls)

    def test_visual_action_caches_selected_bottom_card_before_click(self):
        namespace = load_functions("_invoke_friend_visual_actions_before_home")
        frame = object()
        bounds = {
            "left": 24,
            "right": 119,
            "top": 675,
            "bottom": 757,
            "width": 95,
            "height": 82,
        }
        context = types.SimpleNamespace()
        namespace.update({
            "_friend_selected_carousel_card_bounds": lambda candidate: bounds,
            "_friend_action_frame_without_bottom_bar": lambda candidate: candidate,
            "_invoke_friend_guard_steal_visual_click": lambda *args: False,
            "_invoke_friend_guard_help_visual_click": lambda *args: True,
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_visual_actions_before_home"](
            context, frame
        )

        self.assertTrue(acted)
        self.assertEqual("visual.friend_help_all", label)
        self.assertEqual(
            bounds,
            getattr(context, "_qqfarm_friend_chain_last_selected_bounds", None),
        )

    def test_adjacent_navigation_uses_cached_selected_bounds_when_post_action_frame_hides_border(self):
        import numpy as np

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        clicks = []
        cached_bounds = {
            "left": 24,
            "right": 119,
            "top": 675,
            "bottom": 757,
            "width": 95,
            "height": 82,
        }
        context = types.SimpleNamespace(
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_last_selected_bounds=cached_bounds,
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_friend_selected_carousel_card_bounds": lambda candidate: None,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertFalse(moved)
        self.assertEqual("", label)
        self.assertEqual([], clicks)

    def test_live_carousel_clicks_the_immediate_right_friend_not_the_third_card(self):
        import cv2

        namespace = load_functions(
            "_friend_selected_carousel_card_bounds",
            "_friend_adjacent_card_center",
            "_invoke_friend_adjacent_card_navigation",
        )
        frame = cv2.imread(str(FIXTURES / "friend_carousel_action_order_live.png"))
        self.assertIsNotNone(frame)
        clicks = []
        context = types.SimpleNamespace(
            friend_chain_prefer_adjacent_navigation=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_action_last_ts=100.0,
            _qqfarm_friend_action_last_label="visual.friend_help_all",
            _qqfarm_visual_friend_count=1,
            _last_friend_farm_go_home_present=True,
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_watchdog_now": lambda: 100.2,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertTrue(moved)
        self.assertEqual("visual.adjacent-friend-card", label)
        self.assertEqual(1, len(clicks))
        x, y, width, height = clicks[0]
        self.assertEqual((642, 1140), (width, height))
        self.assertTrue(240 <= x <= 275, clicks[0])
        self.assertTrue(1000 <= y <= 1040, clicks[0])

    def test_bottom_carousel_mode_never_falls_back_to_friend_list_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        native_calls = []
        namespace.update({
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: native_calls.append((args, kwargs)) or (True, "native.friend-list")
            ),
            "_invoke_friend_adjacent_card_navigation": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_visual_actions_before_home": lambda *args: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: (1, 2, 3),
            "_friend_navigation_change_score": lambda signature, candidate: 0.0,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), frame, "visual.friend_help_all"
        )

        self.assertEqual([], native_calls)
        self.assertEqual(0, result["moves"])
        self.assertTrue(result["exhausted"])
        self.assertEqual("no-next-bottom-card", result["reason"])

    def test_bottom_carousel_waits_past_legacy_eight_polls_for_late_in_farm_button(self):
        namespace = load_functions("_run_friend_continuation_chain")
        start_frame = object()
        transition_frame = object()
        actionable_frame = object()
        captures = iter(([transition_frame] * 9) + [actionable_frame])
        action_frames = []
        action_done = {"value": False}

        def visual_action(context, candidate):
            action_frames.append(candidate)
            if candidate is actionable_frame and not action_done["value"]:
                action_done["value"] = True
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: next(captures, actionable_frame),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: (10, 20, 30),
            "_friend_navigation_change_score": lambda signature, candidate: 0.03,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), start_frame, "visual.friend_help_all"
        )

        self.assertGreaterEqual(len(action_frames), 10)
        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertEqual("action-complete", result["reason"])

    def test_fast_friend_chain_uses_each_detected_immediate_right_card_across_moves(self):
        import numpy as np

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        selected_bounds = iter([
            {"left": 36, "right": 132, "top": 682, "bottom": 760},
            {"left": 138, "right": 234, "top": 682, "bottom": 760},
        ])
        detected_centers = iter([(185, 721), (287, 721)])
        clicks = []
        context = types.SimpleNamespace(
            _qqfarm_friend_action_last_label="visual.friend_help_all",
            _qqfarm_visual_friend_count=1,
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_selected_carousel_card_bounds": lambda candidate: next(selected_bounds),
            "_friend_adjacent_card_center": lambda candidate: next(detected_centers),
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })

        first = namespace["_invoke_friend_adjacent_card_navigation"](context, frame)
        second = namespace["_invoke_friend_adjacent_card_navigation"](context, frame)

        self.assertEqual((True, "visual.adjacent-friend-card"), first)
        self.assertEqual((True, "visual.adjacent-friend-card"), second)
        self.assertEqual([(185, 721), (287, 721)], [(x, y) for x, y, _, _ in clicks])


    def test_fast_adjacent_navigation_requires_live_carousel_when_friend_state_is_false_positive(self):
        import numpy as np

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        clicks = []
        context = types.SimpleNamespace(
            friend_chain_prefer_adjacent_navigation=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_action_last_ts=0.0,
            _qqfarm_friend_action_last_label="",
            _qqfarm_visual_friend_count=0,
            _last_friend_farm_go_home_present=True,
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_selected_carousel_card_bounds": lambda candidate: None,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertFalse(moved)
        self.assertEqual("", label)
        self.assertEqual([], clicks)

    def test_fast_adjacent_navigation_does_not_click_stale_self_farm_frame(self):
        import numpy as np

        namespace = load_functions("_invoke_friend_adjacent_card_navigation")
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        clicks = []
        context = types.SimpleNamespace(
            friend_chain_prefer_adjacent_navigation=True,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_action_last_label="visual.friend_help_all",
            _qqfarm_friend_action_last_ts=0.0,
            _qqfarm_visual_friend_count=0,
            _last_friend_farm_go_home_present=False,
        )
        namespace.update({
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_friend_adjacent_card_center": lambda candidate: (171, 721),
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y)) or True
            ),
            "_write": lambda message: None,
        })

        moved, label = namespace["_invoke_friend_adjacent_card_navigation"](
            context, frame
        )

        self.assertFalse(moved)
        self.assertEqual("", label)
        self.assertEqual([], clicks)

    def test_friend_continuation_marks_fixed_navigation_as_active_only_during_chain(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        active_markers = []

        handled_moves = set()

        def adjacent(context, candidate):
            active_markers.append(bool(getattr(context, "_qqfarm_friend_chain_active", False)))
            return True, "visual.adjacent-friend-card"

        def visual_action(*args):
            move_number = len(active_markers)
            if move_number > 0 and move_number not in handled_moves:
                handled_moves.add(move_number)
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 2
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        scheduler = Scheduler()
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertEqual(2, result["moves"])
        self.assertEqual([True, True], active_markers)
        self.assertFalse(getattr(scheduler, "_qqfarm_friend_chain_active", False))


    def test_current_friend_list_layout_is_recognized_from_visit_button_rows(self):
        import cv2

        detect = load_function("_friend_list_visit_button_rows")
        self.assertIsNotNone(detect)
        frame = cv2.imread(str(FIXTURES / "friend_list_stuck_428x800.png"))

        rows = detect(frame)

        self.assertGreaterEqual(len(rows), 5)
        self.assertTrue(355 <= rows[0]["center"][0] <= 375)
        self.assertTrue(280 <= rows[0]["center"][1] <= 300)

    def test_current_friend_list_state_uses_row_layout_when_old_tabs_template_misses(self):
        import cv2

        namespace = load_functions(
            "_friend_guard_read_template",
            "_friend_guard_match_template",
            "_friend_list_visit_button_rows",
            "_friend_guard_friend_ui_state",
        )
        namespace["_FRIEND_GUARD_TEMPLATE_CACHE"] = {}
        namespace["_FRIEND_HOME_TEMPLATE_PATH"] = str(FIXTURES / "friend_home_button.png")
        namespace["_FRIEND_LIST_TEMPLATE_PATH"] = str(FIXTURES / "friend_list_tabs.png")
        frame = cv2.imread(str(FIXTURES / "friend_list_stuck_428x800.png"))

        self.assertIsNone(namespace["_friend_guard_friend_ui_state"](frame))

    def test_current_friend_list_guard_dog_score_rejects_flower_avatar_frame(self):
        import cv2

        score = load_function("_friend_list_guard_dog_score")
        self.assertIsNotNone(score)
        frame = cv2.imread(str(FIXTURES / "friend_list_stuck_428x800.png"))
        guard_template = frame[297:316, 59:78].copy()
        score.__globals__.update({
            "_friend_guard_read_template": lambda path: guard_template,
            "_FRIEND_GUARD_DOG_AVATAR_TEMPLATE_PATH": "fixture-guard-dog.png",
        })

        self.assertGreaterEqual(score(frame, 289), 0.82)
        self.assertLess(score(frame, 383), 0.82)
        self.assertGreaterEqual(score(frame, 478), 0.82)

    def test_visual_watchdog_handles_friend_list_before_friend_farm_recovery(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        handled = []
        events = []
        namespace.update({
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: None,
            "_handle_friend_list_surface": (
                lambda context, candidate: handled.append((context, candidate)) or "visited"
            ),
            "_invoke_friend_actions_before_home": (
                lambda *args: events.append("friend-action") or (False, "")
            ),
            "_write": lambda message: events.append(message),
        })

        scheduler = type("Scheduler", (), {"_qqfarm_friend_cycle_seen": True})()
        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda: None, scheduler, "FarmBotCV.run_cycle"
        )

        self.assertFalse(result)
        self.assertEqual([(scheduler, frame)], handled)
        self.assertNotIn("friend-action", events)

    def test_friend_list_handler_visits_first_guard_dog_action_row(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        frame = object()
        clicks = []
        rows = [
            {"center": (365, 289), "rect": (331, 271, 399, 307)},
            {"center": (367, 383), "rect": (333, 365, 401, 401)},
        ]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_friend_list_guard_dog_score": (
                lambda candidate, row_y: 0.95 if row_y == 289 else 0.20
            ),
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })
        class Frame:
            shape = (800, 428, 3)

        result = handler(object(), Frame())

        self.assertEqual("visited", result)
        self.assertEqual([(365, 289, 428, 800)], clicks)

    def test_friend_list_handler_never_advances_unconfirmed_pending_row(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        logs = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (365, 288)},
            {"center": (365, 383)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y)) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: logs.append(message),
        })
        scheduler = types.SimpleNamespace(_qqfarm_friend_list_visit_cursor=0)

        results = [
            namespace["_handle_friend_list_surface"](scheduler, frame)
            for _ in range(4)
        ]

        self.assertEqual(
            ["visited", "visited", "visited", "pending-row-backoff"],
            results,
        )
        self.assertEqual([(365, 288)] * 3, clicks)
        self.assertEqual(0, scheduler._qqfarm_friend_list_visit_cursor)
        self.assertTrue(any("pending row retry" in message for message in logs))
        self.assertTrue(any("pending row backoff" in message for message in logs))
        self.assertFalse(any("pending row exhausted" in message for message in logs))

    def test_pending_friend_row_reopens_list_after_entry_timeout_without_advancing(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        fast_modes = []
        logs = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (365, 288)},
            {"center": (365, 383)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y)) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": (
                lambda context, active: fast_modes.append(active) or True
            ),
            "_friend_guard_clear_prequalification": lambda context: True,
            "_write": lambda message: logs.append(message),
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=0,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_clicked_ts=90.0,
            _qqfarm_friend_entry_last_retry_ts=99.0,
        )

        result = namespace["_handle_friend_list_surface"](scheduler, frame)

        self.assertEqual("pending-row-reopen", result)
        self.assertEqual([(405, 94)], clicks)
        self.assertEqual(0, scheduler._qqfarm_friend_list_visit_cursor)
        self.assertFalse(scheduler._qqfarm_friend_entry_pending)
        self.assertEqual(0, scheduler._qqfarm_friend_entry_retry_count)
        self.assertEqual([False], fast_modes)
        self.assertTrue(any("reopen recovery" in message for message in logs))

    def test_friend_list_entry_cursor_advances_only_after_confirmed_transition(self):
        namespace = load_functions("_commit_friend_list_entry_transition")
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_list_pending_cursor=4,
            _qqfarm_friend_list_visit_cursor=4,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_last_retry_ts=100.0,
        )

        committed = namespace["_commit_friend_list_entry_transition"](scheduler)

        self.assertTrue(committed)
        self.assertEqual(5, scheduler._qqfarm_friend_list_visit_cursor)
        self.assertEqual(0, scheduler._qqfarm_friend_entry_retry_count)
        self.assertEqual(0.0, scheduler._qqfarm_friend_entry_last_retry_ts)
        self.assertTrue(any("confirmed cursor" in message for message in logs))
    def test_friend_list_handler_reopens_from_first_visible_guard_row(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        rows = [
            {"center": (365, 289), "rect": (331, 271, 399, 307)},
            {"center": (367, 383), "rect": (333, 365, 401, 401)},
        ]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        scheduler = types.SimpleNamespace(_qqfarm_friend_list_visit_cursor=1)
        result = handler(scheduler, Frame())

        self.assertEqual("visited", result)
        self.assertEqual([(365, 289, 428, 800)], clicks)
        self.assertEqual(0, scheduler._qqfarm_friend_list_visit_cursor)
        commit_namespace = load_functions("_commit_friend_list_entry_transition")
        commit_namespace["_write"] = lambda message: None
        self.assertTrue(
            commit_namespace["_commit_friend_list_entry_transition"](scheduler)
        )
        self.assertEqual(1, scheduler._qqfarm_friend_list_visit_cursor)
        self.assertEqual(2, scheduler._qqfarm_friend_list_visible_candidate_count)
    def test_friend_list_visit_marks_transition_pending_until_friend_surface_arrives(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        rows = [{"center": (365, 289), "rect": (331, 271, 399, 307)}]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_guard_post_client_click": lambda *args, **kwargs: True,
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        scheduler = types.SimpleNamespace()
        result = handler(scheduler, Frame())

        self.assertEqual("visited", result)
        self.assertTrue(scheduler._qqfarm_friend_entry_pending)
        self.assertEqual(100.0, scheduler._qqfarm_friend_entry_clicked_ts)

    def test_friend_list_handler_closes_and_does_not_loop_when_no_action_rows(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_friend_guard_post_client_click": (
                lambda x, y, width, height: clicks.append((x, y, width, height)) or True
            ),
            "_write": lambda message: None,
        })
        class Frame:
            shape = (800, 428, 3)

        result = handler(object(), Frame())

        self.assertEqual("closed", result)
        self.assertEqual(1, len(clicks))
        x, y, width, height = clicks[0]
        self.assertTrue(395 <= x <= 414)
        self.assertTrue(80 <= y <= 105)
        self.assertEqual((428, 800), (width, height))

    def test_guard_dog_feature_wrapper_follows_enabled_ui_even_when_original_gate_is_false(self):
        namespace = load_functions("_wrap_guard_dog_enabled_func")
        original_calls = []
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_runtime_info_once": lambda *args, **kwargs: None,
        })

        wrapped, changed = namespace["_wrap_guard_dog_enabled_func"](
            lambda *args, **kwargs: original_calls.append((args, kwargs)) or False,
            "checks_friend._guard_dog_feature_enabled",
        )

        self.assertTrue(changed)
        self.assertTrue(wrapped(object()))
        self.assertEqual([], original_calls)

    def test_guard_dog_feature_wrapper_stays_off_when_ui_is_disabled(self):
        namespace = load_functions("_wrap_guard_dog_enabled_func")
        original_calls = []
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: False,
            "_runtime_info_once": lambda *args, **kwargs: None,
        })

        wrapped, changed = namespace["_wrap_guard_dog_enabled_func"](
            lambda *args, **kwargs: original_calls.append((args, kwargs)) or True,
            "checks_friend._guard_dog_feature_enabled",
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(object()))
        self.assertEqual([], original_calls)


    def test_guard_dog_rejected_initial_help_stays_on_current_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        start_frame = object()
        next_frame = object()
        moves = []

        def visual_action(context, frame):
            if frame is start_frame:
                setattr(context, "_qqfarm_guard_dog_help_skipped", True)
            return False, ""

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda context, frame: moves.append(frame)
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: next_frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 16
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_idle_confirmations = 2
            friend_chain_prefer_adjacent_navigation = True

        scheduler = Scheduler()
        result = namespace["_run_friend_continuation_chain"](
            scheduler, start_frame, ""
        )

        self.assertEqual([], moves)
        self.assertEqual(0, result["moves"])
        self.assertEqual("initial-guard-approval-pending", result["reason"])
        self.assertTrue(getattr(scheduler, "_qqfarm_friend_chain_pending", False))
        self.assertFalse(
            getattr(scheduler, "_qqfarm_guard_dog_help_skipped", False)
        )

    def test_guard_dog_mode_advances_until_first_friend_without_action(self):
        namespace = load_functions("_run_friend_continuation_chain")
        start_frame = object()
        actionable_frame = object()
        empty_frame = object()
        moves = []
        captures = iter((
            start_frame, start_frame, start_frame,
            actionable_frame, actionable_frame, actionable_frame, actionable_frame,
            empty_frame, empty_frame, empty_frame,
        ))

        def adjacent(context, frame):
            moves.append(frame)
            return True, "visual.adjacent-friend-card"

        action_done = {"value": False}

        def visual_action(context, frame):
            if frame is actionable_frame and not action_done["value"]:
                action_done["value"] = True
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": visual_action,
            "_invoke_friend_actions_before_home": visual_action,
            "_get_frame_from_bot": lambda context: next(captures, empty_frame),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 4
            friend_chain_action_poll_limit = 8
            friend_chain_primary_navigation_poll_limit = 2
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), start_frame, "visual.friend_help_all"
        )

        self.assertEqual([start_frame, actionable_frame], moves)
        self.assertEqual(2, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertTrue(result["exhausted"])
        self.assertEqual("first-no-action-friend", result["reason"])

    def test_friend_continuation_rejects_stale_previous_friend_action_until_navigation_changes(self):
        namespace = load_functions("_run_friend_continuation_chain")
        previous_frame = object()
        next_friend_frame = object()
        state = {"moved": False}
        captures = iter((
            previous_frame, previous_frame, previous_frame,
            previous_frame,
            next_friend_frame, next_friend_frame,
            next_friend_frame, next_friend_frame, next_friend_frame,
        ))
        action_frames = []

        def adjacent(context, frame):
            state["moved"] = True
            return True, "visual.adjacent-friend-card"

        def fast_action(context, frame):
            if not state["moved"]:
                return False, ""
            action_frames.append(frame)
            return True, "visual.friend_help_all"

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: False,
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": fast_action,
            "_get_frame_from_bot": lambda context: next(captures, next_friend_frame),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": (
                lambda candidate: (0,) if candidate is previous_frame else (255,)
            ),
            "_friend_navigation_change_score": (
                lambda signature, candidate: 0.0 if candidate is previous_frame else 1.0
            ),
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 16
            friend_chain_primary_navigation_poll_limit = 3
            friend_chain_idle_confirmations = 3
            friend_chain_prefer_adjacent_navigation = True

        result = namespace["_run_friend_continuation_chain"](
            Scheduler(), previous_frame, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, result["actions"])
        self.assertTrue(action_frames)
        self.assertIs(
            next_friend_frame,
            action_frames[0],
            "the previous friend's residual one-click button must not confirm navigation",
        )

    def test_guard_dog_mode_persists_to_both_friend_sections_and_json(self):
        import json
        import os
        import tempfile

        persist = load_function("_persist_guard_dog_mode")
        self.assertTrue(callable(persist))
        persist.__globals__.update({"os": os})

        with tempfile.TemporaryDirectory() as temp_dir:
            ini_path = Path(temp_dir) / "config-multi.ini"
            json_path = Path(temp_dir) / "config.json"
            ini_path.write_text(
                "[friend]\nenable_guard_dog_help_only = False\n"
                "[instance.1.friend]\nenable_guard_dog_help_only = False\n",
                encoding="utf-8",
            )
            json_path.write_text(
                json.dumps({
                    "tasks": {
                        "friend": {
                            "features": {"help_only_guard_dog": False}
                        }
                    }
                }),
                encoding="utf-8",
            )

            self.assertTrue(persist(
                True,
                ini_paths=[str(ini_path)],
                json_paths=[str(json_path)],
            ))

            ini_text = ini_path.read_text(encoding="utf-8")
            self.assertEqual(2, ini_text.count("enable_guard_dog_help_only = True"))
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(
                data["tasks"]["friend"]["features"]["help_only_guard_dog"]
            )


    def test_friend_guard_list_template_ready_detects_active_instance_images(self):
        import tempfile

        namespace = load_functions(
            "_friend_guard_template_status",
            "_friend_guard_list_template_ready",
        )
        ready = namespace.get("_friend_guard_list_template_ready")
        self.assertIsNotNone(ready)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse(ready(instance_ids=("1",), template_root=root))
            guard_dir = root / "instances" / "1" / "friend_list" / "guard"
            guard_dir.mkdir(parents=True)
            (guard_dir / "friend-a.png").write_bytes(b"template")
            self.assertTrue(ready(instance_ids=("1",), template_root=root))
            self.assertFalse(ready(instance_ids=("2",), template_root=root))

    def test_guard_dog_detection_mode_falls_back_when_friend_guard_list_is_empty(self):
        namespace = load_functions("_guard_dog_detection_mode_config")
        detect_mode = namespace["_guard_dog_detection_mode_config"]
        logs = []
        namespace.update({
            "_cfg_get": lambda sections, key, default: "friend_guard_list",
            "_active_friend_sections": lambda: ("friend",),
            "_friend_guard_list_template_ready": lambda: False,
            "_friend_guard_template_status": lambda: {
                "instance_ids": ("1",),
                "directories": (r"C:\fixture\instances\1\friend_list\guard",),
                "count": 0,
            },
            "_throttled_write": lambda key, message, seconds=30.0: logs.append(message),
        })

        self.assertEqual("avatar_frame", detect_mode())
        self.assertTrue(any("fallback=dog_badge" in line for line in logs))

    def test_guard_dog_detection_mode_ignores_unconfirmed_candidate_templates(self):
        namespace = load_functions("_guard_dog_detection_mode_config")
        detect_mode = namespace["_guard_dog_detection_mode_config"]
        logs = []
        namespace.update({
            "_cfg_get": lambda sections, key, default: "friend_guard_list",
            "_active_friend_sections": lambda: ("friend",),
            "_friend_guard_list_confirmed_config": lambda: False,
            "_friend_guard_list_template_ready": lambda: True,
            "_friend_guard_template_status": lambda: {
                "instance_ids": ("1",),
                "directories": (r"C:\fixture\instances\1\friend_list\guard",),
                "count": 5,
            },
            "_throttled_write": lambda key, message, seconds=30.0: logs.append(message),
        })

        self.assertEqual("avatar_frame", detect_mode())
        self.assertTrue(any("unconfirmed" in line for line in logs))
        self.assertTrue(any("fallback=dog_badge" in line for line in logs))

    def test_guard_dog_detection_mode_keeps_friend_guard_list_when_templates_exist(self):
        namespace = load_functions("_guard_dog_detection_mode_config")
        detect_mode = namespace["_guard_dog_detection_mode_config"]
        namespace.update({
            "_cfg_get": lambda sections, key, default: "friend_guard_list",
            "_active_friend_sections": lambda: ("friend",),
            "_friend_guard_list_confirmed_config": lambda: True,
            "_friend_guard_list_template_ready": lambda: True,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        self.assertEqual("friend_guard_list", detect_mode())

    def test_guard_dog_mode_wrapper_uses_friend_guard_list_config(self):
        namespace = load_functions("_wrap_guard_dog_mode_func")
        wrapper = namespace.get("_wrap_guard_dog_mode_func")
        if wrapper is None:
            self.fail("_wrap_guard_dog_mode_func is missing")
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
        })

        mode_fn, mode_changed = wrapper(
            lambda *args, **kwargs: "avatar_frame",
            "checks_friend._guard_dog_detection_mode",
        )
        list_fn, list_changed = wrapper(
            lambda *args, **kwargs: False,
            "checks_friend.is_friend_guard_list_help_only_mode",
        )

        self.assertTrue(mode_changed)
        self.assertTrue(list_changed)
        self.assertEqual("friend_guard_list", mode_fn(object()))
        self.assertTrue(list_fn(object()))

    def test_friend_trouble_counter_snapshot_uses_max_same_day_instance_and_root_value(self):
        import json
        import tempfile

        snapshot = load_function("_friend_trouble_counter_snapshot")
        self.assertIsNotNone(snapshot)
        today = "2026-07-28"

        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            first.write_text(json.dumps({
                "friend_trouble_daily_date": today,
                "friend_trouble_daily_count": 2,
                "instances": {
                    "1": {
                        "friend_trouble_daily_date": today,
                        "friend_trouble_daily_count": 4,
                    }
                },
            }), encoding="utf-8")
            second.write_text(json.dumps({
                "friend_trouble_daily_date": "2026-07-27",
                "friend_trouble_daily_count": 99,
            }), encoding="utf-8")

            context = types.SimpleNamespace(
                instance_id="1",
                friend_trouble_daily_date=today,
                friend_trouble_daily_count=3,
            )
            self.assertEqual(4, snapshot(
                context,
                counter_paths=[first, second],
                today=today,
            ))

    def test_single_harvest_forces_immediate_harvest_planting_quota(self):
        namespace = load_functions(
            "_note_runtime_single_harvest_outcome",
            "_wrap_home_harvest_planting_trigger",
        )
        self.assertIn("_note_runtime_single_harvest_outcome", namespace)
        self.assertIn("_wrap_home_harvest_planting_trigger", namespace)
        scheduler = types.SimpleNamespace(planting_harvest_quota=0)
        frame = object()
        logs = []

        def native_harvest(owner, game_frame):
            namespace["_note_runtime_single_harvest_outcome"](
                "??????????????????????????"
            )
            return False

        namespace.update({
            "_SINGLE_HARVEST_EVENT_TOKEN": 0,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_write": logs.append,
        })
        wrapped, changed = namespace["_wrap_home_harvest_planting_trigger"](
            native_harvest, "bot.flows.handle_home_harvest"
        )

        result = wrapped(scheduler, frame)

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual(1, scheduler.planting_harvest_quota)
        self.assertTrue(any("single harvest queued planting" in line for line in logs))

    def test_deferred_troublemaker_runs_only_after_friend_chain_exhaustion(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        calls = []
        frame = object()

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True

            def _run_friend_daily_troublemaker(self, game_frame):
                calls.append(game_frame)
                return "trouble-done"

        scheduler = Scheduler()
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })

        self.assertEqual("trouble-done", runner(scheduler, frame))
        self.assertEqual([frame], calls)
        self.assertTrue(
            getattr(scheduler, "_qqfarm_friend_chain_troublemaker_ran", False)
        )

    def test_deferred_troublemaker_uses_cached_module_callable_with_fresh_frame(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        stale_frame = type("Frame", (), {"shape": (10, 10, 3)})()
        fresh_frame = type("Frame", (), {"shape": (20, 20, 3)})()
        observed = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()

        def module_troublemaker(target, game_frame):
            observed.append((target, game_frame))
            return "module-trouble-done"

        scheduler._qqfarm_friend_chain_deferred_troublemaker = module_troublemaker
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (
            scheduler, stale_frame
        )
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_write": lambda message: None,
        })

        result = runner(scheduler, fresh_frame)

        self.assertEqual("module-trouble-done", result)
        self.assertEqual([(scheduler, fresh_frame)], observed)
        self.assertTrue(
            getattr(scheduler, "_qqfarm_friend_chain_troublemaker_ran", False)
        )

    def test_deferred_troublemaker_discovers_runtime_module_callable_when_context_cache_is_missing(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True

        scheduler = Scheduler()

        def runtime_troublemaker(target, game_frame):
            calls.append((target, game_frame))
            return "runtime-module-trouble-done"

        runtime_module = types.SimpleNamespace(
            _run_friend_daily_troublemaker=runtime_troublemaker,
        )
        runner.__globals__.update({
            "sys": types.SimpleNamespace(
                modules={"bot.runtime.friend_actions": runtime_module}
            ),
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_write": lambda message: None,
        })

        result = runner(scheduler, frame)

        self.assertEqual("runtime-module-trouble-done", result)
        self.assertEqual([(scheduler, frame)], calls)
        self.assertIs(
            runtime_troublemaker,
            getattr(scheduler, "_qqfarm_friend_chain_deferred_troublemaker", None),
        )

    def test_deferred_troublemaker_retries_on_next_friend_until_counter_increments(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)

        class Frame:
            shape = (800, 428, 3)

        first_frame = Frame()
        second_frame = Frame()
        calls = []
        moves = []
        counter = {"value": 0}

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}
            friend_troublemaker_adjacent_retry_limit = 2

        scheduler = Scheduler()

        def troublemaker(target, game_frame):
            calls.append(game_frame)
            if len(calls) == 2:
                counter["value"] += 1
                return True
            return False

        scheduler._qqfarm_friend_chain_deferred_troublemaker = troublemaker
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (
            scheduler,
            first_frame,
        )
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": lambda owner: counter["value"],
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, frame: moves.append(frame)
                or (True, "visual.adjacent-friend-card")
            ),
            "_get_frame_from_bot": lambda owner: second_frame,
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_write": lambda message: None,
        })

        self.assertTrue(runner(scheduler, first_frame))
        self.assertEqual([first_frame, second_frame], calls)
        self.assertEqual([first_frame], moves)
        self.assertEqual(1, counter["value"])
        self.assertTrue(scheduler._qqfarm_friend_chain_troublemaker_ran)

    def test_deferred_troublemaker_default_full_miss_is_bounded_to_three_friends(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        calls = []
        moves = []
        frames = [object(), object(), object(), object(), object()]

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()

        def troublemaker(target):
            calls.append(target)
            return False

        scheduler._qqfarm_friend_chain_deferred_troublemaker = troublemaker
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        capture_index = {"value": 1}

        def capture(owner):
            index = min(capture_index["value"], len(frames) - 1)
            capture_index["value"] += 1
            return frames[index]

        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": lambda owner: 0,
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, frame: moves.append(frame)
                or (True, "visual.adjacent-friend-card")
            ),
            "_get_frame_from_bot": capture,
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_watchdog_now": lambda: 100.0,
            "_write": lambda message: None,
        })

        self.assertFalse(runner(scheduler, frames[0]))
        self.assertEqual(3, len(calls))
        self.assertEqual(2, len(moves))

    def test_deferred_troublemaker_false_result_remains_retryable(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()
        cached = lambda target: False
        scheduler._qqfarm_friend_chain_deferred_troublemaker = cached
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_write": lambda message: None,
        })

        self.assertFalse(runner(scheduler, object()))
        self.assertFalse(
            getattr(scheduler, "_qqfarm_friend_chain_troublemaker_ran", False)
        )
        self.assertIs(
            cached,
            getattr(
                scheduler,
                "_qqfarm_friend_chain_deferred_troublemaker",
                None,
            ),
        )

    def test_deferred_troublemaker_truthy_without_counter_increment_remains_retryable(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        snapshots = iter((0, 0))
        snapshot_calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()
        scheduler._qqfarm_friend_chain_deferred_troublemaker = (
            lambda target: True
        )
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": (
                lambda context: snapshot_calls.append(context) or next(snapshots)
            ),
            "_write": lambda message: None,
        })

        self.assertFalse(runner(scheduler, object()))
        self.assertEqual([scheduler, scheduler], snapshot_calls)
        self.assertFalse(
            getattr(scheduler, "_qqfarm_friend_chain_troublemaker_ran", False)
        )

    def test_deferred_troublemaker_full_miss_uses_cooldown_before_rescanning(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}
            friend_troublemaker_full_miss_cooldown_seconds = 90.0

        scheduler = Scheduler()

        def troublemaker(target):
            calls.append(target)
            return False

        scheduler._qqfarm_friend_chain_deferred_troublemaker = troublemaker
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": lambda owner: 0,
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, frame: (False, "")
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_write": lambda message: None,
        })

        self.assertFalse(runner(scheduler, object()))
        self.assertEqual(1, len(calls))
        self.assertGreater(
            getattr(scheduler, "_qqfarm_troublemaker_full_miss_until", 0.0),
            100.0,
        )

        scheduler._qqfarm_friend_chain_exhausted = True
        self.assertFalse(runner(scheduler, object()))
        self.assertEqual(1, len(calls))
    def test_deferred_troublemaker_counter_increment_marks_success(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        snapshots = iter((0, 2))
        snapshot_calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()
        scheduler._qqfarm_friend_chain_deferred_troublemaker = (
            lambda target: True
        )
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": (
                lambda context: snapshot_calls.append(context) or next(snapshots)
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(runner(scheduler, object()))
        self.assertEqual([scheduler, scheduler], snapshot_calls)
        self.assertTrue(
            getattr(scheduler, "_qqfarm_friend_chain_troublemaker_ran", False)
        )

    def test_private_native_home_check_is_registered_for_visual_gating(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(HOOK))
        value = None
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if any(
                isinstance(target, ast.Name)
                and target.id == "_FRIEND_HOME_FUNC_NAMES"
                for target in node.targets
            ):
                value = ast.literal_eval(node.value.args[0])
                break
        self.assertIsNotNone(value)
        self.assertIn("_has_go_home_icon", value)

    def test_private_native_home_check_rejects_self_surface_false_positive(self):
        namespace = load_functions("_wrap_friend_home_func")
        calls = []
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        scheduler = types.SimpleNamespace()
        namespace.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_chain_should_block_home": lambda context: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_watchdog_now": lambda: 100.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        def native_home(owner, game_frame):
            calls.append(game_frame)
            return True

        wrapped, changed = namespace["_wrap_friend_home_func"](
            native_home, "FarmBotCV._has_go_home_icon"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual([], calls)
        self.assertEqual(100.0, scheduler._qqfarm_native_home_false_positive_ts)

    def test_native_home_check_rejects_self_surface_false_positive(self):
        namespace = load_functions("_wrap_friend_home_func")
        calls = []
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        scheduler = types.SimpleNamespace()
        namespace.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_chain_should_block_home": lambda context: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_watchdog_now": lambda: 100.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        def native_home(owner, game_frame):
            calls.append(game_frame)
            return True

        wrapped, changed = namespace["_wrap_friend_home_func"](
            native_home, "FarmBotCV.check_go_home_icon"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual([], calls)
        self.assertEqual(100.0, scheduler._qqfarm_native_home_false_positive_ts)

    def test_native_home_false_positive_clears_friend_state_immediately(self):
        namespace = load_functions("_wrap_friend_home_func")
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        finalized = []
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_cycle_seen=True,
        )

        def finalize(owner):
            finalized.append(owner)
            owner._qqfarm_friend_chain_pending = False
            owner._qqfarm_friend_chain_active = False
            owner._qqfarm_friend_chain_exhausted = False
            return True

        namespace.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_chain_should_block_home": lambda context: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_watchdog_now": lambda: 100.0,
            "_finalize_friend_chain_after_troublemaker": finalize,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        wrapped, _ = namespace["_wrap_friend_home_func"](
            lambda owner, game_frame: True,
            "FarmBotCV.check_go_home_icon",
        )

        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual([scheduler], finalized)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_active)
        self.assertTrue(getattr(scheduler, "_qqfarm_force_self_cycle_next", False))

    def test_native_home_false_positive_clears_active_run_cycle_context(self):
        namespace = load_functions("_wrap_friend_home_func")
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        native_owner = types.SimpleNamespace(
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_cycle_branch_hint="friend",
        )
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_cycle_branch_hint="friend",
        )
        finalized = []

        def finalize(owner):
            finalized.append(owner)
            owner._qqfarm_friend_chain_pending = False
            owner._qqfarm_friend_chain_active = False
            owner._qqfarm_friend_chain_exhausted = False
            return True

        namespace.update({
            "_ACTIVE_RUN_CYCLE_CONTEXT": scheduler,
            "_friend_guard_context": lambda args, kwargs: native_owner,
            "_friend_chain_should_block_home": lambda context: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_watchdog_now": lambda: 100.0,
            "_finalize_friend_chain_after_troublemaker": finalize,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        wrapped, _ = namespace["_wrap_friend_home_func"](
            lambda owner, game_frame: True,
            "FarmBotCV.check_go_home_icon",
        )

        self.assertFalse(wrapped(native_owner, frame))
        self.assertEqual([native_owner, scheduler], finalized)
        self.assertEqual(100.0, scheduler._qqfarm_native_home_false_positive_ts)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)

    def test_mark_friend_cycle_seen_ignores_recent_native_home_false_positive(self):
        mark = load_function("_mark_friend_cycle_seen")
        scheduler = types.SimpleNamespace(
            _qqfarm_native_home_false_positive_ts=99.0,
            _qqfarm_friend_cycle_seen=False,
            _qqfarm_cycle_branch_hint="self",
        )
        mark.__globals__.update({
            "_ACTIVE_RUN_CYCLE_CONTEXT": scheduler,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_watchdog_now": lambda: 100.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        found = mark((scheduler,), {})

        self.assertIs(found, scheduler)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)

    def test_recent_native_home_false_positive_suppresses_watchdog_friend_fallback(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        finalized = []
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_native_home_false_positive_ts=99.0,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_visual_friend_count=2,
        )

        def finalize(owner):
            finalized.append(owner)
            owner._qqfarm_friend_chain_pending = False
            owner._qqfarm_friend_chain_active = False
            owner._qqfarm_friend_chain_exhausted = False
            return True

        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_false_friend_branch_cooldown_active": lambda *args: False,
            "_finalize_friend_chain_after_troublemaker": finalize,
            "_set_friend_chain_fast_interval": lambda *args: True,
            "_friend_chain_should_block_troublemaker": (
                lambda owner: bool(owner._qqfarm_friend_chain_pending)
            ),
            "_FRIEND_HOME_LAST_MATCH": {},
            "_FRIEND_LIST_LAST_MATCH": {},
            "_throttled_write": lambda *args, **kwargs: None,
            "_write": lambda message: None,
        })

        result = namespace["_apply_visual_friend_route_watchdog"](
            lambda owner: None, scheduler, "FarmBotCV.run_cycle"
        )

        self.assertFalse(result)
        self.assertEqual([scheduler], finalized)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_active)
        self.assertEqual(0, scheduler._qqfarm_visual_friend_count)

    def test_recent_native_home_false_positive_relabels_friend_log_as_self(self):
        note = load_function("_note_runtime_cycle_branch")
        scheduler = types.SimpleNamespace(
            _qqfarm_native_home_false_positive_ts=99.0
        )
        note.__globals__.update({
            "_ACTIVE_RUN_CYCLE_CONTEXT": scheduler,
            "_friend_watchdog_now": lambda: 100.0,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        branch = note("\u6b63\u5728\u68c0\u67e5\u597d\u53cb\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1")

        self.assertEqual("self", branch)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(getattr(scheduler, "_qqfarm_friend_cycle_seen", False))

    def test_native_home_check_accepts_verified_friend_surface(self):
        namespace = load_functions("_wrap_friend_home_func")
        calls = []
        frame = type("Frame", (), {"shape": (800, 428, 3)})()
        scheduler = object()
        namespace.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_chain_should_block_home": lambda context: False,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_get_frame_from_bot": lambda context: frame,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        def native_home(owner, game_frame):
            calls.append(game_frame)
            return True

        wrapped, _ = namespace["_wrap_friend_home_func"](
            native_home, "FarmBotCV.check_go_home_icon"
        )

        self.assertTrue(wrapped(scheduler, frame))
        self.assertEqual([frame], calls)

    def test_two_failed_home_friend_recoveries_clear_stale_friend_branch(self):
        namespace = load_functions(
            "_finalize_friend_chain_after_troublemaker",
            "_record_failed_friend_branch_recovery",
        )
        guard = namespace["_record_failed_friend_branch_recovery"]

        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_visual_friend_count=3,
            _qqfarm_friend_branch_last_ts=100.0,
        )

        self.assertFalse(guard(scheduler, 100.0))
        self.assertTrue(scheduler._qqfarm_friend_chain_pending)
        self.assertTrue(guard(scheduler, 104.0))
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_exhausted)
        self.assertFalse(scheduler._qqfarm_friend_chain_active)
        self.assertEqual("home", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertGreater(scheduler._qqfarm_false_friend_branch_block_until, 104.0)

    def test_friend_chain_finalize_restores_original_check_interval(self):
        namespace = load_functions(
            "_set_friend_chain_fast_interval",
            "_finalize_friend_chain_after_troublemaker",
        )
        scheduler = types.SimpleNamespace(
            check_interval=0.75,
            _qqfarm_friend_chain_original_interval=15.0,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=True,
        )

        finalized = namespace["_finalize_friend_chain_after_troublemaker"](scheduler)

        self.assertTrue(finalized)
        self.assertEqual(15.0, scheduler.check_interval)
        self.assertFalse(scheduler._qqfarm_friend_chain_active)
        self.assertFalse(hasattr(scheduler, "_qqfarm_friend_chain_original_interval"))

    def test_false_friend_branch_cooldown_blocks_native_hint_on_self_surface(self):
        guard = load_function("_false_friend_branch_cooldown_active")
        scheduler = types.SimpleNamespace(
            _qqfarm_false_friend_branch_block_until=112.0
        )

        self.assertTrue(guard(scheduler, False, 108.0))
        self.assertFalse(guard(scheduler, True, 108.0))
        self.assertFalse(guard(scheduler, False, 113.0))

    def test_deferred_troublemaker_success_finalizes_friend_chain_state(self):
        namespace = load_functions(
            "_finalize_friend_chain_after_troublemaker",
            "_run_deferred_friend_troublemaker",
        )
        runner = namespace["_run_deferred_friend_troublemaker"]
        snapshots = iter((0, 24))

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_active = True
            _qqfarm_friend_chain_allow_home = True
            _qqfarm_troublemaker_retry_scan_active = True
            _qqfarm_friend_cycle_seen = True
            _qqfarm_visual_friend_count = 3
            _qqfarm_friend_branch_last_ts = 123.0
            _last_friend_farm_go_home_present = True
            _qqfarm_friend_chain_deferred_troublemaker_args = ()
            _qqfarm_friend_chain_deferred_troublemaker_kwargs = {}

        scheduler = Scheduler()
        scheduler._qqfarm_friend_chain_deferred_troublemaker = lambda target: True
        scheduler._qqfarm_friend_chain_deferred_troublemaker_args = (scheduler,)
        namespace.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(*args, **kwargs)
            ),
            "_friend_trouble_counter_snapshot": lambda owner: next(snapshots),
            "_write": lambda message: None,
        })

        self.assertTrue(runner(scheduler, object()))
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_exhausted)
        self.assertFalse(scheduler._qqfarm_friend_chain_active)
        self.assertFalse(scheduler._qqfarm_friend_chain_allow_home)
        self.assertFalse(scheduler._qqfarm_troublemaker_retry_scan_active)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)
        self.assertEqual(0, scheduler._qqfarm_visual_friend_count)
        self.assertEqual(0.0, scheduler._qqfarm_friend_branch_last_ts)
        self.assertFalse(scheduler._last_friend_farm_go_home_present)

    def test_current_friend_action_must_disappear_before_next_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []
        repeated_actions = []

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent")
                or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": (
                lambda *args, **kwargs: repeated_actions.append("help-visible")
                or (True, "visual.friend_help_all")
            ),
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })

        class Scheduler:
            bottom_friend_list_help_all_limit = 1
            friend_chain_action_poll_limit = 16
            friend_chain_primary_navigation_poll_limit = 3
            friend_chain_idle_confirmations = 3

        scheduler = Scheduler()
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertEqual([], moves)
        self.assertEqual(3, len(repeated_actions))
        self.assertFalse(result["exhausted"])
        self.assertEqual("current-friend-not-idle", result["reason"])
        self.assertTrue(getattr(scheduler, "_qqfarm_friend_chain_pending", False))
        self.assertFalse(getattr(scheduler, "_qqfarm_friend_chain_exhausted", True))

    def test_friend_guard_list_mode_defers_row_selection_to_native_flow(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        rows = [
            {"center": (365, 289), "rect": (331, 271, 399, 307)},
            {"center": (365, 384), "rect": (331, 366, 399, 402)},
        ]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_list_guard_dog_score": lambda candidate, row_y: 0.99,
            "_friend_guard_post_client_click": (
                lambda *args, **kwargs: clicks.append(args) or True
            ),
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        result = handler(object(), Frame())

        self.assertEqual("native-guard-list", result)
        self.assertEqual([], clicks)

    def test_avatar_frame_guard_mode_clicks_first_verified_row(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        rows = [
            {"center": (365, 289), "rect": (331, 271, 399, 307)},
            {"center": (365, 384), "rect": (331, 366, 399, 402)},
        ]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_list_guard_dog_score": (
                lambda candidate, row_y: 0.95 if int(row_y) == 289 else 0.99
            ),
            "_friend_guard_post_client_click": (
                lambda *args, **kwargs: clicks.append(args) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        context = types.SimpleNamespace()
        result = handler(context, Frame())

        self.assertEqual("visited", result)
        self.assertEqual((365, 289), clicks[0][:2])
        self.assertTrue(context._qqfarm_guard_row_verified)
        self.assertEqual(100.0, context._qqfarm_guard_row_verified_ts)
        self.assertEqual(289, context._qqfarm_guard_row_y)
        self.assertAlmostEqual(0.95, context._qqfarm_guard_row_score)

    def test_avatar_frame_guard_mode_closes_when_no_verified_row_is_visible(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        rows = [{"center": (365, 289), "rect": (331, 271, 399, 307)}]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_list_guard_dog_score": lambda candidate, row_y: 0.31,
            "_friend_guard_post_client_click": (
                lambda *args, **kwargs: clicks.append(args) or True
            ),
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        result = handler(object(), Frame())

        self.assertEqual("closed", result)
        self.assertEqual(1, len(clicks))
        self.assertNotEqual((365, 289), clicks[0][:2])

    def test_guard_list_process_friend_opens_list_without_legacy_scan(self):
        wrapper_factory = load_function("_wrap_vip_business_func")
        self.assertIsNotNone(wrapper_factory)
        events = []
        scheduler = types.SimpleNamespace()

        def original(context, frame=None):
            events.append("legacy-scan")
            return "legacy"

        wrapper_factory.__globals__.update({
            "_stop_requested_in_args": lambda args, kwargs: False,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_guard_list_fast_open_from_home": (
                lambda context: events.append("fast-open") or True
            ),
            "_enter_vip_entitlement_context": lambda *args, **kwargs: [],
            "_restore_vip_entitlement_context": lambda values: 0,
            "_mark_friend_cycle_seen": lambda *args, **kwargs: None,
            "_apply_friend_empty_return_home_guard": lambda *args, **kwargs: None,
            "_friend_chain_finish_dispatch": lambda context: True,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        wrapped, changed = wrapper_factory(original, "module.process_friend_farm")

        self.assertTrue(changed)
        self.assertTrue(wrapped(scheduler, object()))
        self.assertEqual(["fast-open"], events)

    def test_recent_native_home_false_positive_skips_legacy_friend_processor(self):
        wrapper_factory = load_function("_wrap_vip_business_func")
        events = []
        frame = object()
        scheduler = types.SimpleNamespace(
            _qqfarm_native_home_false_positive_ts=99.0,
            _qqfarm_friend_cycle_seen=False,
            _qqfarm_cycle_branch_hint="self",
        )

        def original(context, game_frame=None):
            events.append("legacy-friend-processor")
            return True

        wrapper_factory.__globals__.update({
            "_ACTIVE_RUN_CYCLE_CONTEXT": scheduler,
            "_stop_requested_in_args": lambda args, kwargs: False,
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_friend_guard_list_fast_open_from_home": (
                lambda context: events.append("fast-open") or False
            ),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_friend_watchdog_now": lambda: 100.0,
            "_finalize_friend_chain_after_troublemaker": lambda context: True,
            "_force_vip_business_args": lambda args, kwargs: 0,
            "_enter_vip_entitlement_context": lambda *args, **kwargs: [],
            "_restore_vip_entitlement_context": lambda values: 0,
            "_mark_friend_cycle_seen": lambda *args, **kwargs: None,
            "_apply_friend_empty_return_home_guard": lambda *args, **kwargs: None,
            "_friend_chain_begin_dispatch": lambda context: False,
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })
        wrapped, changed = wrapper_factory(
            original, "module.process_friend_farm"
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual(["fast-open"], events)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)

    def test_friend_chain_fast_interval_reduces_list_to_action_latency(self):
        activate = load_function("_set_friend_chain_fast_interval")
        self.assertIsNotNone(activate)
        scheduler = types.SimpleNamespace(check_interval=15.0)

        self.assertTrue(activate(scheduler, True))

        self.assertLessEqual(scheduler.check_interval, 0.75)
        self.assertEqual(15.0, scheduler._qqfarm_friend_chain_original_interval)

    def test_friend_guard_list_continues_through_two_adjacent_friends_before_home(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frames = [object(), object(), object(), object()]
        moves = []
        fast_actions = []
        legacy_actions = []

        def move_adjacent(context, frame):
            moves.append(frame)
            context.after_navigation = len(moves)
            return (
                (True, "visual.adjacent-friend-card")
                if len(moves) <= 2
                else (False, "")
            )

        def fast_action(context, frame):
            marker = int(getattr(context, "after_navigation", 0) or 0)
            if marker > len(fast_actions):
                fast_actions.append(marker)
                return True, "visual.friend_help_all"
            return False, ""

        captures = iter(frames[1:])
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": move_adjacent,
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": (
                lambda *args, **kwargs: legacy_actions.append(args) or (False, "")
            ),
            "_get_frame_from_bot": lambda context: next(captures, frames[-1]),
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=12,
            friend_chain_action_poll_limit=4,
            friend_chain_primary_navigation_poll_limit=1,
            friend_chain_idle_confirmations=2,
        )
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frames[0], "visual.friend_steal_all"
        )

        self.assertEqual(2, result["moves"])
        self.assertEqual(2, result["actions"])
        self.assertEqual([1, 2], fast_actions)
        self.assertEqual([], legacy_actions)
        self.assertTrue(result["exhausted"])
        self.assertEqual("no-next-bottom-card", result["reason"])
        self.assertFalse(getattr(scheduler, "_qqfarm_friend_chain_pending", True))

    def test_friend_guard_list_refreshes_carousel_identity_once_per_friend(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        refresh_calls = []
        move_calls = []

        def move_adjacent(context, candidate):
            move_calls.append(candidate)
            return (
                (True, "visual.adjacent-friend-card")
                if len(move_calls) == 1
                else (False, "")
            )

        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": move_adjacent,
            "_invoke_friend_visual_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_friend_guard_list_refresh_prequalification": (
                lambda context, candidate: refresh_calls.append(candidate) or True
            ),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=12,
            friend_chain_action_poll_limit=4,
            friend_chain_primary_navigation_poll_limit=1,
            friend_chain_idle_confirmations=2,
        )
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertEqual(1, result["moves"])
        self.assertEqual(1, len(refresh_calls))

    def test_friend_guard_list_surface_clicks_first_matching_row_without_native_wait(self):
        handler = load_function("_handle_friend_list_surface")
        self.assertIsNotNone(handler)
        clicks = []
        rows = [
            {"center": (365, 289), "rect": (331, 271, 399, 307)},
            {"center": (365, 384), "rect": (331, 366, 399, 402)},
        ]
        handler.__globals__.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": (
                lambda candidate, row_y: 0.91 if int(row_y) == 289 else 0.99
            ),
            "_friend_guard_post_client_click": (
                lambda *args, **kwargs: clicks.append(args) or True
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_write": lambda message: None,
        })

        class Frame:
            shape = (800, 428, 3)

        scheduler = types.SimpleNamespace()
        result = handler(scheduler, Frame())

        self.assertEqual("visited", result)
        self.assertEqual((365, 289), clicks[0][:2])
        self.assertTrue(scheduler._qqfarm_guard_list_prequalified)
        self.assertEqual(100.0, scheduler._qqfarm_guard_list_prequalified_ts)
        self.assertEqual(289, scheduler._qqfarm_guard_list_row_y)
        self.assertAlmostEqual(0.91, scheduler._qqfarm_guard_list_row_score)
        self.assertTrue(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_exhausted)

    def test_friend_guard_list_carousel_match_recognizes_imported_friend_card(self):
        namespace = load_functions(
            "_friend_guard_read_template",
            "_friend_guard_list_carousel_card_match",
        )
        matcher = namespace.get("_friend_guard_list_carousel_card_match")
        self.assertTrue(callable(matcher))
        import cv2
        frame = cv2.imread(str(FIXTURES / "friend_guard_carousel_live_sanitized.png"))
        template = str(FIXTURES / "friend_guard_row_iris_sanitized.png")
        self.assertIsNotNone(frame)
        namespace["_FRIEND_GUARD_TEMPLATE_CACHE"] = {}
        namespace["_friend_selected_carousel_card_bounds"] = lambda candidate: {
            "left": 123,
            "right": 218,
            "top": 678,
            "bottom": 765,
            "width": 95,
            "height": 87,
        }

        match = matcher(frame, template_paths=(template,))

        self.assertTrue(match["matched"], match)
        self.assertGreaterEqual(match["score"], 0.75)

    def test_guard_list_carousel_refresh_clears_stale_row_approval_for_unmatched_friend(self):
        namespace = load_functions("_friend_guard_list_refresh_prequalification")
        refresh = namespace.get("_friend_guard_list_refresh_prequalification")
        self.assertTrue(callable(refresh))
        scheduler = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=50.0,
        )
        namespace.update({
            "_friend_guard_list_carousel_card_match": lambda frame: {
                "matched": False,
                "score": 0.31,
                "path": "",
            },
            "_friend_watchdog_now": lambda: 100.0,
            "_write": lambda message: None,
        })

        self.assertFalse(refresh(scheduler, object()))
        self.assertFalse(scheduler._qqfarm_guard_list_prequalified)
        self.assertEqual(0.0, scheduler._qqfarm_guard_list_prequalified_ts)

    def test_avatar_badge_guard_mode_finishes_current_friend_before_returning_to_list(self):
        namespace = load_functions("_run_friend_continuation_chain")
        moves = []
        frame = object()
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_guard_verified_entry_active": lambda context: True,
            "_invoke_friend_next_actionable_entry": (
                lambda *args, **kwargs: moves.append("native") or (True, "native")
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent") or (True, "adjacent")
            ),
            "_invoke_friend_visual_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda context: 0,
            "_set_friend_chain_fast_interval": lambda context, active: True,
            "_is_stop_requested_like": lambda context: False,
            "_write": lambda message: None,
        })

        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=12,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
        )
        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertEqual([], moves)
        self.assertTrue(result["exhausted"])
        self.assertEqual("verified-guard-row-complete", result["reason"])
        self.assertFalse(getattr(scheduler, "_qqfarm_guard_row_verified", True))

    def test_friend_guard_list_mode_blocks_compiled_home_until_continuation_finishes(self):
        namespace = load_functions("_friend_chain_should_block_troublemaker")
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        self.assertTrue(namespace["_friend_chain_should_block_troublemaker"](
            scheduler
        ))


    def test_runtime_start_wrapper_syncs_persisted_metrics_before_start(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        events = []
        namespace.update({
            "time": types.SimpleNamespace(
                time=lambda: 100.0,
                monotonic=lambda: 100.0,
            ),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_daily_metrics_sync_runtime": (
                lambda context, force=False: events.append(("sync", context, force))
            ),
        })
        window = object()

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda self: events.append(("start", self)) or True,
            "FarmBotWindow._start_bot",
        )
        result = wrapped(window)

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual(("sync", window, True), events[0])
        self.assertEqual(("start", window), events[1])



    def test_run_cycle_wrapper_periodically_syncs_persisted_metrics_after_cycle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        events = []
        namespace.update({
            "time": types.SimpleNamespace(
                time=lambda: 100.0,
                monotonic=lambda: 100.0,
            ),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_daily_metrics_sync_runtime": (
                lambda context, force=False: events.append(("sync", context, force))
            ),
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_force_self_cycle_next=False,
            _qqfarm_cycle_branch_hint="self",
        )

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda self: events.append(("cycle", self)) or True,
            "FarmBotCV.run_cycle",
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual(("cycle", scheduler), events[0])
        self.assertEqual(("sync", scheduler, False), events[-1])

    def test_friend_entry_callable_inventory_lists_menu_friend_and_home_methods(self):
        inventory = load_function("_friend_entry_callable_inventory")

        class Scheduler:
            def check_menu_more(self):
                return True

            def check_friend_icon(self):
                return True

            def process_self_farm(self):
                return True

            def unrelated(self):
                return True

        names = inventory(Scheduler())

        self.assertIn("check_menu_more", names)
        self.assertIn("check_friend_icon", names)
        self.assertIn("process_self_farm", names)
        self.assertNotIn("unrelated", names)

    def test_friend_home_recovery_skips_entry_when_help_quota_exhausted(self):
        namespace = load_functions(
            "_friend_help_quota_active",
            "_invoke_friend_branch_from_home",
        )
        calls = []
        frame = object()
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_help_quota_exhausted=True,
            check_friend_help_request_entry=lambda candidate: calls.append("help") or True,
            check_friend_icon=lambda candidate: calls.append("icon") or True,
        )
        namespace.update({
            "_guard_dog_ui_config_enabled": lambda: False,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_friend_entry_callable_inventory": lambda context: (),
            "_write": lambda message: None,
            "_throttled_write": lambda *args, **kwargs: None,
        })

        result = namespace["_invoke_friend_branch_from_home"](scheduler, frame)

        self.assertFalse(result)
        self.assertEqual([], calls)

    def test_friend_home_recovery_prefers_direct_help_entry(self):
        recover = load_function("_invoke_friend_branch_from_home")
        self.assertTrue(callable(recover))
        frame = object()
        calls = []

        class Scheduler:
            def check_friend_help_request_entry(self, game_frame):
                calls.append(("help-entry", game_frame))
                return True

            def check_friend_icon(self, game_frame):
                calls.append(("friend-icon", game_frame))
                return True

            def process_friend_farm(self, game_frame):
                calls.append(("processor", game_frame))
                raise RecursionError("recursive compiled friend dispatcher")

        scheduler = Scheduler()
        recover.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(recover(scheduler, frame))
        self.assertEqual([("help-entry", frame)], calls)

    def test_guard_list_home_recovery_skips_direct_help_entry(self):
        recover = load_function("_invoke_friend_branch_from_home")
        self.assertTrue(callable(recover))
        frame = object()
        calls = []

        class Scheduler:
            def check_friend_help_request_entry(self, game_frame):
                calls.append(("help-entry", game_frame))
                return True

            def check_friend_icon(self, game_frame):
                calls.append(("friend-icon", game_frame))
                return True

            def process_friend_farm(self, game_frame):
                calls.append(("processor", game_frame))
                return True

        scheduler = Scheduler()
        recover.__globals__.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(recover(scheduler, frame))
        self.assertEqual([("friend-icon", frame)], calls)
    def test_friend_home_recovery_uses_friend_icon_when_help_entry_is_absent(self):
        recover = load_function("_invoke_friend_branch_from_home")
        self.assertTrue(callable(recover))
        frame = object()
        calls = []

        class Scheduler:
            def check_friend_help_request_entry(self, game_frame):
                calls.append(("help-entry", game_frame))
                return False

            def check_friend_icon(self, game_frame):
                calls.append(("friend-icon", game_frame))
                return True

            def process_friend_farm(self, game_frame):
                calls.append(("processor", game_frame))
                raise RecursionError("recursive compiled friend dispatcher")

        scheduler = Scheduler()
        recover.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })

        self.assertTrue(recover(scheduler, frame))
        self.assertEqual(
            [("help-entry", frame), ("friend-icon", frame)],
            calls,
        )



    def test_native_bottom_help_entry_falls_back_to_immediate_adjacent_friend(self):
        wrapper_factory = load_function("_wrap_friend_next_entry_func")
        self.assertIsNotNone(wrapper_factory)
        frame = object()
        scheduler = types.SimpleNamespace()
        events = []

        def original(owner, game_frame):
            events.append(("native", game_frame))
            return False

        wrapper_factory.__globals__.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: events.append(("adjacent", candidate))
                or (True, "visual.adjacent-friend-card")
            ),
            "_write": lambda message: None,
        })

        wrapped, changed = wrapper_factory(
            original, "FarmBotCV.check_friend_farm_bottom_help_all_entry"
        )
        result = wrapped(scheduler, frame)

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual([("native", frame), ("adjacent", frame)], events)
        self.assertTrue(scheduler._qqfarm_friend_chain_pending)
        self.assertFalse(scheduler._qqfarm_friend_chain_exhausted)

    def test_native_bottom_entry_ignores_opaque_argument_and_captures_fresh_frame(self):
        wrapper_factory = load_function("_wrap_friend_next_entry_func")
        self.assertIsNotNone(wrapper_factory)
        opaque_match = object()
        fresh_frame = types.SimpleNamespace(shape=(800, 428, 3))
        scheduler = types.SimpleNamespace()
        captures = []
        navigations = []

        wrapper_factory.__globals__.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_get_frame_from_bot": (
                lambda owner: captures.append(owner) or fresh_frame
            ),
            "_friend_guard_friend_ui_state": (
                lambda candidate: candidate is fresh_frame
            ),
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: navigations.append(candidate)
                or (True, "visual.adjacent-friend-card")
            ),
            "_write": lambda message: None,
        })

        wrapped, _ = wrapper_factory(
            lambda owner, native_match: False,
            "FarmBotCV.check_friend_farm_bottom_help_all_entry",
        )

        self.assertTrue(wrapped(scheduler, opaque_match))
        self.assertEqual([scheduler], captures)
        self.assertEqual([fresh_frame], navigations)

    def test_native_bottom_entry_does_not_navigate_on_self_surface(self):
        wrapper_factory = load_function("_wrap_friend_next_entry_func")
        self.assertIsNotNone(wrapper_factory)
        frame = object()
        scheduler = types.SimpleNamespace()
        events = []
        wrapper_factory.__globals__.update({
            "_friend_guard_context": lambda args, kwargs: scheduler,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: events.append("adjacent")
                or (True, "visual.adjacent-friend-card")
            ),
            "_write": lambda message: None,
        })

        wrapped, _ = wrapper_factory(
            lambda owner, game_frame: False,
            "FarmBotCV.check_friend_farm_bottom_help_all_entry",
        )

        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual([], events)

    def test_native_go_home_is_blocked_while_friend_chain_is_pending(self):
        namespace = load_functions(
            "_friend_guard_context",
            "_friend_chain_should_block_troublemaker",
            "_friend_chain_should_block_home",
            "_wrap_friend_home_func",
        )
        wrapper = namespace.get("_wrap_friend_home_func")
        self.assertIsNotNone(wrapper)
        calls = []
        logs = []
        namespace.update({
            "_throttled_write": lambda *args, **kwargs: logs.append(args),
        })

        class Scheduler:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_active = False
            _qqfarm_friend_chain_exhausted = False

        scheduler = Scheduler()
        frame = object()
        wrapped, changed = wrapper(
            lambda target, game_frame: calls.append((target, game_frame)) or True,
            "bot.application.flows.check_go_home_icon",
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual([], calls)
        self.assertEqual(1, len(logs))

    def test_blocked_native_home_records_compiled_action_completion_hint(self):
        namespace = load_functions(
            "_friend_guard_context",
            "_friend_chain_should_block_troublemaker",
            "_friend_chain_should_block_home",
            "_wrap_friend_home_func",
        )
        wrapper = namespace.get("_wrap_friend_home_func")
        self.assertIsNotNone(wrapper)
        namespace["_throttled_write"] = lambda *args, **kwargs: None

        class Scheduler:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_active = False
            _qqfarm_friend_chain_exhausted = False

        scheduler = Scheduler()
        wrapped, _ = wrapper(
            lambda target: True,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.check_go_home_icon",
        )

        self.assertFalse(wrapped(scheduler))
        self.assertTrue(
            getattr(scheduler, "_qqfarm_friend_chain_native_home_blocked", False)
        )

    def test_native_go_home_runs_after_friend_chain_is_exhausted(self):
        namespace = load_functions(
            "_friend_guard_context",
            "_friend_chain_should_block_troublemaker",
            "_friend_chain_should_block_home",
            "_wrap_friend_home_func",
        )
        wrapper = namespace.get("_wrap_friend_home_func")
        self.assertIsNotNone(wrapper)
        namespace["_throttled_write"] = lambda *args, **kwargs: None
        calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_active = False
            _qqfarm_friend_chain_exhausted = True

        scheduler = Scheduler()
        frame = object()
        wrapped, _ = wrapper(
            lambda target, game_frame: calls.append((target, game_frame)) or "home-ok",
            "bot.application.flows.go_home",
        )

        self.assertEqual("home-ok", wrapped(scheduler, frame))
        self.assertEqual([(scheduler, frame)], calls)

    def test_troublemaker_retry_scan_blocks_home_without_explicit_authorization(self):
        namespace = load_functions(
            "_friend_chain_should_block_troublemaker",
            "_friend_chain_should_block_home",
        )
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_allow_home=False,
            _qqfarm_troublemaker_retry_scan_active=True,
        )

        self.assertTrue(namespace["_friend_chain_should_block_home"](scheduler))

    def test_explicit_home_authorization_overrides_pending_friend_chain(self):
        namespace = load_functions(
            "_friend_guard_context",
            "_friend_chain_should_block_troublemaker",
            "_friend_chain_should_block_home",
            "_wrap_friend_home_func",
        )
        wrapper = namespace.get("_wrap_friend_home_func")
        self.assertIsNotNone(wrapper)
        namespace["_throttled_write"] = lambda *args, **kwargs: None
        calls = []

        class Scheduler:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_active = True
            _qqfarm_friend_chain_exhausted = False
            _qqfarm_friend_chain_allow_home = True

        scheduler = Scheduler()
        wrapped, _ = wrapper(
            lambda target: calls.append(target) or "authorized-home",
            "bot.application.flows.return_home",
        )

        self.assertEqual("authorized-home", wrapped(scheduler))
        self.assertEqual([scheduler], calls)

    def test_troublemaker_home_authorization_overrides_retry_scan_gate(self):
        should_block = load_function("_friend_chain_should_block_home")
        self.assertIsNotNone(should_block)
        scheduler = types.SimpleNamespace(
            _qqfarm_troublemaker_retry_scan_active=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=True,
        )
        should_block.__globals__["_friend_chain_should_block_troublemaker"] = (
            lambda context: False
        )

        self.assertFalse(should_block(scheduler))

    def test_deferred_troublemaker_temporarily_authorizes_home_and_restores(self):
        runner = load_function("_run_deferred_friend_troublemaker")
        self.assertIsNotNone(runner)
        observed = []
        frame = object()

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_allow_home = False

            def _run_friend_daily_troublemaker(self, game_frame):
                observed.append(bool(getattr(self, "_qqfarm_friend_chain_allow_home", False)))
                return "trouble-home"

        scheduler = Scheduler()
        runner.__globals__.update({
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_write": lambda message: None,
        })

        self.assertEqual("trouble-home", runner(scheduler, frame))
        self.assertEqual([True], observed)
        self.assertFalse(scheduler._qqfarm_friend_chain_allow_home)

    def test_pending_empty_home_guard_log_is_throttled(self):
        namespace = load_functions(
            "_friend_guard_context",
            "_friend_chain_should_block_troublemaker",
            "_apply_friend_empty_return_home_guard",
        )
        direct_logs = []
        throttled_logs = []
        namespace.update({
            "_write": lambda message: direct_logs.append(message),
            "_throttled_write": (
                lambda key, message, seconds=30.0:
                throttled_logs.append((key, message, seconds))
            ),
        })
        context = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=False,
        )

        result = namespace["_apply_friend_empty_return_home_guard"](
            lambda *args, **kwargs: None,
            (context,),
            {},
            0.05,
            "bot.application.flows.process_friend_farm",
        )

        self.assertFalse(result)
        self.assertEqual([], direct_logs)
        self.assertEqual(1, len(throttled_logs))
        self.assertGreaterEqual(float(throttled_logs[0][2]), 10.0)


    def test_visual_help_probe_keeps_original_bottom_carousel_for_guard_gate(self):
        namespace = load_functions("_invoke_friend_visual_actions_before_home")
        original_frame = object()
        masked_frame = object()
        seen = []

        namespace.update({
            "_friend_selected_carousel_card_bounds": lambda frame: None,
            "_friend_guard_friend_ui_state": lambda frame: True,
            "_friend_action_frame_without_bottom_bar": lambda frame: masked_frame,
            "_invoke_friend_guard_steal_visual_click": (
                lambda context, frame: seen.append(("steal", frame)) or False
            ),
            "_invoke_friend_guard_help_visual_click": (
                lambda context, frame: seen.append(("help", frame)) or True
            ),
            "_write": lambda message: None,
        })

        acted, label = namespace["_invoke_friend_visual_actions_before_home"](
            object(), original_frame
        )

        self.assertTrue(acted)
        self.assertEqual("visual.friend_help_all", label)
        self.assertEqual(
            [("steal", masked_frame), ("help", original_frame)],
            seen,
        )

    def test_daily_metrics_sync_preserves_same_day_action_counters_across_files(self):
        import json
        import tempfile

        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)
        sync.__globals__.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_write": lambda message: None,
        })
        day = "2026-07-29"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(temp_dir) / "local.json"
            portable_path = Path(temp_dir) / "portable.json"
            local_path.write_text(json.dumps({
                "friend_help_daily_count": 82,
                "friend_help_daily_date": day,
                "friend_trouble_daily_count": 24,
                "friend_trouble_daily_date": day,
                "self_actions_daily_count": 23,
                "self_actions_daily_date": day,
                "instances": {
                    "1": {
                        "friend_help_daily_count": 82,
                        "friend_help_daily_date": day,
                        "friend_trouble_daily_count": 24,
                        "friend_trouble_daily_date": day,
                        "self_actions_daily_count": 23,
                        "self_actions_daily_date": day,
                    }
                },
            }), encoding="utf-8")
            portable_path.write_text(json.dumps({
                "friend_help_daily_count": 4,
                "friend_help_daily_date": day,
                "friend_trouble_daily_count": 0,
                "friend_trouble_daily_date": day,
                "self_actions_daily_count": 2,
                "self_actions_daily_date": day,
                "instances": {"1": {}},
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                friend_help_daily_count=4,
                friend_help_daily_date=day,
                friend_trouble_daily_count=0,
                friend_trouble_daily_date=day,
                self_actions_daily_count=2,
                self_actions_daily_date=day,
                _instance_metrics={"1": {"date": day}},
            )

            summary = sync(
                context,
                counter_paths=[local_path, portable_path],
                csv_paths=[],
                today=day,
                force=True,
            )

            self.assertEqual(82, summary.get("friend_help_daily_count"))
            self.assertEqual(24, summary.get("friend_trouble_daily_count"))
            self.assertEqual(23, summary.get("self_actions_daily_count"))
            self.assertEqual(82, context.friend_help_daily_count)
            self.assertEqual(24, context.friend_trouble_daily_count)
            self.assertEqual(23, context.self_actions_daily_count)
            for path in (local_path, portable_path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(82, payload["friend_help_daily_count"])
                self.assertEqual(24, payload["friend_trouble_daily_count"])
                self.assertEqual(23, payload["self_actions_daily_count"])
                self.assertEqual(
                    24, payload["instances"]["1"]["gui_metrics"]["troublemaker_count"]
                )

    def test_visual_watchdog_pending_chain_logs_empty_reason_without_runtime_error(self):
        namespace = load_functions("_apply_visual_friend_route_watchdog")
        frame = object()
        logs = []

        namespace.update({
            "_friend_watchdog_now": lambda: 100.0,
            "_get_frame_from_bot": lambda context: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_chain_should_block_troublemaker": lambda context: True,
            "_write": lambda message: logs.append(message),
            "_FRIEND_HOME_LAST_MATCH": {},
            "_FRIEND_LIST_LAST_MATCH": {},
        })

        scheduler = types.SimpleNamespace(
            _qqfarm_friend_cycle_seen=False,
            _qqfarm_visual_friend_count=1,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        self.assertFalse(namespace["_apply_visual_friend_route_watchdog"](
            lambda *args, **kwargs: None,
            scheduler,
            "FarmBotCV.run_cycle",
        ))
        self.assertTrue(any(
            "friend watchdog kept current friend" in message
            for message in logs
        ))
        self.assertFalse(any(
            "UnboundLocalError" in message
            for message in logs
        ))


    def test_full_drag_planting_outcome_starts_short_replant_cooldown(self):
        note = load_function("_note_runtime_planting_outcome")
        self.assertIsNotNone(note)
        note.__globals__["_LAST_SUCCESSFUL_FULL_PLANTING_TS"] = 0.0
        note.__globals__["time"] = types.SimpleNamespace(time=lambda: 100.0)

        note("拖拽播种已覆盖全地块")

        self.assertEqual(100.0, note.__globals__["_LAST_SUCCESSFUL_FULL_PLANTING_TS"])

    def test_home_planting_cooldown_skips_false_empty_land_rescan(self):
        wrapper = load_function("_wrap_home_planting_cooldown")
        self.assertIsNotNone(wrapper)
        calls = []
        wrapper.__globals__.update({
            "time": types.SimpleNamespace(time=lambda: 150.0),
            "_LAST_SUCCESSFUL_FULL_PLANTING_TS": 100.0,
            "_write": lambda message: None,
        })
        wrapped, changed = wrapper(
            lambda owner, frame=None: calls.append((owner, frame)) or True,
            "fixture.handle_home_planting",
        )
        scheduler = types.SimpleNamespace(
            planting_post_success_cooldown_seconds=120.0,
            _qqfarm_single_harvest_planting_pending=False,
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(scheduler, "frame"))
        self.assertEqual([], calls)

        scheduler._qqfarm_single_harvest_planting_pending = True
        self.assertTrue(wrapped(scheduler, "frame"))
        self.assertEqual([(scheduler, "frame")], calls)

    def test_planting_callable_inventory_finds_obfuscated_backpack_seed_helper(self):
        namespace = load_functions("_planting_callable_inventory")

        def obfuscated_helper():
            return "背包种子优先后仍有空地待处理"

        def unrelated_helper():
            return "friend navigation"

        module = types.SimpleNamespace(
            __name__="bot.synthetic_planting",
            _q_backpack=obfuscated_helper,
            unrelated=unrelated_helper,
        )

        inventory = namespace.get("_planting_callable_inventory")
        self.assertTrue(callable(inventory))
        entries = inventory(module)
        paths = [str(entry.get("path", "")) for entry in entries]

        self.assertTrue(any(path.endswith("._q_backpack") for path in paths))
        self.assertFalse(any(path.endswith(".unrelated") for path in paths))
        matched = next(entry for entry in entries if entry["path"].endswith("._q_backpack"))
        self.assertIn("背包种子优先", matched["details"])

    def test_planting_callable_inventory_never_disassembles_protected_callables(self):
        namespace = load_functions("_planting_callable_inventory")

        def protected_helper():
            return "backpack_seed_priority"

        module = types.SimpleNamespace(
            __name__="bot.synthetic_protected_planting",
            _q_protected=protected_helper,
        )
        import dis

        calls = []
        original_dis = dis.dis

        def forbidden_disassembly(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("protected callables must not be disassembled")

        dis.dis = forbidden_disassembly
        try:
            entries = namespace["_planting_callable_inventory"](module)
        finally:
            dis.dis = original_dis

        self.assertTrue(entries)
        self.assertEqual([], calls)
        self.assertFalse(any("disassembly" in entry["details"] for entry in entries))

    def test_backpack_priority_wrapper_clamps_long_panel_settle(self):
        namespace = load_functions("_wrap_backpack_seed_priority_planting_fast")
        wrapper = namespace.get("_wrap_backpack_seed_priority_planting_fast")
        self.assertTrue(callable(wrapper))

        calls = []
        logs = []
        expected = (True, [], False, None, True)

        def original(bot, lands, panel_settle):
            calls.append((bot, lands, panel_settle))
            return expected

        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = wrapper(original, "synthetic.backpack")
        owner = object()
        lands = [{"center": (100, 200)}]

        result = wrapped(owner, lands, 1.5)

        self.assertTrue(changed)
        self.assertIs(expected, result)
        self.assertEqual(1, len(calls))
        self.assertIs(owner, calls[0][0])
        self.assertIs(lands, calls[0][1])
        self.assertAlmostEqual(0.65, calls[0][2], places=6)
        self.assertTrue(any("1.500->0.650" in message for message in logs))

    def _synthetic_seed_panel_frame(self):
        import cv2
        import numpy as np

        frame = np.full((800, 428, 3), (145, 190, 105), dtype=np.uint8)
        cv2.rectangle(frame, (8, 480), (420, 595), (78, 75, 72), -1)
        for index, ratio in enumerate((0.159, 0.318, 0.477, 0.637, 0.796), start=1):
            center = (int(round(428 * ratio)), int(round(800 * 0.639)))
            cv2.ellipse(frame, center, (22, 12), 0, 0, 360, (205, 228, 241), -1)
            cv2.putText(
                frame, str(index), (center[0] - 5, center[1] + 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (55, 60, 70), 1, cv2.LINE_AA,
            )
        return frame

    def test_fast_seed_badges_detect_fixed_panel_slots_without_ocr(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_fast_seed_badge_candidates_from_frame",
        )
        frame = self._synthetic_seed_panel_frame()

        candidates = namespace["_fast_seed_badge_candidates_from_frame"](frame)

        self.assertEqual(5, len(candidates))
        self.assertEqual([68, 136, 204, 273, 341], [item["center"][0] for item in candidates])
        self.assertTrue(all(item["count"] >= 1 for item in candidates))

    def test_fast_seed_badge_wrapper_skips_native_ocr_for_visible_panel(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_fast_seed_badge_candidates_from_frame",
            "_wrap_seed_quantity_badges_fast",
        )
        calls = []
        logs = []

        def original(bot, frame, seed_roi=None):
            calls.append((bot, frame, seed_roi))
            return []

        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = namespace["_wrap_seed_quantity_badges_fast"](
            original, "synthetic.seed_badges"
        )
        bot = types.SimpleNamespace(_qqfarm_backpack_profile_active=True)

        result = wrapped(bot, self._synthetic_seed_panel_frame(), None)

        self.assertTrue(changed)
        self.assertEqual([], calls)
        self.assertEqual(5, len(result))
        self.assertGreater(bot._qqfarm_backpack_candidates_seen_ts, 0)
        self.assertTrue(any("fast seed badges" in message for message in logs))

    def test_empty_land_crop_filter_rejects_planted_false_positive_and_keeps_bare_tiles(self):
        helper = load_function("_empty_land_candidate_has_crop_cover")
        self.assertIsNotNone(helper)
        import cv2

        planted = cv2.imread(str(FIXTURES / "planted_land_false_positive_crop.png"))
        purple = cv2.imread(str(FIXTURES / "empty_land_true_purple_crop.png"))
        yellow = cv2.imread(str(FIXTURES / "empty_land_true_yellow_crop.png"))

        self.assertTrue(helper(planted, (36, 36)))
        self.assertFalse(helper(purple, (36, 36)))
        self.assertFalse(helper(yellow, (36, 36)))

    def test_empty_land_state_filters_crop_covered_candidates_before_backpack(self):
        namespace = load_functions(
            "_empty_land_candidate_has_crop_cover",
            "_wrap_detect_empty_lands_state",
        )
        import cv2
        import numpy as np

        frame = np.hstack([
            cv2.imread(str(FIXTURES / "planted_land_false_positive_crop.png")),
            cv2.imread(str(FIXTURES / "empty_land_true_purple_crop.png")),
            cv2.imread(str(FIXTURES / "empty_land_true_yellow_crop.png")),
        ])
        lands = [
            {"center": (36, 36), "confidence": 0.91},
            {"center": (108, 36), "confidence": 0.92},
            {"center": (180, 36), "confidence": 0.93},
        ]
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda bot, candidate: list(lands), "synthetic.detect_empty"
        )
        bot = types.SimpleNamespace()

        result = wrapped(bot, frame)

        self.assertTrue(changed)
        self.assertEqual([(108, 36), (180, 36)], [item["center"] for item in result])
        self.assertEqual(2, bot._qqfarm_recent_empty_land_count)
        self.assertTrue(any("crop-covered false positives=1" in line for line in logs))

    def test_empty_land_state_records_candidate_centers_for_live_diagnostics(self):
        namespace = load_functions("_wrap_detect_empty_lands_state")
        logs = []
        lands = [
            {"center": (101, 301), "score": 0.91},
            {"center": [203, 407], "score": 0.92},
            {"score": 0.93},
        ]
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda bot, frame: lands, "synthetic.detect_empty"
        )
        wrapped.__globals__["_write"] = lambda message: logs.append(message)
        bot = types.SimpleNamespace()

        result = wrapped(bot, object())

        self.assertTrue(changed)
        self.assertIs(lands, result)
        self.assertEqual([(101, 301), (203, 407)], bot._qqfarm_recent_empty_land_centers)
        self.assertTrue(any("v220 empty land candidates" in line for line in logs))

    def test_multi_empty_land_batch_skips_redundant_label_ocr(self):
        namespace = load_functions(
            "_wrap_detect_empty_lands_state",
            "_wrap_backpack_empty_land_label_fast",
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        lands = [{"center": (100 + index * 10, 300)} for index in range(6)]
        detect_wrapped, _ = namespace["_wrap_detect_empty_lands_state"](
            lambda bot, frame: lands, "synthetic.detect_empty"
        )
        label_calls = []
        label_wrapped, _ = namespace["_wrap_backpack_empty_land_label_fast"](
            lambda *args, **kwargs: label_calls.append((args, kwargs)) or (False, "slow", 0.0, None),
            "synthetic.label_ocr",
        )
        bot = types.SimpleNamespace(_qqfarm_backpack_profile_active=False)

        self.assertIs(lands, detect_wrapped(bot, object()))
        result = label_wrapped(bot, object(), (123, 456), context="planting")

        self.assertEqual((True, "hook-batch-preverified-empty-land", 1.0, 123), result)
        self.assertEqual([], label_calls)
        self.assertTrue(any("batch preverified empty land" in message for message in logs))

    def test_recent_backpack_inventory_defers_shop_purchase(self):
        namespace = load_functions("_wrap_buy_seed_for_crop_backpack_guard")
        calls = []
        logs = []
        namespace["_write"] = lambda message: logs.append(message)

        def original(bot, crop_name, count):
            calls.append((crop_name, count))
            return True

        wrapped, changed = namespace["_wrap_buy_seed_for_crop_backpack_guard"](
            original, "synthetic.buy_seed"
        )
        import time
        bot = types.SimpleNamespace(_qqfarm_backpack_candidates_seen_ts=time.time())

        result = wrapped(bot, "???", 15)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], calls)
        self.assertEqual(1, bot.planting_buy_retry_no_buy_quota)
        self.assertTrue(any("deferred seed shop" in message for message in logs))

    def test_quad_confirm_template_uses_contextual_lower_threshold(self):
        namespace = load_functions("_wrap_planting_template_center_fast")
        calls = []

        def original(bot, frame, template_id, threshold=0.75):
            calls.append((template_id, threshold))
            return (10, 20)

        wrapped, changed = namespace["_wrap_planting_template_center_fast"](
            original, "synthetic.template_center"
        )
        self.assertTrue(changed)

        wrapped(object(), object(), "act_seeds_btn_ok", 0.78)
        wrapped(object(), object(), "unrelated", 0.78)

        self.assertAlmostEqual(0.62, calls[0][1], places=6)
        self.assertAlmostEqual(0.78, calls[1][1], places=6)

    def test_player_level_uses_config_cache_before_slow_ocr(self):
        namespace = load_functions("_configured_player_level", "_wrap_player_level_fast")
        namespace["_active_planting_sections"] = lambda: ["instance.1.planting", "planting"]
        namespace["_cfg_get"] = lambda sections, key, default: "120"
        namespace["_write"] = lambda message: None
        calls = []

        def original(bot, game_frame=None, fallback_to_config=True):
            calls.append((game_frame, fallback_to_config))
            return 121

        wrapped, changed = namespace["_wrap_player_level_fast"](
            original, "synthetic.player_level"
        )
        bot = types.SimpleNamespace()

        self.assertTrue(changed)
        self.assertEqual(120, wrapped(bot, object(), True))
        self.assertEqual(120, wrapped(bot, object(), True))
        self.assertEqual([], calls)

        bot._qqfarm_player_level_next_probe_ts = 0.0
        self.assertEqual(121, wrapped(bot, object(), True))
        self.assertEqual(1, len(calls))

    def test_fertilizer_template_wrapper_uses_lower_contextual_threshold(self):
        namespace = load_functions("_wrap_fertilizer_template_fast")
        observed = []

        def original(bot, frame, fertilizer_type, seed_roi=None):
            observed.append(bot.fertilizer_one_frame_threshold)
            return None, 0.61

        wrapped, changed = namespace["_wrap_fertilizer_template_fast"](
            original, "synthetic.fertilizer"
        )
        bot = types.SimpleNamespace(fertilizer_one_frame_threshold=0.72)

        self.assertTrue(changed)
        self.assertEqual((None, 0.61), wrapped(bot, object(), "one", None))
        self.assertEqual([0.62], observed)
        self.assertEqual(0.72, bot.fertilizer_one_frame_threshold)

    def test_backpack_profile_helper_records_only_active_backpack_calls(self):
        namespace = load_functions("_wrap_backpack_profile_helper")
        wrapper = namespace.get("_wrap_backpack_profile_helper")
        self.assertTrue(callable(wrapper))

        def original(bot, value):
            return value + 1

        wrapped, changed = wrapper(original, "synthetic.seed_ocr")
        active = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_backpack_profile={},
        )
        inactive = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=False,
            _qqfarm_backpack_profile={},
        )

        self.assertTrue(changed)
        self.assertEqual(4, wrapped(active, 3))
        self.assertEqual(5, wrapped(inactive, 4))
        self.assertIn("synthetic.seed_ocr", active._qqfarm_backpack_profile)
        stats = active._qqfarm_backpack_profile["synthetic.seed_ocr"]
        self.assertEqual(1, stats["count"])
        self.assertGreaterEqual(stats["total"], 0.0)
        self.assertEqual({}, inactive._qqfarm_backpack_profile)

    def test_backpack_preverified_empty_land_skips_slow_label_ocr(self):
        namespace = load_functions("_wrap_backpack_empty_land_label_fast")
        wrapper = namespace.get("_wrap_backpack_empty_land_label_fast")
        self.assertTrue(callable(wrapper))

        calls = []
        logs = []
        fallback = (False, "native-miss", 0.0, None)

        def original(bot, frame, land_center, context=""):
            calls.append((bot, frame, land_center, context))
            return fallback

        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = wrapper(original, "synthetic.empty_land_label")
        active = types.SimpleNamespace(_qqfarm_backpack_profile_active=True)
        inactive = types.SimpleNamespace(_qqfarm_backpack_profile_active=False)
        frame = object()

        result = wrapped(active, frame, (123, 456), context="? 1 ????")

        self.assertTrue(changed)
        self.assertEqual((True, "hook-backpack-preverified-empty-land", 1.0, 123), result)
        self.assertEqual([], calls)
        self.assertTrue(any("v197 backpack preverified empty land" in message for message in logs))

        self.assertIs(fallback, wrapped(inactive, frame, (123, 456), context="????"))
        self.assertIs(fallback, wrapped(active, frame, None, context="????"))
        self.assertEqual(2, len(calls))

    def test_backpack_no_seed_hint_wrapper_saves_active_seed_panel_frame(self):
        namespace = load_functions("_wrap_backpack_no_seed_hint_fast")
        wrapper = namespace.get("_wrap_backpack_no_seed_hint_fast")
        self.assertTrue(callable(wrapper))
        saved = []
        frame = object()
        native_result = (False, "", 0.0)
        namespace["_save_backpack_seed_panel_debug_frame"] = (
            lambda candidate: saved.append(candidate) or "backpack-seed-panel-live.png"
        )
        namespace["_write"] = lambda message: None
        wrapped, changed = wrapper(
            lambda bot, candidate, seed_roi=None: native_result,
            "synthetic.no_seed_hint",
        )
        active = types.SimpleNamespace(_qqfarm_backpack_profile_active=True)

        self.assertTrue(changed)
        self.assertIs(native_result, wrapped(active, frame, (10, 20, 30, 40)))
        self.assertEqual([frame], saved)
    def test_backpack_no_seed_hint_ocr_preserves_native_result_for_active_branch(self):
        namespace = load_functions("_wrap_backpack_no_seed_hint_fast")
        wrapper = namespace.get("_wrap_backpack_no_seed_hint_fast")
        self.assertTrue(callable(wrapper))

        calls = []
        logs = []
        native_result = (True, "??????", 0.99)

        def original(bot, frame, seed_roi=None):
            calls.append((bot, frame, seed_roi))
            return native_result

        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = wrapper(original, "synthetic.no_seed_hint")
        active = types.SimpleNamespace(_qqfarm_backpack_profile_active=True)
        frame = object()

        self.assertTrue(changed)
        self.assertIs(native_result, wrapped(active, frame, (10, 20, 30, 40)))
        self.assertEqual(1, len(calls))
        self.assertTrue(any("v202 restored native no-seed OCR" in line for line in logs))

    def test_fast_planting_switch_disables_expensive_enhanced_land_ocr(self):
        switch_value = load_function("_fast_planting_switch_value")
        self.assertIsNotNone(switch_value)

        self.assertFalse(switch_value("enhance_empty_land_detection", True))
        self.assertTrue(switch_value("enable_daily_radish_exp", True))

    def test_visible_seed_inventory_skips_slow_no_seed_ocr(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_fast_seed_badge_candidates_from_frame",
            "_wrap_backpack_no_seed_hint_fast",
        )
        calls = []
        logs = []

        def original(bot, frame, seed_roi=None):
            calls.append((bot, frame, seed_roi))
            return True, "no-seed", 0.99

        namespace["_save_backpack_seed_panel_debug_frame"] = lambda frame: ""
        namespace["_write"] = lambda message: logs.append(message)
        wrapped, changed = namespace["_wrap_backpack_no_seed_hint_fast"](
            original, "synthetic.no_seed_hint"
        )
        bot = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_recent_empty_land_count=16,
        )

        result = wrapped(bot, self._synthetic_seed_panel_frame(), None)

        self.assertTrue(changed)
        self.assertEqual((False, "hook-visible-seed-inventory", 1.0), result)
        self.assertEqual([], calls)
        self.assertTrue(any("visible seed inventory" in line for line in logs))

    def test_fast_seed_badges_use_land_capacity_instead_of_magic_999(self):
        namespace = load_functions(
            "_seed_panel_strip_visible",
            "_fast_seed_badge_candidates_from_frame",
            "_wrap_seed_quantity_badges_fast",
        )
        namespace["_write"] = lambda message: None
        wrapped, changed = namespace["_wrap_seed_quantity_badges_fast"](
            lambda *args, **kwargs: [], "synthetic.seed_badges"
        )
        bot = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_recent_empty_land_count=16,
        )

        result = wrapped(bot, self._synthetic_seed_panel_frame(), None)

        self.assertTrue(changed)
        self.assertEqual([16] * 5, [item["count"] for item in result])
        self.assertTrue(all(item["count"] != 999 for item in result))

    def test_quad_seed_blacklist_uses_contextual_lower_threshold(self):
        namespace = load_functions("_wrap_backpack_seed_blacklist_fast")
        self.assertIn("_wrap_backpack_seed_blacklist_fast", namespace)
        observed = []

        def original(bot, frame, seed_center, seed_roi=None):
            observed.append(bot.act_seeds_frame_threshold)
            return bot.act_seeds_frame_threshold <= 0.62

        wrapped, changed = namespace["_wrap_backpack_seed_blacklist_fast"](
            original, "synthetic.quad_blacklist"
        )
        bot = types.SimpleNamespace(act_seeds_frame_threshold=0.72)

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, object(), (68, 512), None))
        self.assertEqual([0.62], observed)
        self.assertEqual(0.72, bot.act_seeds_frame_threshold)

    def test_compiled_steal_retries_same_friend_once_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        phase = {"second": False}

        def fast_action(owner, candidate):
            events.append("probe-second" if phase["second"] else "probe-first")
            if phase["second"]:
                events.append("help")
                return True, "visual.friend_help_all"
            return False, ""

        def adjacent(owner, candidate):
            events.append("navigate")
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
            _qqfarm_friend_entry_extended_action_grace=True,
        )

        first = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "method.check_steal_all_icon"
        )

        self.assertEqual(0, first["moves"])
        self.assertNotIn("navigate", events)
        self.assertTrue(scheduler._qqfarm_post_steal_help_retry_pending)

        phase["second"] = True
        second = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "method.check_steal_all_icon"
        )

        self.assertGreaterEqual(second["actions"], 1)
        self.assertIn("help", events)
        if "navigate" in events:
            self.assertLess(events.index("help"), events.index("navigate"))
        self.assertFalse(getattr(scheduler, "_qqfarm_post_steal_help_retry_pending", False))

    def test_reopened_friend_list_resets_stale_cursor_and_clicks_first_row(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (364, 289)},
            {"center": (364, 383)},
            {"center": (364, 478)},
            {"center": (364, 572)},
            {"center": (364, 667)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_list_blocked_row_visual_hint": lambda candidate, row_y: False,
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_guard_post_client_click": (
                lambda x, y, width=428, height=800: clicks.append((x, y)) or True
            ),
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_write": lambda message: None,
        })
        context = types.SimpleNamespace(
            _qqfarm_friend_list_visit_cursor=81,
            _qqfarm_friend_entry_pending=False,
        )

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("visited", result)
        self.assertEqual([(364, 289)], clicks)
        self.assertEqual(0, context._qqfarm_friend_list_pending_cursor)
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)

    def test_blocked_first_friend_row_is_skipped_immediately_for_second_row(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        logs = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (364, 289)},
            {"center": (364, 383)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_list_blocked_row_visual_hint": (
                lambda candidate, row_y: int(row_y) == 289
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_guard_post_client_click": (
                lambda x, y, width=428, height=800: clicks.append((x, y)) or True
            ),
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_write": lambda message: logs.append(message),
        })
        context = types.SimpleNamespace()

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("visited", result)
        self.assertEqual([(364, 383)], clicks)
        self.assertEqual(1, context._qqfarm_friend_list_pending_cursor)
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertTrue(any("blocked first row" in line for line in logs))

    def test_blocked_second_friend_row_never_skips_normal_first_row(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (364, 289)},
            {"center": (364, 383)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_list_blocked_row_visual_hint": (
                lambda candidate, row_y: int(row_y) == 383
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_guard_post_client_click": (
                lambda x, y, width=428, height=800: clicks.append((x, y)) or True
            ),
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_write": lambda message: None,
        })
        context = types.SimpleNamespace()

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("visited", result)
        self.assertEqual([(364, 289)], clicks)
        self.assertEqual(0, context._qqfarm_friend_list_pending_cursor)
        self.assertEqual(0, context._qqfarm_friend_list_visit_cursor)

    def test_failed_first_friend_row_advances_to_second_without_closing_list(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        logs = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (364, 289)},
            {"center": (364, 383)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_list_blocked_row_visual_hint": lambda candidate, row_y: True,
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_guard_post_client_click": (
                lambda x, y, width=428, height=800: clicks.append((x, y)) or True
            ),
            "_friend_guard_clear_prequalification": lambda owner: True,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_write": lambda message: logs.append(message),
        })
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_clicked_ts=90.0,
            _qqfarm_friend_entry_last_retry_ts=98.0,
            _qqfarm_friend_list_pending_cursor=0,
            _qqfarm_friend_list_visit_cursor=0,
        )

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("blocked-row-next", result)
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertEqual([], clicks)
        self.assertTrue(any("blocked row" in line for line in logs))

    def test_blocked_pending_second_row_closes_list_instead_of_advancing_to_third(self):
        namespace = load_functions("_handle_friend_list_surface")
        clicks = []
        logs = []
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        rows = [
            {"center": (364, 289)},
            {"center": (364, 383)},
            {"center": (364, 478)},
        ]
        namespace.update({
            "_friend_list_visit_button_rows": lambda candidate: rows,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_row_match_score": lambda candidate, row_y: 0.95,
            "_friend_list_blocked_row_visual_hint": (
                lambda candidate, row_y: int(row_y) == 383
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_guard_post_client_click": (
                lambda x, y, width=428, height=800: clicks.append((x, y)) or True
            ),
            "_friend_guard_clear_prequalification": lambda owner: True,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_write": lambda message: logs.append(message),
        })
        context = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_retry_count=3,
            _qqfarm_friend_entry_clicked_ts=90.0,
            _qqfarm_friend_entry_last_retry_ts=98.0,
            _qqfarm_friend_list_pending_cursor=1,
            _qqfarm_friend_list_visit_cursor=1,
        )

        result = namespace["_handle_friend_list_surface"](context, frame)

        self.assertEqual("pending-row-reopen", result)
        self.assertEqual([(405, 94)], clicks)
        self.assertEqual(1, context._qqfarm_friend_list_visit_cursor)
        self.assertFalse(context._qqfarm_friend_entry_pending)
        self.assertFalse(any("to cursor=2" in line for line in logs))

    def test_blocked_friend_row_template_matches_provided_status_text(self):
        namespace = load_functions("_friend_list_blocked_row_visual_hint")
        import cv2
        import numpy as np

        template_path = ROOT / "portable" / "friend_blocked_visit_text.png"
        template = cv2.imread(str(template_path))
        self.assertIsNotNone(template)
        frame = np.full((800, 428, 3), (190, 220, 235), dtype=np.uint8)
        row_y = 383
        top = row_y - (template.shape[0] // 2)
        left = 115
        frame[
            top:top + template.shape[0],
            left:left + template.shape[1],
        ] = template
        namespace["_FRIEND_BLOCKED_VISIT_TEMPLATE_PATH"] = str(template_path)
        namespace["_write"] = lambda message: None

        self.assertTrue(
            namespace["_friend_list_blocked_row_visual_hint"](frame, row_y)
        )
        self.assertFalse(
            namespace["_friend_list_blocked_row_visual_hint"](frame, 289)
        )

    def test_blocked_visit_status_matches_anywhere_in_transition_frame(self):
        namespace = load_functions("_friend_blocked_visit_visual_hint")
        self.assertIn("_friend_blocked_visit_visual_hint", namespace)
        import cv2
        import numpy as np

        template_path = ROOT / "portable" / "friend_blocked_visit_text.png"
        template = cv2.imread(str(template_path))
        self.assertIsNotNone(template)
        frame = np.full((800, 428, 3), (190, 220, 235), dtype=np.uint8)
        top, left = 310, 112
        frame[
            top:top + template.shape[0],
            left:left + template.shape[1],
        ] = template
        namespace["_FRIEND_BLOCKED_VISIT_TEMPLATE_PATH"] = str(template_path)
        namespace["_write"] = lambda message: None

        self.assertTrue(namespace["_friend_blocked_visit_visual_hint"](frame))
        self.assertFalse(
            namespace["_friend_blocked_visit_visual_hint"](
                np.full((800, 428, 3), (190, 220, 235), dtype=np.uint8)
            )
        )

    def test_blocked_visit_toast_matches_after_adjacent_friend_navigation(self):
        namespace = load_functions("_friend_blocked_visit_visual_hint")
        import cv2
        import numpy as np

        template_path = ROOT / "portable" / "friend_blocked_visit_toast.png"
        self.assertTrue(template_path.is_file())
        template = cv2.imread(str(template_path))
        self.assertIsNotNone(template)
        frame = np.full((800, 428, 3), (110, 160, 140), dtype=np.uint8)
        top, left = 350, 111
        frame[
            top:top + template.shape[0],
            left:left + template.shape[1],
        ] = template
        namespace["_FRIEND_BLOCKED_VISIT_TEMPLATE_PATH"] = str(
            ROOT / "portable" / "friend_blocked_visit_text.png"
        )
        namespace["_FRIEND_BLOCKED_VISIT_TOAST_TEMPLATE_PATH"] = str(template_path)
        namespace["_write"] = lambda message: None

        self.assertTrue(namespace["_friend_blocked_visit_visual_hint"](frame))

    def test_adjacent_blocked_friend_return_home_is_terminal_not_pending(self):
        namespace = load_functions("_run_friend_continuation_chain")
        current_frame = object()
        returned_home_frame = object()
        state = {"moved": False}
        logs = []

        def adjacent(owner, candidate):
            state["moved"] = True
            return True, "visual.adjacent-friend-card"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": (
                lambda owner: returned_home_frame if state["moved"] else current_frame
            ),
            "_friend_guard_friend_ui_state": lambda candidate: candidate is current_frame,
            "_friend_blocked_visit_visual_hint": (
                lambda candidate: candidate is returned_home_frame
            ),
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_friend_guard_list_refresh_prequalification": lambda owner, frame: True,
            "_write": lambda message: logs.append(message),
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=2,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, current_frame, ""
        )

        self.assertEqual(1, result["moves"])
        self.assertTrue(result["exhausted"])
        self.assertEqual("blocked-next-friend-returned-home", result["reason"])
        self.assertFalse(scheduler._qqfarm_friend_chain_pending)
        self.assertTrue(any("blocked next friend" in line for line in logs))

    def test_moderate_home_match_without_carousel_is_not_friend_farm(self):
        namespace = load_functions("_friend_guard_friend_ui_state")
        matches = iter([
            {"matched": True, "gray": 0.82, "edge": 0.28, "center": (393, 606)},
            {"matched": False, "gray": 0.2, "edge": 0.1, "center": None},
        ])
        namespace.update({
            "_friend_guard_match_template": lambda *args, **kwargs: next(matches),
            "_friend_selected_carousel_card_bounds": lambda frame: None,
            "_friend_list_visit_button_rows": lambda frame: [],
        })

        self.assertFalse(namespace["_friend_guard_friend_ui_state"](object()))

    def test_daily_metrics_sync_recovers_counters_from_same_day_gui_metrics(self):
        import json
        import tempfile

        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)
        sync.__globals__.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_write": lambda message: None,
        })
        day = "2026-07-29"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(temp_dir) / "local.json"
            portable_path = Path(temp_dir) / "portable.json"
            payload = {
                "friend_help_daily_count": 0,
                "friend_help_daily_date": day,
                "friend_trouble_daily_count": 0,
                "friend_trouble_daily_date": day,
                "self_actions_daily_count": 0,
                "self_actions_daily_date": day,
                "daily_radish_exp_count": 4,
                "daily_radish_exp_date": day,
                "gui_metrics": {
                    "date": day,
                    "friend_farming_count": 131,
                    "troublemaker_count": 37,
                    "self_farming_count": 39,
                    "planting_count": 4,
                    "radish_detect_count": 3,
                },
                "instances": {"1": {}},
            }
            local_path.write_text(json.dumps(payload), encoding="utf-8")
            portable_path.write_text(json.dumps(payload), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                friend_help_daily_count=0,
                friend_help_daily_date=day,
                friend_trouble_daily_count=0,
                friend_trouble_daily_date=day,
                self_actions_daily_count=0,
                self_actions_daily_date=day,
                daily_radish_exp_count=0,
                daily_radish_exp_date=day,
                _instance_metrics={"1": dict(payload["gui_metrics"])},
            )

            summary = sync(
                context,
                counter_paths=[str(local_path), str(portable_path)],
                csv_paths=[],
                today=day,
                force=True,
            )

            self.assertEqual(131, summary["friend_help_daily_count"])
            self.assertEqual(37, summary["friend_trouble_daily_count"])
            self.assertEqual(39, summary["self_actions_daily_count"])
            self.assertEqual(4, summary["daily_radish_exp_count"])
            for path in (local_path, portable_path):
                merged = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(131, merged["friend_help_daily_count"])
                self.assertEqual(37, merged["friend_trouble_daily_count"])
                self.assertEqual(39, merged["self_actions_daily_count"])
                self.assertEqual(4, merged["daily_radish_exp_count"])

    def test_daily_metrics_sync_does_not_count_generic_planting_as_daily_radish(self):
        import json
        import tempfile

        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)
        sync.__globals__.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_write": lambda message: None,
        })
        day = "2026-07-29"
        with tempfile.TemporaryDirectory() as temp_dir:
            counter_path = Path(temp_dir) / "daily_counters.hook.json"
            counter_path.write_text(json.dumps({
                "daily_radish_exp_count": 40,
                "daily_radish_exp_date": day,
                "gui_metrics": {
                    "date": day,
                    "planting_count": 62,
                    "radish_detect_count": 62,
                },
                "instances": {"1": {}},
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                daily_radish_exp_count=40,
                daily_radish_exp_date=day,
                _instance_metrics={
                    "1": {
                        "date": day,
                        "planting_count": 62,
                        "radish_detect_count": 62,
                    },
                },
            )

            summary = sync(
                context,
                counter_paths=[str(counter_path)],
                csv_paths=[],
                today=day,
                force=True,
            )

            self.assertEqual(40, summary["daily_radish_exp_count"])
            merged = json.loads(counter_path.read_text(encoding="utf-8"))
            self.assertEqual(40, merged["daily_radish_exp_count"])
            self.assertEqual(40, merged["instances"]["1"]["daily_radish_exp_count"])
            self.assertEqual(40, merged["gui_metrics"]["radish_detect_count"])
            self.assertEqual(62, merged["gui_metrics"]["planting_count"])

    def test_daily_metrics_sync_merges_same_day_daily_flow_success_dates(self):
        import json
        import tempfile

        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)
        sync.__globals__.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_write": lambda message: None,
        })
        day = "2026-07-29"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(temp_dir) / "local.json"
            portable_path = Path(temp_dir) / "portable.json"
            local_path.write_text(json.dumps({
                "task_last_date": "",
                "share_last_date": "",
                "instances": {"1": {}},
            }), encoding="utf-8")
            portable_path.write_text(json.dumps({
                "task_last_date": day,
                "share_last_date": day,
                "instances": {"1": {
                    "task_last_date": day,
                    "share_last_date": day,
                }},
            }), encoding="utf-8")
            context = types.SimpleNamespace(
                instance_id="1",
                task_last_date="",
                share_last_date="",
                _instance_metrics={"1": {"date": day}},
            )

            sync(
                context,
                counter_paths=[str(local_path), str(portable_path)],
                csv_paths=[],
                today=day,
                force=True,
            )

            self.assertEqual(day, context.task_last_date)
            self.assertEqual(day, context.share_last_date)
            for path in (local_path, portable_path):
                merged = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(day, merged["task_last_date"])
                self.assertEqual(day, merged["share_last_date"])
                self.assertEqual(day, merged["instances"]["1"]["task_last_date"])
                self.assertEqual(day, merged["instances"]["1"]["share_last_date"])

    def test_daily_metrics_default_sync_writes_hook_owned_durable_mirrors(self):
        import json
        import os
        import tempfile
        from unittest import mock

        sync = load_function("_daily_metrics_sync_runtime")
        self.assertIsNotNone(sync)
        sync.__globals__.update({
            "_DAILY_METRICS_LAST_SYNC_TS": 0.0,
            "_write": lambda message: None,
        })
        day = "2026-07-29"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            local = root / "Local"
            fake_hook = root / "portable" / "hook.py"
            fake_hook.parent.mkdir(parents=True, exist_ok=True)
            local.mkdir(parents=True, exist_ok=True)
            sync.__globals__["__file__"] = str(fake_hook)
            context = types.SimpleNamespace(
                instance_id="1",
                friend_help_daily_count=12,
                friend_help_daily_date=day,
                friend_trouble_daily_count=3,
                friend_trouble_daily_date=day,
                self_actions_daily_count=7,
                self_actions_daily_date=day,
                daily_radish_exp_count=2,
                daily_radish_exp_date=day,
                _instance_metrics={"1": {"date": day}},
            )
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": str(local)}):
                sync(
                    context,
                    counter_paths=None,
                    csv_paths=[],
                    today=day,
                    force=True,
                )

            mirrors = (
                local / "qq-farm-bot-rev" / "daily_counters.hook.json",
                fake_hook.parent / "UserData" / "legacy-qq-farm-bot-rev" /
                "daily_counters.hook.json",
            )
            for mirror in mirrors:
                self.assertTrue(mirror.is_file(), str(mirror))
                data = json.loads(mirror.read_text(encoding="utf-8"))
                self.assertEqual(12, data["friend_help_daily_count"])
                self.assertEqual(3, data["friend_trouble_daily_count"])
                self.assertEqual(7, data["self_actions_daily_count"])
                self.assertEqual(2, data["daily_radish_exp_count"])

    def test_first_friend_waits_for_delayed_help_after_compiled_steal_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        action_calls = []

        def fast_action(owner, candidate):
            action_calls.append(candidate)
            events.append("probe")
            if len(action_calls) == 5:
                events.append("help")
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("navigate") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "method.check_steal_all_icon"
        )

        self.assertGreaterEqual(len(action_calls), 5)
        self.assertIn("help", events)
        if "navigate" in events:
            self.assertLess(events.index("help"), events.index("navigate"))
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_first_friend_rechecks_delayed_help_even_when_compiled_label_is_help(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        action_calls = []

        def fast_action(owner, candidate):
            action_calls.append(candidate)
            events.append("probe")
            if len(action_calls) == 5:
                events.append("help")
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("navigate") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertGreaterEqual(len(action_calls), 5)
        self.assertIn("help", events)
        if "navigate" in events:
            self.assertLess(events.index("help"), events.index("navigate"))
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_first_friend_waits_for_delayed_help_button_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        calls = []
        moves = []

        def fast_action(owner, candidate):
            calls.append(candidate)
            if len(calls) == 5:
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: False,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertGreaterEqual(len(calls), 5)
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_guard_list_first_friend_waits_through_full_render_grace_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        action_calls = []

        def fast_action(owner, candidate):
            action_calls.append(candidate)
            events.append("probe")
            if len(action_calls) == 11:
                events.append("help")
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("navigate") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertGreaterEqual(len(action_calls), 11)
        self.assertIn("help", events)
        if "navigate" in events:
            self.assertLess(events.index("help"), events.index("navigate"))
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_guard_list_first_friend_waits_for_very_late_help_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        events = []
        action_calls = []

        def fast_action(owner, candidate):
            action_calls.append(candidate)
            events.append("probe")
            if len(action_calls) == 20:
                events.append("help")
                return True, "visual.friend_help_all"
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: events.append("navigate") or (False, "")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
            _qqfarm_friend_entry_extended_action_grace=True,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertGreaterEqual(len(action_calls), 20)
        self.assertIn("help", events)
        if "navigate" in events:
            self.assertLess(events.index("help"), events.index("navigate"))
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_next_friend_waits_for_very_late_help_after_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        state = {"navigated": False, "post_navigation_probes": 0}
        events = []

        def fast_action(owner, candidate):
            if not state["navigated"]:
                return False, ""
            state["post_navigation_probes"] += 1
            events.append("probe-next")
            if state["post_navigation_probes"] == 20:
                events.append("help-next")
                return True, "visual.friend_help_all"
            return False, ""

        def adjacent(owner, candidate):
            state["navigated"] = True
            events.append("navigate")
            return True, "visual.adjacent-friend-card"

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": adjacent,
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_friend_guard_list_prequalified_entry_active": lambda owner: True,
            "_friend_guard_list_refresh_prequalification": lambda owner, candidate: True,
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_initial_idle_poll_min=8,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, "visual.friend_help_all"
        )

        self.assertGreaterEqual(state["post_navigation_probes"], 20)
        self.assertIn("help-next", events)
        self.assertGreaterEqual(result["actions"], 1)
        self.assertEqual("visual.friend_help_all", result["last_label"])

    def test_initial_guard_help_rejection_retries_same_first_friend_before_navigation(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []
        action_calls = []

        def fast_action(owner, candidate):
            action_calls.append(candidate)
            owner._qqfarm_guard_dog_help_skipped = True
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda *args, **kwargs: moves.append("adjacent") or (True, "next")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=3,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )

        result = namespace["_run_friend_continuation_chain"](
            scheduler, frame, ""
        )

        self.assertGreaterEqual(len(action_calls), 1)
        self.assertEqual([], moves)
        self.assertFalse(result["exhausted"])
        self.assertEqual("initial-guard-approval-pending", result["reason"])
        self.assertTrue(scheduler._qqfarm_friend_chain_pending)

    def test_initial_guard_help_rejection_advances_after_bounded_pending_retries(self):
        namespace = load_functions("_run_friend_continuation_chain")
        frame = object()
        moves = []

        def fast_action(owner, candidate):
            owner._qqfarm_guard_dog_help_skipped = True
            return False, ""

        namespace.update({
            "_invoke_friend_next_actionable_entry": lambda *args, **kwargs: (False, ""),
            "_invoke_friend_adjacent_card_navigation": (
                lambda owner, candidate: moves.append(candidate)
                or (True, "visual.adjacent-friend-card")
            ),
            "_invoke_friend_visual_actions_before_home": fast_action,
            "_invoke_friend_actions_before_home": lambda *args, **kwargs: (False, ""),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_sleep": lambda seconds: None,
            "_friend_navigation_signature": lambda candidate: None,
            "_friend_navigation_change_score": lambda signature, candidate: None,
            "_restore_runtime_business_switches": lambda owner: 0,
            "_set_friend_chain_fast_interval": lambda owner, active: True,
            "_is_stop_requested_like": lambda owner: False,
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "friend_guard_list",
            "_write": lambda message: None,
        })
        scheduler = types.SimpleNamespace(
            bottom_friend_list_help_all_limit=1,
            friend_chain_action_poll_limit=16,
            friend_chain_primary_navigation_poll_limit=2,
            friend_chain_idle_confirmations=2,
            friend_chain_guard_pending_retry_limit=3,
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=100.0,
        )

        first = namespace["_run_friend_continuation_chain"](scheduler, frame, "")
        second = namespace["_run_friend_continuation_chain"](scheduler, frame, "")
        third = namespace["_run_friend_continuation_chain"](scheduler, frame, "")

        self.assertEqual([], moves[:0])
        self.assertEqual("initial-guard-approval-pending", first["reason"])
        self.assertEqual("initial-guard-approval-pending", second["reason"])
        self.assertGreaterEqual(len(moves), 1)
        self.assertNotEqual("initial-guard-approval-pending", third["reason"])
    def test_runtime_go_home_threshold_floor_updates_loaded_threshold_holders(self):
        apply_floor = load_function("_apply_runtime_go_home_threshold_floor")
        threshold_holder = types.SimpleNamespace(go_home_frame=0.70)
        scheduler = types.SimpleNamespace(
            go_home_frame_threshold=0.70,
            config={"threshold": {"go_home_frame": 0.70}},
            thresholds=threshold_holder,
        )

        changed = apply_floor(scheduler, 0.79)

        self.assertGreaterEqual(changed, 3)
        self.assertEqual(0.79, scheduler.go_home_frame_threshold)
        self.assertEqual(0.79, scheduler.config["threshold"]["go_home_frame"])
        self.assertEqual(0.79, threshold_holder.go_home_frame)

    def test_run_cycle_forces_one_self_pass_after_false_friend_branch(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        events = []

        class Scheduler:
            _qqfarm_force_self_cycle_next = True
            _qqfarm_cycle_branch_hint = "friend"
            _qqfarm_friend_cycle_seen = True

            def process_self_farm(self, game_frame):
                events.append(("self", game_frame))
                return "self-done"

        scheduler = Scheduler()
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_invoke_friend_guard_action": (
                lambda action, target, args, kwargs: action(args[-1])
            ),
            "_set_friend_chain_fast_interval": (
                lambda owner, active: events.append(("fast", active)) or True
            ),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
        })

        def original_run_cycle(owner):
            events.append(("original", owner))
            return "original"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            original_run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertEqual("self-done", result)
        self.assertEqual([("fast", False), ("self", frame)], events)
        self.assertFalse(scheduler._qqfarm_force_self_cycle_next)
        self.assertEqual("self", scheduler._qqfarm_cycle_branch_hint)
        self.assertFalse(scheduler._qqfarm_friend_cycle_seen)

    def test_run_cycle_waits_for_pending_friend_list_transition_before_native_flow(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        native_calls = []
        watchdog_calls = []
        logs = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 101.0),
            "_write": lambda message: logs.append(message),
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_apply_visual_friend_route_watchdog": (
                lambda fn, owner, label, force_recovery=False:
                watchdog_calls.append((owner, label, force_recovery)) or False
            ),
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        def native_run_cycle(owner):
            native_calls.append(owner)
            return "native"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native_run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], watchdog_calls)
        self.assertTrue(scheduler._qqfarm_friend_entry_pending)
        self.assertTrue(any("friend-list transition" in message for message in logs))

    def test_run_cycle_starts_first_friend_early_when_action_button_is_visible(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        watchdog_calls = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 101.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_friend_guard_help_button_match": (
                lambda candidate: {"matched": True, "center": (213, 597)}
            ),
            "_friend_guard_steal_button_match": (
                lambda candidate: {"matched": False}
            ),
            "_apply_visual_friend_route_watchdog": (
                lambda fn, owner, label, force_recovery=False:
                watchdog_calls.append((owner, label, force_recovery)) or False
            ),
            "_daily_metrics_sync_runtime": lambda owner, force=False: {},
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        wrapped, _ = namespace["_wrap_runtime_diag_method"](
            lambda owner: "native", "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertFalse(result)
        self.assertFalse(scheduler._qqfarm_friend_entry_pending)
        self.assertEqual([(scheduler, "FarmBotCV.run_cycle", True)], watchdog_calls)

    def test_run_cycle_keeps_pending_friend_entry_when_surface_is_not_ready_after_settle(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        native_calls = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 103.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        def native_run_cycle(owner):
            native_calls.append(owner)
            return "native"

        wrapped, _ = namespace["_wrap_runtime_diag_method"](
            native_run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertTrue(scheduler._qqfarm_friend_entry_pending)

    def test_run_cycle_releases_timed_out_friend_entry_for_native_recovery(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        native_calls = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 109.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: False,
            "_apply_visual_friend_route_watchdog": lambda *args, **kwargs: False,
            "_daily_metrics_sync_runtime": lambda owner, force=False: {},
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        def native_run_cycle(owner):
            native_calls.append(owner)
            return "native"

        wrapped, _ = namespace["_wrap_runtime_diag_method"](
            native_run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertEqual("native", result)
        self.assertEqual([scheduler], native_calls)
        self.assertFalse(scheduler._qqfarm_friend_entry_pending)

    def test_run_cycle_confirms_pending_friend_entry_after_settle_before_watchdog(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        watchdog_calls = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 103.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_apply_visual_friend_route_watchdog": (
                lambda fn, owner, label, force_recovery=False:
                watchdog_calls.append((owner, label, force_recovery)) or False
            ),
            "_daily_metrics_sync_runtime": lambda owner, force=False: {},
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=100.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda owner: "native", "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertFalse(scheduler._qqfarm_friend_entry_pending)
        self.assertEqual([(scheduler, "FarmBotCV.run_cycle", True)], watchdog_calls)

    def test_run_cycle_preflight_owns_visible_friend_farm_before_native_unknown_flow(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        frame = object()
        native_calls = []
        watchdog_calls = []
        sync_calls = []
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": lambda owner: False,
            "_friend_guard_friend_ui_state": lambda candidate: True,
            "_apply_visual_friend_route_watchdog": (
                lambda fn, owner, label, force_recovery=False:
                watchdog_calls.append((owner, label, force_recovery)) or False
            ),
            "_daily_metrics_sync_runtime": (
                lambda owner, force=False: sync_calls.append((owner, force)) or {}
            ),
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        def native_run_cycle(owner):
            native_calls.append(owner)
            return "native"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            native_run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([(scheduler, "FarmBotCV.run_cycle", True)], watchdog_calls)
        self.assertEqual([(scheduler, False)], sync_calls)
        self.assertIsNone(namespace["_ACTIVE_RUN_CYCLE_CONTEXT"])

    def test_run_cycle_preserves_first_friend_guard_approval_until_action(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        seen = []
        clear_calls = []
        frame = object()

        def clear_approval(owner):
            clear_calls.append(owner)
            owner._qqfarm_guard_list_prequalified = False
            owner._qqfarm_guard_list_prequalified_ts = 0.0
            return True

        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": clear_approval,
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=99.0,
            _qqfarm_friend_chain_pending=True,
            _qqfarm_friend_chain_exhausted=False,
        )

        def run_cycle(owner):
            seen.append(owner._qqfarm_guard_list_prequalified)
            return "ran"

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            run_cycle, "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertEqual("ran", result)
        self.assertEqual([True], seen)
        self.assertEqual([], clear_calls)


    def test_run_cycle_preserves_guard_approval_while_friend_entry_is_pending(self):
        namespace = load_functions("_wrap_runtime_diag_method")
        clear_calls = []
        frame = object()

        def clear_approval(owner):
            clear_calls.append(owner)
            owner._qqfarm_guard_list_prequalified = False
            owner._qqfarm_guard_list_prequalified_ts = 0.0
            return True

        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_write": lambda message: None,
            "_runtime_diag_repr": lambda value: repr(value),
            "_runtime_diag_state": lambda value: "{}",
            "_restore_runtime_business_switches": lambda owner: 0,
            "_run_share_prompt_recovery": lambda owner: False,
            "_get_frame_from_bot": lambda owner: frame,
            "_friend_list_visit_button_rows": lambda candidate: [],
            "_handle_friend_list_surface": lambda owner, candidate: None,
            "_friend_guard_clear_prequalification": clear_approval,
            "_friend_guard_list_prequalified_entry_active": lambda owner: bool(
                owner._qqfarm_guard_list_prequalified
            ),
            "_friend_guard_friend_ui_state": lambda candidate: None,
            "_ACTIVE_RUN_CYCLE_CONTEXT": None,
        })
        scheduler = types.SimpleNamespace(
            _qqfarm_guard_list_prequalified=True,
            _qqfarm_guard_list_prequalified_ts=99.0,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_exhausted=False,
            _qqfarm_friend_entry_pending=True,
            _qqfarm_friend_entry_clicked_ts=99.0,
            friend_list_entry_settle_seconds=2.8,
            friend_list_entry_timeout_seconds=8.0,
        )

        wrapped, changed = namespace["_wrap_runtime_diag_method"](
            lambda owner: "native", "FarmBotCV.run_cycle"
        )
        result = wrapped(scheduler)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], clear_calls)
        self.assertTrue(scheduler._qqfarm_guard_list_prequalified)



    def test_troublemaker_live_frame_geometry_finds_24_seed_land_centers(self):
        namespace = load_functions("_collect_friend_seed_land_centers_from_frame")
        import cv2

        frame = cv2.imread(str(FIXTURES / "friend_troublemaker_live.png"))
        self.assertIsNotNone(frame)
        centers = namespace["_collect_friend_seed_land_centers_from_frame"](frame)

        self.assertEqual(24, len(centers))
        self.assertEqual(len(centers), len(set(centers)))
        self.assertTrue(all(70 <= x <= 350 for x, _ in centers))
        self.assertTrue(all(395 <= y <= 570 for _, y in centers))

    def test_troublemaker_dense_crop_field_returns_crop_centers_not_right_edge_artifacts(self):
        namespace = load_functions("_collect_friend_seed_land_centers_from_frame")
        import cv2

        frame = cv2.imread(
            str(FIXTURES / "friend_troublemaker_dense_live_sanitized.png")
        )
        self.assertIsNotNone(frame)
        centers = namespace["_collect_friend_seed_land_centers_from_frame"](frame)

        self.assertGreaterEqual(len(centers), 12)
        self.assertLessEqual(min(x for x, _ in centers), 150)
        self.assertTrue(all(390 <= y <= 560 for _, y in centers))

    def test_troublemaker_empty_soil_is_not_treated_as_planted_land(self):
        namespace = load_functions("_collect_friend_seed_land_centers_from_frame")
        import cv2

        frame = cv2.imread(
            str(FIXTURES / "friend_troublemaker_empty_live_sanitized.png")
        )
        self.assertIsNotNone(frame)
        centers = namespace["_collect_friend_seed_land_centers_from_frame"](frame)

        self.assertEqual([], centers)

    def test_troublemaker_shifted_field_uses_largest_land_lattice(self):
        namespace = load_functions("_collect_friend_seed_land_centers_from_frame")
        import cv2

        frame = cv2.imread(str(FIXTURES / "friend_troublemaker_shifted_live.png"))
        self.assertIsNotNone(frame)
        centers = namespace["_collect_friend_seed_land_centers_from_frame"](frame)

        self.assertEqual(8, len(centers))
        self.assertTrue(all(130 <= x <= 340 for x, _ in centers))
        self.assertTrue(all(690 <= y <= 790 for _, y in centers))

    def test_troublemaker_popup_action_detector_finds_visible_weed_or_worm_button(self):
        detector = load_function("_detect_friend_trouble_popup_action")
        self.assertIsNotNone(detector)
        import cv2

        popup = cv2.imread(
            str(FIXTURES / "friend_trouble_popup_action_live_sanitized.png")
        )
        plain = cv2.imread(
            str(FIXTURES / "friend_troublemaker_dense_live_sanitized.png")
        )

        match = detector(popup)
        self.assertIsInstance(match, dict)
        self.assertIn("center", match)
        center_x, center_y = match["center"]
        self.assertTrue(150 <= center_x <= 270)
        self.assertTrue(510 <= center_y <= 555)
        self.assertIsNone(detector(plain))

    def test_troublemaker_button_picker_uses_popup_action_fallback_when_native_misses(self):
        namespace = load_functions(
            "_detect_friend_trouble_popup_action",
            "_wrap_troublemaker_button_picker",
        )
        import cv2

        frame = cv2.imread(
            str(FIXTURES / "friend_trouble_popup_action_live_sanitized.png")
        )
        logs = []
        namespace["_write"] = lambda message: logs.append(message)
        wrapped = namespace["_wrap_troublemaker_button_picker"](
            lambda owner, popup_frame, roi: None
        )
        result = wrapped(object(), frame, (100, 400, 320, 560))

        self.assertIsInstance(result, dict)
        self.assertIn("center", result)
        self.assertTrue(any("v200 trouble popup action fallback" in line for line in logs))

    def test_troublemaker_seed_land_wrapper_uses_geometry_when_native_returns_empty(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
        )
        import cv2

        frame = cv2.imread(str(FIXTURES / "friend_troublemaker_live.png"))
        calls = []

        def native(owner, game_frame):
            calls.append((owner, game_frame))
            return []

        owner_globals = {"_FRIEND_DAILY_TROUBLE_SEED_MATCH_THRESHOLD": 0.76}
        namespace.update({"_write": lambda message: None})
        wrapped = namespace["_wrap_troublemaker_seed_land_collector"](
            native, owner_globals
        )
        owner = object()
        centers = wrapped(owner, frame)

        self.assertEqual(24, len(centers))
        self.assertEqual(1, len(calls))
        self.assertEqual(0.76, owner_globals["_FRIEND_DAILY_TROUBLE_SEED_MATCH_THRESHOLD"])

    def test_troublemaker_seed_land_wrapper_rejects_native_candidates_on_empty_soil(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
        )
        import cv2

        frame = cv2.imread(
            str(FIXTURES / "friend_troublemaker_empty_live_sanitized.png")
        )
        namespace.update({"_write": lambda message: None})
        wrapped = namespace["_wrap_troublemaker_seed_land_collector"](
            lambda owner, game_frame: [(243, 426)],
            {"_FRIEND_DAILY_TROUBLE_SEED_MATCH_THRESHOLD": 0.76},
        )

        self.assertEqual([], wrapped(object(), frame))

    def test_troublemaker_seed_land_wrapper_prefers_dense_crop_geometry_over_sparse_native(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
        )
        import cv2

        frame = cv2.imread(
            str(FIXTURES / "friend_troublemaker_dense_live_sanitized.png")
        )
        namespace.update({"_write": lambda message: None})
        wrapped = namespace["_wrap_troublemaker_seed_land_collector"](
            lambda owner, game_frame: [(364, 446)],
            {"_FRIEND_DAILY_TROUBLE_SEED_MATCH_THRESHOLD": 0.76},
        )
        centers = wrapped(object(), frame)

        self.assertGreaterEqual(len(centers), 12)
        self.assertLessEqual(min(x for x, _ in centers), 150)

    def test_troublemaker_seed_land_wrapper_preserves_native_candidates(self):
        namespace = load_functions(
            "_collect_friend_seed_land_centers_from_frame",
            "_wrap_troublemaker_seed_land_collector",
        )
        native_centers = [(101, 420), (130, 435)]
        namespace.update({"_write": lambda message: None})
        wrapped = namespace["_wrap_troublemaker_seed_land_collector"](
            lambda owner, frame: list(native_centers),
            {"_FRIEND_DAILY_TROUBLE_SEED_MATCH_THRESHOLD": 0.76},
        )

        self.assertEqual(native_centers, wrapped(object(), object()))


if __name__ == "__main__":
    unittest.main()
