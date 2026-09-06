import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
SLOT_IDS = tuple(f"L{index:02d}" for index in range(1, 25))


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
    namespace = {"__file__": str(HOOK), "__name__": "v433_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def full_board_ledger():
    return {
        "capture_status": "aligned",
        "capture_reason": "physical-window-normalized-full-board-observation",
        "full_board_confirmed": True,
        "occupied_count": 24,
        "empty_count": 0,
        "unknown_count": 0,
        "ui_blocked": False,
        "click_safe": False,
        "observation_only": True,
        "slots": {
            slot_id: {"state": "occupied-1x1"}
            for slot_id in SLOT_IDS
        },
        "slot_centers": {},
    }


def non_full_ledger(*, empty=0, unknown=0, ui_blocked=False):
    occupied = 24 - int(empty) - int(unknown)
    states = []
    states.extend(["occupied-1x1"] * max(0, occupied))
    states.extend(["empty"] * int(empty))
    states.extend(["unknown"] * int(unknown))
    return {
        "capture_status": "aligned",
        "capture_reason": "geometry-anchors",
        "full_board_confirmed": False,
        "occupied_count": occupied,
        "empty_count": int(empty),
        "unknown_count": int(unknown),
        "ui_blocked": bool(ui_blocked),
        "click_safe": not bool(ui_blocked),
        "observation_only": False,
        "slots": {
            slot_id: {"state": states[index - 1]}
            for index, slot_id in enumerate(SLOT_IDS, 1)
        },
        "slot_centers": {},
    }


class NativeFullBoardPlantingPreflight20260809Tests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_functions(
            "_qqfarm_is_native_full_board_observation",
            "_qqfarm_clear_native_full_board_planting_state",
            "_wrap_native_v225_full_board_planting_preflight",
            "_patch_native_v225_full_board_preflight_for_module",
        )

    def test_exact_full_board_observation_does_not_skip_native_planting(self):
        """A single physical 24/0/0 frame is observation only, not a route decision."""
        events = []
        logs = []
        frame = object()
        bot = types.SimpleNamespace(
            # This fixture represents stale non-empty routing latches only;
            # the pending-empty conflict is covered by the v481 regression.
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_empty_land_remaining=0,
            _qqfarm_backpack_inventory_scan_pending=True,
            _qqfarm_force_self_cycle_next=True,
            _qqfarm_cycle_branch_hint="self",
            _qqfarm_recent_empty_lands=[{"slot_id": "L07"}],
            _qqfarm_recent_empty_land_count=1,
            _qqfarm_recent_empty_land_centers=[(17, 27)],
            _qqfarm_fixed_slot_pending_slot_ids=("L07",),
            _qqfarm_fixed_slot_pending_lands=[{"slot_id": "L07"}],
            _qqfarm_fixed_slot_pending_quad_groups=(("L01", "L02", "L05", "L06"),),
        )

        def native_home_planting(owner, *_args, **_kwargs):
            events.append("native-handle-home-planting")
            owner.get_current_player_level()
            owner.choose_planting_strategy()
            return "native-result"

        bot.get_current_player_level = lambda: events.append("level-ocr")
        bot.choose_planting_strategy = lambda: events.append("seed-strategy")
        self.namespace.update({
            "_write": lambda message: logs.append(str(message)),
            "_qqfarm_capture_visible_farm_frame": (
                lambda prefer_desktop=False: (
                    self.assertTrue(prefer_desktop) or frame
                )
            ),
            "_qqfarm_capture_current_frame_24_slot_ledger": (
                lambda candidate, **_kwargs: (
                    self.assertIs(frame, candidate) or full_board_ledger()
                )
            ),
        })

        wrapped, changed = self.namespace[
            "_wrap_native_v225_full_board_planting_preflight"
        ](native_home_planting, "FarmBotCV.handle_home_planting")

        self.assertTrue(changed)
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(
            ["native-handle-home-planting", "level-ocr", "seed-strategy"],
            events,
        )
        self.assertFalse(bot._qqfarm_home_empty_land_pending)
        self.assertTrue(bot._qqfarm_backpack_inventory_scan_pending)
        self.assertTrue(bot._qqfarm_force_self_cycle_next)
        self.assertEqual("self", bot._qqfarm_cycle_branch_hint)
        self.assertEqual([{"slot_id": "L07"}], bot._qqfarm_recent_empty_lands)
        self.assertEqual(1, bot._qqfarm_recent_empty_land_count)
        self.assertEqual([(17, 27)], bot._qqfarm_recent_empty_land_centers)
        self.assertEqual(("L07",), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual([{"slot_id": "L07"}], bot._qqfarm_fixed_slot_pending_lands)
        self.assertEqual((("L01", "L02", "L05", "L06"),), bot._qqfarm_fixed_slot_pending_quad_groups)
        self.assertTrue(any("observation-only" in line.lower() for line in logs), logs)

    def test_any_empty_unknown_or_overlay_frame_delegates_to_native_planting(self):
        """This guard never converts a real/uncertain planting state into a skip."""
        ledgers = [
            non_full_ledger(empty=1),
            non_full_ledger(unknown=1),
            non_full_ledger(ui_blocked=True),
        ]
        events = []
        bot = types.SimpleNamespace(_qqfarm_home_empty_land_pending=True)

        def native_home_planting(owner, *_args, **_kwargs):
            events.append("native")
            return "native-result"

        self.namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_qqfarm_capture_visible_farm_frame": lambda **_kwargs: object(),
            "_qqfarm_capture_current_frame_24_slot_ledger": (
                lambda _frame, **_kwargs: ledgers.pop(0)
            ),
        })
        wrapped, changed = self.namespace[
            "_wrap_native_v225_full_board_planting_preflight"
        ](native_home_planting, "FarmBotCV.handle_home_planting")

        self.assertTrue(changed)
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(["native", "native", "native"], events)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)

    def test_native_owner_patches_only_native_home_planting_and_keeps_legacy_rollback_clean(self):
        """The narrow preflight is installed only under native-runtime ownership."""
        self.namespace.update({
            "_qqfarm_legacy_wrapper_allowed": lambda _label: False,
            "_write": lambda *_args, **_kwargs: None,
        })

        class FarmBotCV:
            def handle_home_planting(self):
                return "native"

        module = types.SimpleNamespace(__name__="bot.application.flows", FarmBotCV=FarmBotCV)
        changed = self.namespace[
            "_patch_native_v225_full_board_preflight_for_module"
        ](module, "v433-test")
        self.assertEqual(1, changed)
        self.assertTrue(getattr(
            FarmBotCV.handle_home_planting,
            "__qqfarm_native_v225_full_board_preflight_wrapped__",
            False,
        ))
        self.assertEqual(0, self.namespace[
            "_patch_native_v225_full_board_preflight_for_module"
        ](module, "v433-repeat"))

        self.namespace["_qqfarm_legacy_wrapper_allowed"] = lambda _label: True

        class LegacyFarmBotCV:
            def handle_home_planting(self):
                return "legacy"

        legacy_module = types.SimpleNamespace(
            __name__="bot.application.flows", FarmBotCV=LegacyFarmBotCV
        )
        self.assertEqual(0, self.namespace[
            "_patch_native_v225_full_board_preflight_for_module"
        ](legacy_module, "v433-legacy"))
        self.assertFalse(getattr(
            LegacyFarmBotCV.handle_home_planting,
            "__qqfarm_native_v225_full_board_preflight_wrapped__",
            False,
        ))


if __name__ == "__main__":
    unittest.main()
