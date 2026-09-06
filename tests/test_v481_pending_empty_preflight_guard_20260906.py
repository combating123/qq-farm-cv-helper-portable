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
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v481_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def full_board_ledger():
    return {
        "capture_status": "aligned",
        "full_board_confirmed": True,
        "occupied_count": 24,
        "empty_count": 0,
        "unknown_count": 0,
        "ui_blocked": False,
        "slots": {
            f"L{index:02d}": {"state": "occupied-1x1"}
            for index in range(1, 25)
        },
    }


class PendingEmptyPreflightGuardTests(unittest.TestCase):
    def test_full_board_frame_does_not_release_pending_empty_land_work(self):
        """A conflicting full-board frame must not route away from known empty land."""
        namespace = load_functions(
            "_wrap_native_v225_full_board_planting_preflight",
            "_qqfarm_is_native_full_board_observation",
            "_qqfarm_clear_native_full_board_planting_state",
        )
        events = []
        bot = types.SimpleNamespace(
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=1,
            _qqfarm_force_self_cycle_next=True,
        )

        def native_home_planting(owner, *_args, **_kwargs):
            events.append("native")
            return "native-result"

        namespace["_qqfarm_capture_visible_farm_frame"] = (
            lambda **_kwargs: object()
        )
        namespace["_qqfarm_capture_current_frame_24_slot_ledger"] = (
            lambda *_args, **_kwargs: full_board_ledger()
        )
        wrapped, changed = namespace[
            "_wrap_native_v225_full_board_planting_preflight"
        ](native_home_planting, "FarmBotCV.handle_home_planting")

        self.assertTrue(changed)
        self.assertEqual("native-result", wrapped(bot))
        self.assertEqual(["native"], events)
        self.assertTrue(bot._qqfarm_home_empty_land_pending)
        self.assertEqual(1, bot._qqfarm_home_empty_land_remaining)


if __name__ == "__main__":
    unittest.main()
