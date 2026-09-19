import ast
import hashlib
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "live-v502-sparse-terrain-seedling-platform-full-board-sanitized-20260919.png"
)
FIXTURE_SHA256 = "C78F70994F0EC5B72ABE2F93117367E758152837E615FA197680D004D524BA2C"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes_by_name = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    missing = [name for name in names if name not in nodes_by_name]
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(missing))
    module = ast.Module(
        body=[nodes_by_name[name] for name in names],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    namespace = {"np": np, "cv2": cv2}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_v502_namespace():
    return load_functions(
        "_seed_panel_strip_visible",
        "_qqfarm_dynamic_viewport_plot_anchor_candidates",
        "_qqfarm_dynamic_viewport_crop_geometry_anchor_candidates",
        "_qqfarm_fit_dynamic_24_slot_lattice_from_geometry_anchors",
        "_qqfarm_build_24_plot_ledger",
        "_empty_land_candidate_has_seedling_occupancy",
        "_empty_land_candidate_has_crop_cover",
        "_qqfarm_capture_current_frame_24_slot_ledger",
        "_qqfarm_detect_outer_chrome_crop",
        "_qqfarm_normalize_window_owned_frame_for_business",
        "_qqfarm_full_board_observation_from_frame",
        "_wrap_detect_empty_lands_state",
    )


class V502SparseTerrainSeedlingPlatformFullBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        actual_hash = hashlib.sha256(FIXTURE.read_bytes()).hexdigest().upper()
        if actual_hash != FIXTURE_SHA256:
            raise AssertionError(f"fixture hash changed: {actual_hash}")
        cls.frame = cv2.imread(str(FIXTURE), cv2.IMREAD_COLOR)
        if cls.frame is None:
            raise AssertionError("fixture cannot be decoded")

    def test_current_full_board_with_sparse_terrain_and_platforms_is_24_occupied(self):
        """The live 138-level board is full even though only five soil anchors remain."""
        namespace = load_v502_namespace()

        observed = namespace["_qqfarm_full_board_observation_from_frame"](
            self.frame,
            now_ts=502.0,
        )

        self.assertIsInstance(observed, dict)
        self.assertEqual("aligned", observed["capture_status"], observed)
        self.assertEqual(
            "sparse-terrain-seedling-full-board-observation",
            observed["capture_reason"],
            observed,
        )
        self.assertTrue(observed["observation_only"], observed)
        self.assertFalse(observed["click_safe"], observed)
        self.assertTrue(observed["full_board_confirmed"], observed)
        self.assertEqual(24, observed["occupied_count"], observed)
        self.assertEqual(0, observed["empty_count"], observed)
        self.assertEqual(0, observed["unknown_count"], observed)
        self.assertIn(
            observed["_qqfarm_full_board_probe_source"],
            ("content-crop", "content-crop-minus", "content-crop-plus"),
        )

    def test_six_native_false_empty_hits_are_cleared_by_the_fresh_full_board(self):
        """Native template hits on occupied crops never gain land/shop authority."""
        namespace = load_v502_namespace()
        namespace["_write"] = lambda _message: None
        native_false_hits = [
            {"center": center, "score": 0.91}
            for center in (
                (249, 410),
                (220, 426),
                (279, 426),
                (190, 441),
                (249, 441),
                (308, 441),
            )
        ]
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_lands=list(native_false_hits),
            _qqfarm_recent_empty_land_count=6,
            _qqfarm_stable_empty_lands=list(native_false_hits),
            _qqfarm_stable_empty_land_count=6,
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=6,
            _qqfarm_force_self_cycle_next=True,
            _qqfarm_cycle_branch_hint="self",
            _qqfarm_post_harvest_pending=False,
            _qqfarm_single_harvest_planting_pending=False,
        )
        wrapped, changed = namespace["_wrap_detect_empty_lands_state"](
            lambda _owner, _frame=None: list(native_false_hits),
            "fixture.v502-live-full-board",
        )

        result = wrapped(bot, self.frame)

        self.assertTrue(changed)
        self.assertEqual([], result)
        self.assertEqual(0, bot._qqfarm_recent_empty_land_count)
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertEqual(0, bot._qqfarm_home_empty_land_remaining)
        self.assertFalse(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("", bot._qqfarm_cycle_branch_hint)


if __name__ == "__main__":
    unittest.main()
