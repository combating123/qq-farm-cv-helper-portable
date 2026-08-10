import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
SLOT_IDS = tuple("L%02d" % index for index in range(1, 25))


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
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def observations(empty_slots):
    empty_slots = set(empty_slots)
    return {
        slot_id: {
            "state": "empty" if slot_id in empty_slots else "occupied-1x1",
        }
        for slot_id in SLOT_IDS
    }


def ledger(build, *, frame_id, captured_at, empty_slots):
    result = build(
        observations(empty_slots),
        frame_id=frame_id,
        board_signature="fixture-dynamic-grid",
        captured_at=captured_at,
    )
    result.update({
        "capture_status": "aligned",
        "capture_reason": "fixture",
        "slot_centers": {
            slot_id: (index * 10, index * 7)
            for index, slot_id in enumerate(SLOT_IDS, start=1)
        },
    })
    return result


class CommittedLedgerPendingStateTests(unittest.TestCase):
    def test_committed_transaction_persists_exact_after_frame_pending_slot_ids_and_centers(self):
        namespace = load_functions(
            "_qqfarm_build_24_plot_ledger",
            "_qqfarm_validate_24_plot_transaction",
            "_qqfarm_commit_current_frame_planting_transaction",
        )
        build = namespace["_qqfarm_build_24_plot_ledger"]
        commit = namespace["_qqfarm_commit_current_frame_planting_transaction"]
        before = ledger(
            build,
            frame_id="before",
            captured_at=100.0,
            empty_slots=("L01", "L02", "L03"),
        )
        after = ledger(
            build,
            frame_id="after",
            captured_at=101.0,
            empty_slots=("L02", "L03"),
        )
        bot = types.SimpleNamespace()

        result = commit(
            bot,
            before,
            after,
            attempted_slots=("L01",),
            planting_mode="1x1",
        )

        self.assertTrue(result["committed"], result)
        self.assertEqual(("L02", "L03"), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(
            ["L02", "L03"],
            [item["slot_id"] for item in bot._qqfarm_fixed_slot_pending_lands],
        )
        self.assertEqual(
            [after["slot_centers"]["L02"], after["slot_centers"]["L03"]],
            [item["center"] for item in bot._qqfarm_fixed_slot_pending_lands],
        )
        self.assertEqual(2, bot._qqfarm_recent_empty_land_count)
        self.assertEqual(101.0, bot._qqfarm_recent_empty_land_ts)
        self.assertEqual(("L02", "L03"), tuple(
            item["slot_id"] for item in bot._qqfarm_recent_empty_lands
        ))


    def test_rejected_transaction_retains_exact_before_frame_pending_slots(self):
        """A rejected action keeps the last verified before-frame Lxx work list."""
        namespace = load_functions(
            "_qqfarm_build_24_plot_ledger",
            "_qqfarm_validate_24_plot_transaction",
            "_qqfarm_commit_current_frame_planting_transaction",
        )
        build = namespace["_qqfarm_build_24_plot_ledger"]
        commit = namespace["_qqfarm_commit_current_frame_planting_transaction"]
        before = ledger(
            build,
            frame_id="before",
            captured_at=100.0,
            empty_slots=("L01", "L02", "L03"),
        )
        after = ledger(
            build,
            frame_id="after-overlay",
            captured_at=101.0,
            empty_slots=("L01", "L02", "L03"),
        )
        after["ui_blocked"] = True
        bot = types.SimpleNamespace()

        result = commit(
            bot,
            before,
            after,
            attempted_slots=("L01",),
            planting_mode="1x1",
        )

        self.assertFalse(result["committed"], result)
        self.assertEqual("ui-overlay-visible", result["reason"])
        self.assertEqual(("L01", "L02", "L03"), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(3, bot._qqfarm_recent_empty_land_count)
        self.assertEqual(100.0, bot._qqfarm_recent_empty_land_ts)
        self.assertEqual(
            [before["slot_centers"][slot_id] for slot_id in ("L01", "L02", "L03")],
            bot._qqfarm_recent_empty_land_centers,
        )

    def test_unknown_ledger_does_not_replace_existing_verified_pending_slots(self):
        """An ambiguous current frame never overwrites a prior verified Lxx queue."""
        namespace = load_functions(
            "_qqfarm_build_24_plot_ledger",
            "_qqfarm_validate_24_plot_transaction",
            "_qqfarm_commit_current_frame_planting_transaction",
        )
        build = namespace["_qqfarm_build_24_plot_ledger"]
        commit = namespace["_qqfarm_commit_current_frame_planting_transaction"]
        before = ledger(
            build,
            frame_id="before-unknown",
            captured_at=100.0,
            empty_slots=("L01",),
        )
        before["slots"]["L01"]["state"] = "unknown"
        before["unknown_count"] = 1
        after = ledger(
            build,
            frame_id="after",
            captured_at=101.0,
            empty_slots=(),
        )
        bot = types.SimpleNamespace(
            _qqfarm_fixed_slot_pending_slot_ids=("L17",),
            _qqfarm_fixed_slot_pending_lands=[
                {"slot_id": "L17", "center": (170, 119)}
            ],
            _qqfarm_recent_empty_lands=[
                {"slot_id": "L17", "center": (170, 119)}
            ],
            _qqfarm_recent_empty_land_count=1,
            _qqfarm_recent_empty_land_centers=[(170, 119)],
        )

        result = commit(
            bot,
            before,
            after,
            attempted_slots=("L01",),
            planting_mode="1x1",
        )

        self.assertFalse(result["committed"], result)
        self.assertEqual("unknown-slot-state", result["reason"])
        self.assertEqual(("L17",), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(["L17"], [item["slot_id"] for item in bot._qqfarm_recent_empty_lands])


if __name__ == "__main__":
    unittest.main()
