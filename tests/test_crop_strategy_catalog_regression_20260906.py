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
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {}
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class CropStrategyCatalogRegressionTests(unittest.TestCase):
    def test_v233_unlock_catalog_maps_level_134_to_wan_xiang_yu(self):
        namespace = load_functions("_qqfarm_v233_authoritative_crop_for_level")

        self.assertEqual(
            "晚香玉",
            namespace["_qqfarm_v233_authoritative_crop_for_level"](134),
        )
        self.assertEqual(
            "晚香玉",
            namespace["_qqfarm_v233_authoritative_crop_for_level"](135),
        )
        self.assertEqual(
            "人参",
            namespace["_qqfarm_v233_authoritative_crop_for_level"](136),
        )

    def test_auto_level_strategy_replaces_stale_pineapple_alias_before_planting(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_strategy_level",
            "_qqfarm_auto_level_strategy_enabled",
            "_qqfarm_correct_crop_name_for_level",
            "_wrap_planting_flow_fast",
        )
        calls = []

        def native(owner, game_frame=None, crop_name="", allow_buy=True):
            calls.append((owner, game_frame, crop_name, allow_buy))
            return True

        bot = types.SimpleNamespace(
            backpack_seed_priority=False,
            _qqfarm_player_level_trusted_value=134,
            _last_player_level_detect_source="live-ocr",
            _qqfarm_player_level_dynamic_pending=False,
            strategy="auto_detect_level",
        )
        namespace.update({
            "_write": lambda _message: None,
            "_qqfarm_backpack_priority_enabled": lambda _bot: False,
        })

        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native,
            "fixture._run_planting_flow",
        )
        result = wrapped(
            bot,
            game_frame=object(),
            crop_name="菠萝蜜",
            allow_buy=True,
        )

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual(1, len(calls))
        self.assertEqual("晚香玉", calls[0][2])

    def test_level_134_never_accepts_short_pineapple_card_as_target(self):
        namespace = load_functions("_qqfarm_crop_card_matches_target")

        self.assertFalse(
            namespace["_qqfarm_crop_card_matches_target"]("菠萝", "晚香玉")
        )
        self.assertFalse(
            namespace["_qqfarm_crop_card_matches_target"]("菠萝蜜", "晚香玉")
        )
        self.assertTrue(
            namespace["_qqfarm_crop_card_matches_target"]("晚香玉", "晚香玉")
        )
        self.assertTrue(
            namespace["_qqfarm_crop_card_matches_target"]("晚香玉种子", "晚香玉")
        )

    def test_explicit_crop_strategy_is_not_overridden_by_level_catalog(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_strategy_level",
            "_qqfarm_auto_level_strategy_enabled",
            "_qqfarm_correct_crop_name_for_level",
            "_wrap_planting_flow_fast",
        )
        calls = []

        def native(owner, game_frame=None, crop_name="", allow_buy=True):
            calls.append((owner, game_frame, crop_name, allow_buy))
            return True

        bot = types.SimpleNamespace(
            backpack_seed_priority=False,
            _qqfarm_player_level_trusted_value=134,
            _qqfarm_player_level_dynamic_pending=False,
            strategy="fixed_crop",
        )
        namespace.update({
            "_write": lambda _message: None,
            "_qqfarm_backpack_priority_enabled": lambda _bot: False,
        })

        wrapped, changed = namespace["_wrap_planting_flow_fast"](
            native,
            "fixture._run_planting_flow",
        )
        result = wrapped(
            bot,
            game_frame=object(),
            crop_name="菠萝蜜",
            allow_buy=True,
        )

        self.assertTrue(changed)
        self.assertTrue(result)
        self.assertEqual("菠萝蜜", calls[0][2])

    def test_daily_radish_strategy_is_not_overridden_by_level_catalog(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_strategy_level",
            "_qqfarm_auto_level_strategy_enabled",
            "_qqfarm_correct_crop_name_for_level",
            "_wrap_planting_flow_fast",
        )
        calls = []

        def native(owner, game_frame=None, crop_name="", allow_buy=True):
            calls.append(crop_name)
            return True

        bot = types.SimpleNamespace(
            backpack_seed_priority=False,
            _qqfarm_player_level_trusted_value=134,
            _qqfarm_player_level_dynamic_pending=False,
            strategy="auto_detect_level",
        )
        namespace.update({
            "_write": lambda _message: None,
            "_qqfarm_backpack_priority_enabled": lambda _bot: False,
        })

        wrapped, _changed = namespace["_wrap_planting_flow_fast"](
            native,
            "fixture._run_planting_flow",
        )
        self.assertTrue(wrapped(
            bot,
            game_frame=object(),
            crop_name="白萝卜",
            allow_buy=True,
        ))
        self.assertEqual(["白萝卜"], calls)

    def test_native_owner_receives_corrected_crop_call(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_strategy_level",
            "_qqfarm_auto_level_strategy_enabled",
            "_qqfarm_correct_crop_name_for_level",
            "_wrap_native_v225_crop_catalog_planting_flow",
        )
        calls = []

        def native(owner, game_frame=None, crop_name="", allow_buy=True):
            calls.append(crop_name)
            return True

        bot = types.SimpleNamespace(
            _qqfarm_player_level_trusted_value=134,
            _qqfarm_player_level_dynamic_pending=False,
            strategy="auto_detect_level",
        )
        namespace["_write"] = lambda _message: None
        wrapped, changed = namespace[
            "_wrap_native_v225_crop_catalog_planting_flow"
        ](native, "fixture.native._run_planting_flow")

        self.assertTrue(changed)
        self.assertTrue(wrapped(
            bot,
            object(),
            "菠萝蜜",
            True,
        ))
        self.assertEqual(["晚香玉"], calls)

    def test_native_level_catalog_result_is_corrected_before_strategy_log(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_card_matches_target",
            "_qqfarm_correct_native_crop_catalog_result",
        )
        namespace["_write"] = lambda _message: None

        corrected = namespace["_qqfarm_correct_native_crop_catalog_result"](
            "菠萝蜜",
            134,
            strategy="auto_detect_level",
            name="fixture.get_best_crop_for_level",
        )

        self.assertEqual("晚香玉", corrected)

    def test_native_level_catalog_result_preserves_explicit_crop_strategy(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_card_matches_target",
            "_qqfarm_correct_native_crop_catalog_result",
        )

        corrected = namespace["_qqfarm_correct_native_crop_catalog_result"](
            "菠萝蜜",
            134,
            strategy="fixed_crop",
            name="fixture.get_best_crop_for_level",
        )

        self.assertEqual("菠萝蜜", corrected)

    def test_native_level_catalog_wrapper_preserves_result_shape(self):
        namespace = load_functions(
            "_qqfarm_v233_authoritative_crop_for_level",
            "_qqfarm_crop_card_matches_target",
            "_qqfarm_correct_native_crop_catalog_result",
            "_wrap_native_crop_catalog_result_func",
        )
        namespace["_write"] = lambda _message: None

        def native(level, strategy="auto_detect_level"):
            return ("菠萝蜜", 0.0803, level)

        wrapped, changed = namespace["_wrap_native_crop_catalog_result_func"](
            native,
            "fixture.get_best_crop_for_level",
        )

        self.assertTrue(changed)
        self.assertEqual(
            ("晚香玉", 0.0803, 134),
            wrapped(134, strategy="auto_detect_level"),
        )


if __name__ == "__main__":
    unittest.main()
