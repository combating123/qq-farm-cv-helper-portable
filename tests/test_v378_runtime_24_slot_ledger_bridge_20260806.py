import ast
import types
import unittest
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


def slot_states(*, occupied=(), unknown=()):
    occupied_set = set(occupied)
    unknown_set = set(unknown)
    return {
        slot_id: {
            "state": (
                "unknown" if slot_id in unknown_set else
                "occupied-1x1" if slot_id in occupied_set else
                "empty"
            )
        }
        for slot_id in SLOT_IDS
    }


def ledger(build, *, frame_id, states, captured_at, signature="fixture-camera"):
    return build(
        states,
        frame_id=frame_id,
        board_signature=signature,
        captured_at=captured_at,
    )


class V378Runtime24SlotLedgerBridgeTests(unittest.TestCase):
    def _namespace(self):
        return load_functions(
            "_qqfarm_build_24_plot_ledger",
            "_qqfarm_validate_24_plot_transaction",
            "_qqfarm_capture_current_frame_24_slot_ledger",
            "_qqfarm_resolve_attempted_slot_ids",
            "_qqfarm_commit_current_frame_planting_transaction",
            "_wrap_planting_outcome_verify_func",
        )

    def _install_runtime_stubs(self, namespace, ledgers, metric_calls):
        queue = list(ledgers)
        # The bridge must obtain a new capture both before and after the native
        # action.  Provide distinct frames instead of allowing it to fall back
        # to the action's stale bound frame.
        fresh_frames = [
            np.zeros((800, 428, 3), dtype=np.uint8),
            np.full((800, 428, 3), 1, dtype=np.uint8),
        ]
        namespace.update({
            "_write": lambda *_args, **_kwargs: None,
            "_qqfarm_backpack_nonseed_popup": lambda _frame: None,
            "_qqfarm_update_home_priority": lambda *_args, **_kwargs: None,
            "_qqfarm_mark_visual_planting_success": (
                lambda context, before, after, **kwargs: (
                    metric_calls.append((before, after, kwargs)), True
                )[1]
            ),
            "_qqfarm_capture_current_frame_24_slot_ledger": (
                lambda *_args, **_kwargs: queue.pop(0)
            ),
            "_get_frame_from_bot": (
                lambda *_args, **_kwargs: fresh_frames.pop(0) if fresh_frames else None
            ),
            "_qqfarm_resolve_attempted_slot_ids": (
                lambda *_args, **_kwargs: {
                    "resolved": True,
                    "reason": "resolved",
                    "attempted_slots": ("L13",),
                    "planting_mode": "1x1",
                }
            ),
        })

    def _run_wrapped_action(self, namespace, bot, native_calls):
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        lands = [{"center": (201, 481)}]

        def native(owner, seed_payload, game_frame, remain_lands, crop_name):
            native_calls.append((owner, list(remain_lands), crop_name))
            # Reproduce the legacy false success signal.  No test is allowed to
            # use this aggregate transition as planting proof.
            owner._qqfarm_recent_empty_land_count = 7
            owner._qqfarm_recent_empty_land_ts = 101.0
            owner._qqfarm_single_harvest_planting_pending = False
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )
        self.assertTrue(changed)
        return wrapped(bot, {}, frame, lands, "REAL_1X1_SEED")

    def test_exact_single_slot_transition_commits_once_and_uses_ledger_counts(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        before = ledger(
            build,
            frame_id="before-1",
            states=slot_states(),
            captured_at=100.0,
        )
        after = ledger(
            build,
            frame_id="after-1",
            states=slot_states(occupied=("L13",)),
            captured_at=101.0,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_single_harvest_planting_pending=True,
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [before, after], metric_calls)

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertTrue(result)
        self.assertEqual(1, len(native_calls))
        self.assertEqual(1, len(metric_calls))
        self.assertEqual(24, metric_calls[0][0])
        self.assertEqual(23, metric_calls[0][1])
        transaction = bot._qqfarm_last_planting_transaction
        self.assertTrue(transaction["committed"])
        self.assertEqual(1, transaction["delta"])
        self.assertEqual(("L13",), transaction["committed_slots"])

    def test_missing_fresh_before_capture_blocks_before_native_click(self):
        """A bound action frame is stale evidence and cannot authorize a land click."""
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        before = ledger(
            build,
            frame_id="stale-action-frame",
            states=slot_states(),
            captured_at=100.0,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [before], metric_calls)
        namespace["_get_frame_from_bot"] = lambda *_args, **_kwargs: None

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual(
            "fresh-before-frame-unavailable",
            bot._qqfarm_last_planting_transaction["reason"],
        )

    def test_missing_fresh_after_capture_never_commits_from_the_bound_action_frame(self):
        """The post-click ledger also requires a new capture, not the input frame."""
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        before = ledger(
            build,
            frame_id="before-fresh-only",
            states=slot_states(),
            captured_at=100.0,
        )
        after = ledger(
            build,
            frame_id="stale-input-must-not-count",
            states=slot_states(occupied=("L13",)),
            captured_at=101.0,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_single_harvest_planting_pending=True,
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [before, after], metric_calls)
        one_fresh_frame = [np.zeros((800, 428, 3), dtype=np.uint8)]
        namespace["_get_frame_from_bot"] = (
            lambda *_args, **_kwargs: one_fresh_frame.pop(0) if one_fresh_frame else None
        )

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual(1, len(native_calls))
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual(
            "fresh-after-frame-unavailable",
            bot._qqfarm_last_planting_transaction["reason"],
        )
        self.assertTrue(bot._qqfarm_single_harvest_planting_pending)

    def test_complete_physical_two_by_two_commits_through_the_runtime_bridge(self):
        """A real nonsequential 2x2 group remains one four-slot runtime transaction."""
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        quad = ("L08", "L13", "L12", "L17")
        before = ledger(
            build,
            frame_id="before-quad",
            states=slot_states(),
            captured_at=100.0,
        )
        after_states = slot_states()
        for slot_id in quad:
            after_states[slot_id]["state"] = "occupied-2x2"
        after = ledger(
            build,
            frame_id="after-quad",
            states=after_states,
            captured_at=101.0,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [before, after], metric_calls)
        resolved_modes = []
        namespace["_qqfarm_candidate_is_quad_seed"] = (
            lambda candidate, **_kwargs: bool((candidate or {}).get("is_quad"))
        )
        namespace["_qqfarm_resolve_attempted_slot_ids"] = (
            lambda _ledger, _lands, *, planting_mode="": (
                resolved_modes.append(planting_mode), {
                    "resolved": True,
                    "reason": "resolved",
                    "attempted_slots": quad,
                    "planting_mode": planting_mode,
                }
            )[1]
        )
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        lands = [{"center": (200 + index, 480 + index)} for index in range(4)]

        def native(owner, seed_payload, game_frame, remain_lands, crop_name):
            native_calls.append((owner, seed_payload, list(remain_lands), crop_name))
            return True

        wrapped, changed = namespace["_wrap_planting_outcome_verify_func"](
            native, "fixture._execute_planting_by_mode"
        )
        self.assertTrue(changed)
        result = wrapped(
            bot,
            {"center": (90, 700), "is_quad": True},
            frame,
            lands,
            "STAR_2X2_SEED",
        )

        self.assertTrue(result)
        self.assertEqual(1, len(native_calls))
        self.assertEqual(["2x2"], resolved_modes)
        self.assertEqual(1, len(metric_calls))
        self.assertEqual(24, metric_calls[0][0])
        self.assertEqual(20, metric_calls[0][1])
        transaction = bot._qqfarm_last_planting_transaction
        self.assertTrue(transaction["committed"])
        self.assertEqual("2x2", transaction["planting_mode"])
        self.assertEqual(quad, transaction["committed_slots"])

    def test_legacy_twelve_to_seven_without_slot_change_does_not_commit_or_consume_pending(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        before = ledger(
            build,
            frame_id="before-unchanged",
            states=slot_states(),
            captured_at=100.0,
        )
        after = ledger(
            build,
            frame_id="after-unchanged",
            states=slot_states(),
            captured_at=101.0,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
            _qqfarm_single_harvest_planting_pending=True,
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [before, after], metric_calls)

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual(1, len(native_calls))
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual("attempted-slots-unchanged", bot._qqfarm_last_planting_transaction["reason"])
        self.assertTrue(bot._qqfarm_single_harvest_planting_pending)

    def test_visible_seed_panel_blocks_before_native_click(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        blocked = build(
            slot_states(),
            frame_id="panel-visible",
            board_signature="fixture-camera",
            captured_at=100.0,
            seed_panel_visible=True,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [blocked], metric_calls)

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual("ui-overlay-visible", bot._qqfarm_last_planting_transaction["reason"])

    def test_visible_land_name_popup_blocks_before_native_click(self):
        """The gold/purple land-name overlay is click-blocking even without a seed shelf."""
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        blocked = build(
            slot_states(),
            frame_id="land-name-popup",
            board_signature="fixture-camera",
            captured_at=100.0,
            land_popup_visible=True,
        )
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [blocked], metric_calls)

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual("ui-overlay-visible", bot._qqfarm_last_planting_transaction["reason"])

    def test_unknown_or_cropped_viewport_blocks_before_native_click(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        unknown = ledger(
            build,
            frame_id="cropped",
            states=slot_states(unknown=("L01",)),
            captured_at=100.0,
        )
        unknown["capture_status"] = "unknown"
        unknown["capture_reason"] = "viewport-not-full-board"
        bot = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=12,
            _qqfarm_recent_empty_land_ts=100.0,
            _qqfarm_empty_land_board_gate_state="confirmed",
        )
        native_calls = []
        metric_calls = []
        self._install_runtime_stubs(namespace, [unknown], metric_calls)

        result = self._run_wrapped_action(namespace, bot, native_calls)

        self.assertFalse(result)
        self.assertEqual([], native_calls)
        self.assertEqual([], metric_calls)
        self.assertFalse(bot._qqfarm_last_planting_transaction["committed"])
        self.assertEqual("viewport-not-full-board", bot._qqfarm_last_planting_transaction["reason"])

    def test_resolver_maps_one_current_empty_land_to_one_fixed_slot(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        current = ledger(
            build,
            frame_id="current",
            states=slot_states(),
            captured_at=100.0,
        )
        current["slot_centers"] = {
            slot_id: (index * 10, index * 10)
            for index, slot_id in enumerate(SLOT_IDS, start=1)
        }

        resolved = namespace["_qqfarm_resolve_attempted_slot_ids"](
            current,
            [{"center": current["slot_centers"]["L13"]}],
            planting_mode="1x1",
        )

        self.assertTrue(resolved["resolved"])
        self.assertEqual(("L13",), resolved["attempted_slots"])
        self.assertEqual("1x1", resolved["planting_mode"])


    def test_resolver_accepts_only_a_complete_physical_nonsequential_quad(self):
        namespace = self._namespace()
        build = namespace["_qqfarm_build_24_plot_ledger"]
        current = ledger(
            build,
            frame_id="current-quad",
            states=slot_states(),
            captured_at=100.0,
        )
        current["slot_centers"] = {
            slot_id: (index * 10, index * 10)
            for index, slot_id in enumerate(SLOT_IDS, start=1)
        }
        quad = ("L08", "L13", "L12", "L17")

        resolved = namespace["_qqfarm_resolve_attempted_slot_ids"](
            current,
            [{"center": current["slot_centers"][slot_id]} for slot_id in quad],
            planting_mode="2x2",
        )

        self.assertTrue(resolved["resolved"])
        self.assertEqual(quad, resolved["attempted_slots"])
        self.assertEqual("2x2", resolved["planting_mode"])


if __name__ == "__main__":
    unittest.main()
