import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
SLOT_IDS = tuple(f"L{index:02d}" for index in range(1, 25))


def load_functions(*names):
    """Load the live hook functions without starting the QQ assistant.

    The future transaction helper is intentionally optional during RED: before
    implementation the existing strict entry is still loaded and the behavioral
    assertion fails because it invokes only one native self pass.
    """
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes_by_name = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    selected_names = list(names)
    helper_name = "_qqfarm_run_strict_24slot_harvest_then_replant_transaction"
    if helper_name in nodes_by_name:
        selected_names.append(helper_name)
    missing = [name for name in selected_names if name not in nodes_by_name]
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(
        body=[nodes_by_name[name] for name in selected_names],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FakeClock:
    def __init__(self, now=0.0):
        self.now = float(now)

    def time(self):
        return self.now


class Frame:
    def __init__(self, label):
        self.label = label


def ledger(frame, empty_slots):
    empty = tuple(empty_slots)
    empty_set = set(empty)
    centers = {
        slot_id: (100 + index, 300 + index)
        for index, slot_id in enumerate(SLOT_IDS, start=1)
    }
    return {
        "capture_status": "aligned",
        "capture_reason": "fixture-aligned",
        "ui_blocked": False,
        "unknown_count": 0,
        "frame_id": frame.label,
        "captured_at": 1.0,
        "slot_ids": SLOT_IDS,
        "slot_centers": centers,
        "slots": {
            slot_id: {
                "state": "empty" if slot_id in empty_set else "occupied-1x1",
                "land_quality": "gold" if index % 2 else "purple",
            }
            for index, slot_id in enumerate(SLOT_IDS, start=1)
        },
        "empty_slots": empty,
        "occupied_slots": tuple(
            slot_id for slot_id in SLOT_IDS if slot_id not in empty_set
        ),
        "empty_count": len(empty),
        "occupied_count": 24 - len(empty),
    }


class StrictHarvestDrainThenSingleSlotPlantingTests(unittest.TestCase):
    def test_strict_entry_drains_each_mature_pass_then_hands_exact_empty_slots_to_scheduler(self):
        """Three mature plots become L01-L03, then only that fixed list is planted.

        The regression reproduces the current field failure: the legacy strict
        entry invokes one native self pass and returns, which leaves the other
        mature crops and their newly empty Lxx slots for unrelated later cycles.
        """
        namespace = load_functions("_qqfarm_run_strict_self_planting_cycle")
        clock = FakeClock(0.0)
        board_0 = Frame("board-0-full")
        board_1 = Frame("board-1-l01-empty")
        board_2 = Frame("board-2-l01-l02-empty")
        board_3 = Frame("board-3-l01-l03-empty")
        board_final = Frame("board-final-full")
        after_native_frames = iter((board_1, board_2, board_3, board_3, board_final))
        observed = {
            board_0: ledger(board_0, ()),
            board_1: ledger(board_1, ("L01",)),
            board_2: ledger(board_2, ("L01", "L02")),
            board_3: ledger(board_3, ("L01", "L02", "L03")),
            board_final: ledger(board_final, ()),
        }
        native_frames = []
        legacy_calls = []
        preflights = []
        scheduler_calls = []
        context = types.SimpleNamespace()

        def capture(_owner):
            if not native_frames:
                return board_0
            return next(after_native_frames)

        def native_self(owner, current_frame):
            self.assertIs(context, owner)
            native_frames.append(current_frame.label)
            # The production strict transaction marker is what the legacy
            # planting gate consumes.  A missing marker reproduces the old
            # same-pass 225-second whole-board escape.
            if not getattr(owner, "_qqfarm_strict_24slot_transaction_active", False):
                legacy_calls.append(current_frame.label)
            return {"success": True, "action": "harvest", "harvested_count": 1}

        def observe(frame, *, frame_id, captured_at):
            del frame_id, captured_at
            return observed[frame]

        def open_seed_panel(owner, lands, panel_settle=0.35):
            del panel_settle
            self.assertIs(context, owner)
            preflights.append(tuple(item["slot_id"] for item in lands))
            return True, Frame("seed-panel"), "panel-confirmed"

        def schedule(owner, panel_frame, lands, runtime_globals, crop_name, name=""):
            self.assertIs(context, owner)
            self.assertEqual("seed-panel", panel_frame.label)
            self.assertEqual(("L01", "L02", "L03"), tuple(item["slot_id"] for item in lands))
            self.assertTrue(owner._qqfarm_fixed_slot_chain_active)
            self.assertEqual(120.0, owner._qqfarm_fixed_slot_chain_deadline_ts)
            self.assertIsInstance(runtime_globals, dict)
            scheduler_calls.append((tuple(item["slot_id"] for item in lands), crop_name, name))
            return True, [], True, {"card": "#2"}, True

        context.process_self_farm = native_self
        namespace.update({
            "time": clock,
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_get_frame_from_bot": capture,
            "_qqfarm_strict_self_scene_state": lambda _frame: False,
            "_friend_guard_friend_ui_state": lambda _frame: False,
            "_invoke_friend_guard_action": (
                lambda action, _identity, args, kwargs: action(*args, **kwargs)
            ),
            "_qqfarm_capture_current_frame_24_slot_ledger": observe,
            "_qqfarm_open_seed_panel_for_backpack_preflight": open_seed_panel,
            "_qqfarm_run_preopened_backpack_candidates_fast": schedule,
        })

        result = namespace["_qqfarm_run_strict_self_planting_cycle"](context)

        self.assertTrue(result)
        self.assertEqual(
            ["board-0-full", "board-1-l01-empty", "board-2-l01-l02-empty", "board-3-l01-l03-empty"],
            native_frames,
        )
        self.assertEqual([], legacy_calls)
        self.assertEqual([("L01", "L02", "L03")], preflights)
        self.assertEqual(1, len(scheduler_calls))
        self.assertEqual((), context._qqfarm_fixed_slot_pending_slot_ids)
        self.assertFalse(context._qqfarm_fixed_slot_chain_active)
        self.assertFalse(hasattr(context, "_qqfarm_strict_24slot_transaction_active"))

    def test_full_commit_logs_elapsed_before_chain_state_is_cleared(self):
        """Completion evidence retains the actual transaction duration."""
        namespace = load_functions("_qqfarm_run_strict_24slot_harvest_then_replant_transaction")
        clock = FakeClock(107.5)
        initial = Frame("initial-l01-empty")
        after_harvest = Frame("after-harvest-l01-empty")
        final = Frame("final-full")
        captures = iter((after_harvest, final))
        logs = []
        context = types.SimpleNamespace(
            _qqfarm_fixed_slot_chain_active=True,
            _qqfarm_fixed_slot_chain_expired=False,
            _qqfarm_fixed_slot_chain_started_ts=100.0,
            _qqfarm_fixed_slot_chain_deadline_ts=220.0,
        )
        observed = {
            initial: ledger(initial, ("L01",)),
            after_harvest: ledger(after_harvest, ("L01",)),
            final: ledger(final, ()),
        }

        def native_self(owner, current_frame):
            self.assertIs(context, owner)
            self.assertIs(initial, current_frame)
            return {"success": False, "action": "none"}

        def observe(frame, *, frame_id, captured_at):
            del frame_id, captured_at
            return observed[frame]

        context.process_self_farm = native_self
        namespace.update({
            "time": clock,
            "_write": lambda message: logs.append(str(message)),
            "_get_frame_from_bot": lambda _owner: next(captures),
            "_invoke_friend_guard_action": (
                lambda action, _identity, args, kwargs: action(*args, **kwargs)
            ),
            "_qqfarm_capture_current_frame_24_slot_ledger": observe,
            "_qqfarm_open_seed_panel_for_backpack_preflight": (
                lambda _owner, _lands, panel_settle=0.35: (
                    True, Frame("seed-panel"), "panel-confirmed"
                )
            ),
            "_qqfarm_run_preopened_backpack_candidates_fast": (
                lambda *_args, **_kwargs: (True, [], True, {"card": "#2"}, True)
            ),
        })

        result = namespace[
            "_qqfarm_run_strict_24slot_harvest_then_replant_transaction"
        ](context, initial_frame=initial)

        self.assertTrue(result)
        self.assertTrue(
            any("committed full board elapsed=7.500" in line for line in logs),
            logs,
        )
        self.assertEqual(0.0, context._qqfarm_fixed_slot_chain_started_ts)
    def test_strict_active_transaction_blocks_legacy_planting_inside_native_self_pass(self):
        """The native harvesting pass cannot re-enter the old multi-card flow."""
        namespace = load_functions("_wrap_post_harvest_rescan_planting_gate")
        calls = []
        context = types.SimpleNamespace(
            _qqfarm_strict_24slot_transaction_active=True,
            _qqfarm_post_harvest_rescan_remaining=0,
        )

        def legacy_planting(owner, frame):
            calls.append((owner, frame))
            return "legacy-result"

        namespace.update({
            "_friend_guard_context": lambda args, _kwargs: args[0],
            "_write": lambda *_args, **_kwargs: None,
            "time": FakeClock(1.0),
        })
        wrapped, changed = namespace["_wrap_post_harvest_rescan_planting_gate"](
            legacy_planting, "fixture.legacy-planting",
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(context, Frame("self-board")))
        self.assertEqual([], calls)
        self.assertTrue(context._qqfarm_force_self_cycle_next)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)


if __name__ == "__main__":
    unittest.main()
