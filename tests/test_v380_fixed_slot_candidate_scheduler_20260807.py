import ast
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


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
    namespace = {"__file__": str(HOOK), "np": np}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FakeClock:
    def __init__(self, now):
        self.now = float(now)

    def time(self):
        return self.now


class FixedSlotCandidateSchedulerTests(unittest.TestCase):
    def _namespace(self):
        namespace = load_functions(
            "_qqfarm_run_preopened_backpack_candidates_fast",
        )
        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_seed_panel_strip_visible": lambda _frame: True,
            "_fast_seed_badge_candidates_from_frame": (
                lambda _frame, capacity_hint=None: [
                    {"card": "#1", "center": (68, 511), "is_seed": True},
                    {"card": "#2", "center": (136, 511), "is_seed": True},
                    {"card": "#3", "center": (204, 511), "is_seed": True},
                    {"card": "#4", "center": (272, 511), "is_seed": True},
                    {"card": "#5", "center": (340, 511), "is_seed": True},
                ]
            ),
            "_filter_backpack_planting_candidates": (
                lambda items, bot=None: (list(items), [], [])
            ),
            "_qqfarm_backpack_candidate_is_quarantined": (
                lambda _bot, _candidate, frame=None, now_ts=None: False
            ),
            "_qqfarm_candidate_is_quad_seed": (
                lambda candidate, bot=None: bool(candidate.get("is_quad_seed", False))
            ),
        })
        return namespace

    def test_1x1_candidate_chain_targets_one_named_slot_and_hard_stops_at_120_seconds(self):
        """A 1x1 candidate may receive one fixed Lxx target, never a full land list."""
        namespace = self._namespace()
        helper = namespace["_qqfarm_run_preopened_backpack_candidates_fast"]
        frame = object()
        lands = [
            {"slot_id": "L01", "center": (185, 454)},
            {"slot_id": "L02", "center": (214, 469)},
            {"slot_id": "L03", "center": (156, 469)},
        ]
        clock = FakeClock(119.9)
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=3,
            _qqfarm_recent_empty_lands=list(lands),
            _qqfarm_recent_empty_land_ts=clock.time(),
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_fixed_slot_chain_active=True,
            _qqfarm_fixed_slot_chain_started_ts=0.0,
            _qqfarm_fixed_slot_chain_deadline_ts=120.0,
        )
        calls = []

        def execute(owner, seed_match, target_lands, crop_name, run_post_fertilizer=False):
            calls.append((seed_match["card"], tuple(item["slot_id"] for item in target_lands)))
            if len(calls) == 1:
                owner._qqfarm_recent_empty_lands = list(lands[1:])
                owner._qqfarm_recent_empty_land_count = 2
                owner._qqfarm_last_planting_outcome_verified = True
                owner._qqfarm_last_planting_transaction = {
                    "committed": True,
                    "committed_slots": ("L01",),
                    "attempted_slots": ("L01",),
                    "planting_mode": "1x1",
                }
                clock.now = 120.0
                return True
            owner._qqfarm_last_planting_outcome_verified = False
            owner._qqfarm_last_planting_transaction = {
                "committed": False,
                "committed_slots": (),
                "attempted_slots": tuple(item["slot_id"] for item in target_lands),
                "planting_mode": "1x1",
            }
            return False

        with patch("time.time", clock.time):
            result = helper(
                bot,
                frame,
                list(lands),
                {"_execute_planting_by_mode": execute},
                "fixture-1x1",
                name="fixture.fixed-slot-deadline",
            )

        self.assertTrue(result[0])
        self.assertEqual([("#1", ("L01",))], calls)
        self.assertEqual(["L02", "L03"], [item["slot_id"] for item in result[1]])
        self.assertEqual(("L02", "L03"), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertTrue(bot._qqfarm_fixed_slot_chain_expired)

    def test_quad_candidate_is_skipped_without_a_predeclared_complete_physical_group(self):
        """The current #1 2x2 card must not be dragged over arbitrary 1x1 empties."""
        namespace = self._namespace()
        helper = namespace["_qqfarm_run_preopened_backpack_candidates_fast"]
        frame = object()
        lands = [
            {"slot_id": "L01", "center": (185, 454)},
            {"slot_id": "L02", "center": (214, 469)},
            {"slot_id": "L03", "center": (156, 469)},
        ]
        candidates = [
            {"card": "#1", "center": (68, 511), "is_seed": True, "is_quad_seed": True},
            {"card": "#2", "center": (136, 511), "is_seed": True},
        ]
        namespace["_fast_seed_badge_candidates_from_frame"] = (
            lambda _frame, capacity_hint=None: list(candidates)
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=3,
            _qqfarm_recent_empty_lands=list(lands),
            _qqfarm_recent_empty_land_ts=time.time(),
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_fixed_slot_pending_quad_groups=(),
        )
        calls = []

        def execute(owner, seed_match, target_lands, crop_name, run_post_fertilizer=False):
            calls.append((seed_match["card"], tuple(item["slot_id"] for item in target_lands)))
            owner._qqfarm_recent_empty_lands = list(lands[1:])
            owner._qqfarm_recent_empty_land_count = 2
            owner._qqfarm_last_planting_outcome_verified = True
            committed_slot = target_lands[0]["slot_id"]
            owner._qqfarm_last_planting_transaction = {
                "committed": True,
                "committed_slots": (committed_slot,),
                "attempted_slots": (committed_slot,),
                "planting_mode": "1x1",
            }
            return True

        result = helper(
            bot,
            frame,
            list(lands),
            {"_execute_planting_by_mode": execute},
            "fixture-quad-skip",
            name="fixture.fixed-slot-quad-skip",
        )

        self.assertTrue(result[0])
        self.assertEqual([("#2", ("L01",)), ("#2", ("L02",)), ("#2", ("L03",))], calls)


if __name__ == "__main__":
    unittest.main()
