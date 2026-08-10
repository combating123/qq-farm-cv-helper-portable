import ast
import time
import types
import unittest
from unittest.mock import ANY
from pathlib import Path

import numpy as np


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
    namespace = {"np": np, "__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def states_with_only_l01_empty():
    return {
        slot_id: {
            "state": "empty" if slot_id == "L01" else "occupied-1x1",
        }
        for slot_id in SLOT_IDS
    }


def states_with_l01_occupied():
    return {
        slot_id: {"state": "occupied-1x1"}
        for slot_id in SLOT_IDS
    }


class V383PreopenedPanelStrictLedgerBridgeTests(unittest.TestCase):
    def _namespace(self):
        return load_functions(
            "_qqfarm_build_24_plot_ledger",
            "_qqfarm_validate_24_plot_transaction",
            "_qqfarm_commit_current_frame_planting_transaction",
            "_wrap_planting_outcome_verify_func",
        )

    def test_preopened_1x1_uses_unobscured_baseline_closes_shelf_then_commits_only_l01(self):
        """A selected shelf card is an interaction surface, never the before/after ledger.

        The preflight path owns one already-fresh no-panel ledger.  The action
        drags exactly L01 while the shelf is open, then closes the shelf and
        proves the post-action frame before the strict bridge may commit.
        """
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        before = build(
            states_with_only_l01_empty(),
            frame_id="preopen-board-before",
            board_signature="fixture-camera",
            captured_at=100.0,
        )
        after = build(
            states_with_l01_occupied(),
            frame_id="after-panel-close",
            board_signature="fixture-camera",
            captured_at=101.0,
        )
        panel_frame = object()
        after_frame = object()
        land = {"slot_id": "L01", "center": (185, 454)}
        seed = {"card": "#2", "center": (136, 511), "is_seed": True}
        events = []
        direct_calls = []
        metric_calls = []
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=1,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
            planting_visual_verify_delay_seconds=0.0,
            # This strict baseline is captured immediately before the land
            # click opens the seed shelf.  It has one-shot scope.
            _qqfarm_preopened_strict_before_ledger=before,
            _qqfarm_preopened_strict_before_ledger_ts=time.time(),
        )

        def native_execute(owner, selected_seed, action_frame, lands, crop_name):
            raise AssertionError("the one-slot shelf action must use direct drag")

        def direct_drag(owner, seed_center, land_center, *, source_globals, name):
            self.assertIs(bot, owner)
            direct_calls.append((tuple(seed_center), tuple(land_center), name))
            events.append("drag")
            return True

        def close_seed_panel(owner, panel_settle=0.35):
            self.assertIs(bot, owner)
            self.assertEqual("drag", events[-1])
            events.append("close")
            return True, after_frame, "panel-closed"

        def unexpected_capture(_owner):
            raise AssertionError("strict bridge must not read the open shelf as its ledger")

        def capture_ledger(frame, *, frame_id, captured_at):
            self.assertIs(after_frame, frame)
            self.assertTrue(frame_id.startswith("planting-after-"))
            self.assertGreaterEqual(captured_at, 100.0)
            return after

        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_qqfarm_candidate_is_quad_seed": lambda *_args, **_kwargs: False,
            "_qqfarm_backpack_nonseed_popup": lambda *_args, **_kwargs: None,
            "_qqfarm_update_home_priority": lambda *_args, **_kwargs: None,
            "_qqfarm_mark_visual_planting_success": (
                lambda _bot, before_count, after_count, **kwargs: (
                    metric_calls.append((before_count, after_count, kwargs)), True
                )[1]
            ),
            "_get_frame_from_bot": unexpected_capture,
            "_qqfarm_capture_current_frame_24_slot_ledger": capture_ledger,
            "_qqfarm_resolve_attempted_slot_ids": (
                lambda ledger, attempted_lands, *, planting_mode: {
                    "resolved": ledger is before and attempted_lands == [land],
                    "reason": "resolved",
                    "attempted_slots": ("L01",),
                    "planting_mode": planting_mode,
                }
            ),
            "_qqfarm_drag_single_backpack_seed": direct_drag,
            "_qqfarm_close_seed_panel_for_board_refresh": close_seed_panel,
        })
        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native_execute,
            "fixture.preopened-1x1",
        )

        result = wrapped(bot, seed, panel_frame, [land], "FIXTURE_1X1_SEED")

        self.assertTrue(changed)
        self.assertTrue(result, vars(bot))
        self.assertEqual(
            [((136, 511), (185, 454), "fixture.preopened-1x1")],
            direct_calls,
        )
        self.assertEqual(["drag", "close"], events)
        transaction = bot._qqfarm_last_planting_transaction
        self.assertTrue(transaction["committed"], transaction)
        self.assertEqual(("L01",), transaction["attempted_slots"])
        self.assertEqual(("L01",), transaction["committed_slots"])
        self.assertEqual(1, transaction["before_empty_count"])
        self.assertEqual(0, transaction["after_empty_count"])
        self.assertEqual([(1, 0, ANY)], metric_calls)
        self.assertTrue(bot._qqfarm_last_planting_outcome_verified)
        self.assertFalse(hasattr(bot, "_qqfarm_preopened_strict_before_ledger"))
        self.assertTrue(
            getattr(
                bot,
                "_qqfarm_preopened_strict_shelf_closed_after_transaction",
                False,
            ),
            "a committed strict shelf transaction must tell the scheduler to reopen",
        )


    def test_preflight_captures_one_unobscured_strict_baseline_before_opening_the_shelf(self):
        """The shelf opener must hand the strict bridge a fresh no-panel ledger."""
        namespace = load_functions("_qqfarm_open_seed_panel_for_backpack_preflight")
        before_frame = object()
        panel_frame = object()
        before_ledger = {
            "capture_status": "aligned",
            "capture_reason": "fixture-aligned",
            "unknown_count": 0,
            "ui_blocked": False,
            "slots": states_with_only_l01_empty(),
            "slot_centers": {
                slot_id: (185 + index, 454 + index)
                for index, slot_id in enumerate(SLOT_IDS)
            },
            "frame_id": "before-open",
            "captured_at": 100.0,
        }
        events = []
        bot = types.SimpleNamespace()

        def capture(owner):
            self.assertIs(bot, owner)
            if "click" not in events:
                events.append("capture-before")
                return before_frame
            events.append("capture-panel")
            return panel_frame

        def click(*_args):
            events.append("click")
            return True

        def ledger(frame, *, frame_id, captured_at):
            self.assertIs(before_frame, frame)
            self.assertTrue(frame_id.startswith("preopened-before-"))
            self.assertGreaterEqual(captured_at, 100.0)
            return dict(before_ledger)

        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_get_frame_from_bot": capture,
            "_friend_guard_post_client_click": click,
            "_seed_panel_strip_visible": lambda frame: frame is panel_frame,
            "_qqfarm_capture_current_frame_24_slot_ledger": ledger,
        })

        opened, frame, reason = namespace[
            "_qqfarm_open_seed_panel_for_backpack_preflight"
        ](
            bot,
            [{
                "slot_id": "L01",
                "center": (185, 454),
                "_qqfarm_visual_soil_proof": True,
            }],
            panel_settle=0.0,
        )

        self.assertTrue(opened)
        self.assertIs(panel_frame, frame)
        self.assertEqual("panel-confirmed", reason)
        self.assertEqual(["capture-before", "click", "capture-panel"], events)
        self.assertEqual(
            before_ledger,
            bot._qqfarm_preopened_strict_before_ledger,
        )
        self.assertGreater(bot._qqfarm_preopened_strict_before_ledger_ts, 0.0)


if __name__ == "__main__":
    unittest.main()
