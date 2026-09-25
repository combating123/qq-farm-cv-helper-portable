import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'


def load_functions(*names):
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted.difference(node.name for node in nodes)
    if missing:
        raise AssertionError('missing hook functions: ' + repr(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace


class V549RuntimeActionAndEmptyGateTests(unittest.TestCase):
    def test_unconfirmed_candidates_are_observation_only(self):
        namespace = load_functions(
            '_qqfarm_unconfirmed_empty_candidates_are_actionable',
        )
        gate = namespace['_qqfarm_unconfirmed_empty_candidates_are_actionable']
        bot = types.SimpleNamespace(
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_empty_land_board_gate_ts=100.0,
        )
        self.assertFalse(gate(bot, 'unknown', 1, now_ts=110.0))
        self.assertFalse(gate(bot, 'bypass', 1, now_ts=110.0))
        self.assertFalse(gate(bot, 'confirmed', 1, now_ts=150.1))
        self.assertTrue(gate(bot, 'confirmed', 1, now_ts=110.0))

    def test_repeated_self_action_is_deferred_only_for_same_frame(self):
        namespace = load_functions(
            '_qqfarm_self_action_should_defer',
            '_qqfarm_record_self_action_frame',
        )
        bot = types.SimpleNamespace(
            self_action_confirmation_cooldown_seconds=18.0,
            _qqfarm_home_empty_land_pending=False,
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_post_harvest_pending=False,
            _qqfarm_single_harvest_planting_pending=False,
        )
        record = namespace['_qqfarm_record_self_action_frame']
        defer = namespace['_qqfarm_self_action_should_defer']
        self.assertTrue(record(bot, ('same', 1), now_ts=100.0))
        self.assertTrue(defer(bot, ('same', 1), now_ts=110.0))
        self.assertFalse(defer(bot, ('new', 2), now_ts=110.0))
        self.assertFalse(defer(bot, ('same', 1), now_ts=119.0))

    def test_pending_home_work_allows_same_frame_retry(self):
        namespace = load_functions(
            '_qqfarm_self_action_should_defer',
            '_qqfarm_record_self_action_frame',
        )
        bot = types.SimpleNamespace(
            self_action_confirmation_cooldown_seconds=18.0,
            _qqfarm_home_empty_land_pending=True,
            _qqfarm_home_visual_recheck_required=True,
        )
        namespace['_qqfarm_record_self_action_frame'](bot, ('same', 1), now_ts=100.0)
        self.assertFalse(
            namespace['_qqfarm_self_action_should_defer'](
                bot, ('same', 1), now_ts=110.0
            )
        )


if __name__ == '__main__':
    unittest.main()
