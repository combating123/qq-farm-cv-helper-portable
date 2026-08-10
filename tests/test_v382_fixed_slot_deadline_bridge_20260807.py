import ast
import types
import unittest
from pathlib import Path
from unittest.mock import patch


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
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class FakeClock:
    def __init__(self, now):
        self.now = float(now)

    def time(self):
        return self.now


SLOT_IDS = tuple(f"L{index:02d}" for index in range(1, 25))


class Frame:
    def __init__(self, label):
        self.label = str(label)


def click_safe_ledger(frame, empty_slots=("L01",)):
    empty_slots = tuple(empty_slots)
    empty_set = set(empty_slots)
    return {
        "capture_status": "aligned",
        "capture_reason": "fixture-aligned",
        "unknown_count": 0,
        "ui_blocked": False,
        "frame_id": frame.label,
        "captured_at": 1.0,
        "slot_centers": {
            slot_id: (100 + index, 300 + index)
            for index, slot_id in enumerate(SLOT_IDS, start=1)
        },
        "slots": {
            slot_id: {
                "state": "empty" if slot_id in empty_set else "occupied-1x1",
            }
            for slot_id in SLOT_IDS
        },
        "empty_slots": empty_slots,
        "empty_count": len(empty_slots),
        "occupied_count": 24 - len(empty_slots),
    }


