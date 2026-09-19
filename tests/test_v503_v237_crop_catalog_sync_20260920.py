import ast
import json
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
CATALOG = ROOT / "portable" / "data" / "v237_plant_catalog.json"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {
        "__file__": str(HOOK),
        "_QQFARM_V237_CROP_CATALOG_CACHE": None,
        "_QQFARM_V237_CROP_CATALOG_CACHE_PATH": "",
    }
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V237CropCatalogSyncTests(unittest.TestCase):
    def test_high_level_boundaries_use_v237_names(self):
        namespace = load_functions(
            "_qqfarm_v237_crop_catalog_path",
            "_qqfarm_load_v237_crop_catalog",
            "_qqfarm_v237_crop_for_level",
            "_qqfarm_v233_authoritative_crop_for_level",
        )
        select = namespace["_qqfarm_v233_authoritative_crop_for_level"]

        self.assertEqual("晚香玉", select(134))
        self.assertEqual("似血杜鹃", select(140))
        self.assertEqual("艳蝶兰", select(150))
        self.assertEqual("蓝铃花", select(162))
        self.assertEqual("宋梅", select(164))

    def test_catalog_excludes_stale_level_134_pineapple_and_has_new_assets(self):
        self.assertTrue(CATALOG.is_file(), CATALOG)
        records = json.loads(CATALOG.read_text(encoding="utf-8"))
        by_level = {}
        by_name = {}
        for record in records:
            by_level.setdefault(int(record["land_level_need"]), []).append(record)
            by_name[str(record["name"])] = record

        self.assertEqual(["晚香玉"], [item["name"] for item in by_level[134]])
        self.assertNotIn("菠萝蜜", by_name)
        self.assertEqual("crop_132", by_name["蓝铃花"]["asset_name"])
        self.assertEqual("crop_172", by_name["宋梅"]["asset_name"])

    def test_catalog_metrics_match_v237_multi_season_rules(self):
        namespace = load_functions(
            "_qqfarm_crop_growth_phase_seconds",
            "_qqfarm_crop_total_growth_seconds",
            "_qqfarm_crop_exp_per_second",
            "_qqfarm_crop_profit_per_hour",
        )
        crop = {
            "name": "晚香玉",
            "seasons": 2,
            "grow_phases": "种子:2400;发芽:2400;小叶子:2400;大叶子:3600;花蕾:3600;盛开:0;",
            "exp": 867,
            "fruit": {"count": 200, "sell_price": 117},
            "seed_price": 9360,
        }

        self.assertEqual(
            [2400, 2400, 2400, 3600, 3600],
            namespace["_qqfarm_crop_growth_phase_seconds"](crop),
        )
        self.assertEqual(
            21600,
            namespace["_qqfarm_crop_total_growth_seconds"](crop),
        )
        self.assertAlmostEqual(
            0.0802777778,
            namespace["_qqfarm_crop_exp_per_second"](crop),
            places=8,
        )
        self.assertAlmostEqual(
            6240.0,
            namespace["_qqfarm_crop_profit_per_hour"](crop),
            places=6,
        )

    def test_catalog_asset_lookup_uses_authoritative_resource_name(self):
        namespace = load_functions(
            "_qqfarm_v237_crop_catalog_path",
            "_qqfarm_load_v237_crop_catalog",
            "_qqfarm_v237_crop_by_name",
            "_qqfarm_v237_crop_asset_name",
        )
        lookup = namespace["_qqfarm_v237_crop_asset_name"]

        self.assertEqual("crop_174", lookup("晚香玉"))
        self.assertEqual("crop_132", lookup("蓝铃花"))
        self.assertEqual("crop_172", lookup("宋梅"))
        self.assertEqual("", lookup("菠萝蜜"))

    def test_native_crop_modules_receive_v237_data_and_asset_lookup(self):
        namespace = load_functions(
            "_qqfarm_v237_crop_catalog_path",
            "_qqfarm_load_v237_crop_catalog",
            "_qqfarm_crop_growth_phase_seconds",
            "_qqfarm_crop_total_growth_seconds",
            "_qqfarm_crop_profit_per_hour",
            "_qqfarm_v237_crop_by_name",
            "_qqfarm_v237_crop_asset_name",
            "_wrap_native_v237_crop_asset_name_func",
            "_patch_native_v237_crop_catalog_data_for_module",
        )
        namespace["_write"] = lambda _message: None
        original_rows = [{"name": "菠萝蜜", "land_level_need": 134}]
        original_asset_map = {"菠萝蜜": "crop_16"}
        original_profit_map = {"菠萝蜜": 1.0}
        module = types.SimpleNamespace(
            __name__="bot._q17ae55bf47.crop_catalog",
            CROPS=original_rows,
            _CROP_ASSET_NAME_MAP=original_asset_map,
            _CROP_PROFIT_PER_HOUR=original_profit_map,
            get_crop_asset_name=lambda crop_name: "old:" + str(crop_name),
        )

        changed = namespace[
            "_patch_native_v237_crop_catalog_data_for_module"
        ](module, "fixture")

        self.assertGreaterEqual(changed, 5)
        self.assertIs(original_rows, module.CROPS)
        self.assertIs(original_asset_map, module._CROP_ASSET_NAME_MAP)
        self.assertIs(original_profit_map, module._CROP_PROFIT_PER_HOUR)
        sidecar_rows = module.__qqfarm_v237_crop_catalog_rows__
        self.assertEqual(132, len(sidecar_rows))
        self.assertNotIn("菠萝蜜", {item["name"] for item in sidecar_rows})
        self.assertEqual(
            "crop_132",
            module.__qqfarm_v237_crop_asset_map__["蓝铃花"],
        )
        self.assertEqual("crop_172", module.get_crop_asset_name("宋梅"))
        self.assertEqual("old:不存在作物", module.get_crop_asset_name("不存在作物"))
        self.assertGreater(
            module.__qqfarm_v237_crop_profit_per_hour__["晚香玉"],
            0.0,
        )

    def test_native_positional_crop_rows_keep_their_original_schema(self):
        namespace = load_functions(
            "_qqfarm_v237_crop_catalog_path",
            "_qqfarm_load_v237_crop_catalog",
            "_qqfarm_crop_growth_phase_seconds",
            "_qqfarm_crop_total_growth_seconds",
            "_qqfarm_crop_profit_per_hour",
            "_qqfarm_v237_crop_by_name",
            "_qqfarm_v237_crop_asset_name",
            "_wrap_native_v237_crop_asset_name_func",
            "_patch_native_v237_crop_catalog_data_for_module",
        )
        namespace["_write"] = lambda _message: None
        original_rows = [("菠萝蜜", 134, "crop_16")]
        original_asset_map = [("菠萝蜜", "crop_16")]
        original_profit_map = [("菠萝蜜", 1.0)]
        module = types.SimpleNamespace(
            __name__="bot._q17ae55bf47.crop_catalog",
            CROPS=original_rows,
            _CROP_ASSET_NAME_MAP=original_asset_map,
            _CROP_PROFIT_PER_HOUR=original_profit_map,
            get_crop_asset_name=lambda crop_name: "old:" + str(crop_name),
        )

        namespace[
            "_patch_native_v237_crop_catalog_data_for_module"
        ](module, "positional-fixture")

        self.assertIs(original_rows, module.CROPS)
        self.assertIs(original_asset_map, module._CROP_ASSET_NAME_MAP)
        self.assertIs(original_profit_map, module._CROP_PROFIT_PER_HOUR)
        self.assertEqual("菠萝蜜", module.CROPS[0][0])
        self.assertEqual("crop_172", module.get_crop_asset_name("宋梅"))


if __name__ == "__main__":
    unittest.main()
