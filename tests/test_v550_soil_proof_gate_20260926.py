import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'


def load_helper():
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == '_qqfarm_filter_empty_land_candidates_by_soil_proof'
    ]
    if not nodes:
        raise AssertionError('soil-proof helper is missing')
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace['_qqfarm_filter_empty_land_candidates_by_soil_proof']


class V550SoilProofGateTests(unittest.TestCase):
    def test_lattice_only_hits_are_held_but_visual_soil_hits_remain(self):
        helper = load_helper()
        visual = {
            'center': (120, 220),
            '_qqfarm_visual_soil_proof': True,
        }
        post_harvest = {
            'center': (150, 250),
            '_qqfarm_post_harvest_confirmed': True,
        }
        lattice_only = {
            'center': (180, 280),
            '_qqfarm_board_confirmed_empty_candidate': True,
        }

        proven, held = helper([lattice_only, visual, post_harvest])

        self.assertEqual([visual, post_harvest], proven)
        self.assertEqual([lattice_only], held)

    def test_non_dict_candidates_are_held_without_becoming_click_targets(self):
        helper = load_helper()
        proven, held = helper([(1, 2), {'center': (3, 4)}])
        self.assertEqual([], proven)
        self.assertEqual([(1, 2), {'center': (3, 4)}], held)

    def test_confirmed_lattice_only_hit_never_enters_slow_proof_or_ocr_path(self):
        """A board lattice is geometry evidence, not planting authority."""
        source = HOOK.read_text(encoding='utf-8-sig')
        tree = ast.parse(source, filename=str(HOOK))
        wanted = {
            '_qqfarm_frame_is_usable_for_empty_land_detection',
            '_qqfarm_empty_land_board_gate',
            '_qqfarm_home_priority_active',
            '_qqfarm_update_home_priority',
            '_empty_land_candidate_has_crop_cover',
            '_empty_land_candidate_crop_cover_evidence',
            '_qqfarm_visual_empty_land_marker_candidates',
            '_qqfarm_dedupe_empty_land_candidates',
            '_qqfarm_filter_empty_land_candidates_by_soil_proof',
            '_wrap_detect_empty_lands_state',
        }
        nodes = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        self.assertEqual(wanted, {node.name for node in nodes})
        module = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(module)
        namespace = {}
        exec(compile(module, str(HOOK), 'exec'), namespace)

        logs = []
        slow_path_calls = []
        lattice_only = {
            'center': (210, 470),
            '_qqfarm_board_confirmed_empty_candidate': True,
        }

        namespace.update({
            '_write': lambda message: logs.append(str(message)),
            '_qqfarm_frame_is_usable_for_empty_land_detection': (
                lambda _frame: True
            ),
            '_qqfarm_visual_empty_land_marker_candidates': (
                lambda _frame: []
            ),
            '_empty_land_candidate_has_crop_cover': (
                lambda _frame, _center: False
            ),
            '_empty_land_candidate_crop_cover_evidence': (
                lambda _frame, _center: 'none'
            ),
            '_qqfarm_empty_land_board_gate': (
                lambda _frame, _candidates: {
                    'state': 'confirmed',
                    'lands': [lattice_only],
                    'rejected_centers': [],
                    'anchor_count': 24,
                }
            ),
            '_qqfarm_attach_live_flat_empty_land_proof': (
                lambda *_args, **_kwargs: slow_path_calls.append('flat-proof')
                or [lattice_only]
            ),
            '_qqfarm_dedupe_empty_land_candidates': (
                lambda items: (list(items), [], list(items))
            ),
            '_qqfarm_update_home_priority': lambda *_args, **_kwargs: None,
        })
        bot = types.SimpleNamespace(
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_empty_land_remaining=1,
            _qqfarm_recent_empty_land_count=1,
            _qqfarm_recent_empty_lands=[lattice_only],
            _qqfarm_stable_empty_land_count=1,
            _qqfarm_stable_empty_lands=[lattice_only],
        )

        def native(_owner, _frame=None):
            return [dict(lattice_only)]

        wrapped, changed = namespace['_wrap_detect_empty_lands_state'](
            native, 'fixture.v550-lattice-only'
        )
        result = wrapped(bot, object())

        self.assertTrue(changed)
        self.assertEqual([], result)
        self.assertEqual([], slow_path_calls)
        self.assertEqual(0, bot._qqfarm_recent_empty_land_count)
        self.assertEqual('unknown', bot._qqfarm_empty_land_board_gate_state)
        self.assertTrue(bot._qqfarm_home_visual_recheck_required)
        self.assertTrue(any('v550 empty-land soil-proof gate' in line for line in logs))


if __name__ == '__main__':
    unittest.main()