class FixedSlotDeadlineBridgeTests(unittest.TestCase):
    def test_active_fixed_slot_chain_uses_its_absolute_deadline_without_second_native_action(self):
        """The v380 chain deadline must override the obsolete 60-second round reset."""
        namespace = load_functions("_wrap_planting_outcome_verify_func")
        clock = FakeClock(119.9)
        calls = []
        commits = []
        lands = [{"slot_id": "L01", "center": (185, 454)}]
        pending = [
            {"slot_id": "L01", "center": (185, 454)},
            {"slot_id": "L02", "center": (214, 469)},
        ]
        bot = types.SimpleNamespace(
            _qqfarm_backpack_profile_active=True,
            _qqfarm_backpack_round_started_ts=0.0,
            _qqfarm_backpack_round_deadline_ts=0.0,
            _qqfarm_backpack_round_action_attempts=0,
            _qqfarm_backpack_round_no_progress_attempts=0,
            _qqfarm_fixed_slot_chain_active=True,
            _qqfarm_fixed_slot_chain_started_ts=0.0,
            _qqfarm_fixed_slot_chain_deadline_ts=120.0,
            _qqfarm_fixed_slot_pending_slot_ids=("L01", "L02"),
            _qqfarm_fixed_slot_pending_lands=list(pending),
            _qqfarm_recent_empty_lands=list(pending),
            _qqfarm_recent_empty_land_count=2,
            _qqfarm_recent_empty_land_centers=[item["center"] for item in pending],
            _qqfarm_recent_empty_land_ts=clock.now,
            _qqfarm_empty_land_board_gate_state="confirmed",
            planting_visual_verify_delay_seconds=0.0,
        )

        def native_execute(owner, target_lands):
            self.assertIs(bot, owner)
            calls.append(tuple(item["slot_id"] for item in target_lands))
            return True

        def capture(_frame, *, frame_id, captured_at):
            return {
                "capture_status": "aligned",
                "unknown_count": 0,
                "ui_blocked": False,
                "frame_id": frame_id,
                "captured_at": captured_at,
            }

        def resolve(_ledger, _lands, *, planting_mode):
            self.assertEqual("1x1", planting_mode)
            return {"resolved": True, "attempted_slots": ("L01",)}

        def commit(_bot, _before, _after, *, attempted_slots, planting_mode, **_kwargs):
            commits.append((tuple(attempted_slots), planting_mode))
            return {
                "committed": True,
                "committed_slots": tuple(attempted_slots),
                "attempted_slots": tuple(attempted_slots),
                "planting_mode": planting_mode,
                "before_empty_count": 2,
                "after_empty_count": 1,
            }

        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_get_frame_from_bot": lambda _bot: object(),
            "_qqfarm_capture_current_frame_24_slot_ledger": capture,
            "_qqfarm_resolve_attempted_slot_ids": resolve,
            "_qqfarm_commit_current_frame_planting_transaction": commit,
            "_qqfarm_mark_visual_planting_success": lambda *_args, **_kwargs: True,
        })
        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native_execute, "fixture.fixed-slot-deadline-bridge",
        )

        with patch("time.time", clock.time):
            first = wrapped(bot, list(lands))
            self.assertFalse(
                hasattr(bot, "_qqfarm_planting_outcome_verify_active"),
                "a committed transaction must release its reentrancy guard",
            )
            clock.now = 120.0
            second = wrapped(bot, list(lands))

        self.assertTrue(changed)
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual([("L01",)], calls)
        self.assertEqual([(("L01",), "1x1")], commits)
        self.assertEqual(120.0, bot._qqfarm_backpack_round_deadline_ts)
        self.assertEqual(("L01", "L02"), bot._qqfarm_fixed_slot_pending_slot_ids)
        self.assertEqual(["L01", "L02"], [
            item["slot_id"] for item in bot._qqfarm_fixed_slot_pending_lands
        ])


    def test_expired_chain_restarts_only_on_later_fresh_click_safe_ledger(self):
        """An expired 120-second chain retains Lxx, then a later fresh board may rearm it.

        The expiry invocation itself must not extend the deadline.  On the next
        invocation, a newly captured complete ledger is a separate bounded
        transaction and may resume the exact pending Lxx once.
        """
        namespace = load_functions(
            "_qqfarm_run_strict_24slot_harvest_then_replant_transaction"
        )
        clock = FakeClock(120.0)
        first = Frame("deadline-expiry")
        second = Frame("fresh-complete-board")
        post_harvest = Frame("fresh-after-harvest")
        observed = {
            first: click_safe_ledger(first),
            second: click_safe_ledger(second),
            post_harvest: click_safe_ledger(post_harvest),
        }
        native_calls = []
        context = types.SimpleNamespace(
            _qqfarm_fixed_slot_chain_active=True,
            _qqfarm_fixed_slot_chain_expired=False,
            _qqfarm_fixed_slot_chain_started_ts=0.0,
            _qqfarm_fixed_slot_chain_deadline_ts=120.0,
            _qqfarm_fixed_slot_pending_slot_ids=("L01",),
            _qqfarm_fixed_slot_pending_lands=[
                {"slot_id": "L01", "center": (101, 301)}
            ],
        )

        def native_self(owner, frame):
            self.assertIs(context, owner)
            native_calls.append(frame.label)
            return {"success": False, "action": "none"}

        def observe(frame, *, frame_id, captured_at):
            del frame_id, captured_at
            return observed[frame]

        context.process_self_farm = native_self
        namespace.update({
            "time": clock,
            "_write": lambda *_args, **_kwargs: None,
            "_get_frame_from_bot": lambda _owner: post_harvest,
            "_invoke_friend_guard_action": (
                lambda action, _identity, args, kwargs: action(*args, **kwargs)
            ),
            "_qqfarm_capture_current_frame_24_slot_ledger": observe,
            "_qqfarm_open_seed_panel_for_backpack_preflight": (
                lambda *_args, **_kwargs: (
                    False, None, "fixture-panel-held"
                )
            ),
        })

        expired_result = namespace[
            "_qqfarm_run_strict_24slot_harvest_then_replant_transaction"
        ](context, initial_frame=first)
        self.assertFalse(expired_result)
        self.assertEqual([], native_calls)
        self.assertTrue(context._qqfarm_fixed_slot_chain_expired)
        self.assertEqual(120.0, context._qqfarm_fixed_slot_chain_deadline_ts)

        clock.now = 121.0
        resumed_result = namespace[
            "_qqfarm_run_strict_24slot_harvest_then_replant_transaction"
        ](context, initial_frame=second)

        self.assertFalse(resumed_result)
        self.assertEqual(["fresh-complete-board"], native_calls)
        self.assertTrue(context._qqfarm_fixed_slot_chain_active)
        self.assertFalse(context._qqfarm_fixed_slot_chain_expired)
        self.assertEqual(121.0, context._qqfarm_fixed_slot_chain_started_ts)
        self.assertEqual(241.0, context._qqfarm_fixed_slot_chain_deadline_ts)
        self.assertEqual(("L01",), context._qqfarm_fixed_slot_pending_slot_ids)


if __name__ == "__main__":
    unittest.main()
