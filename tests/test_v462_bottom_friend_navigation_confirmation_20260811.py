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
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace


class V462BottomFriendNavigationConfirmationTests(unittest.TestCase):
    def test_same_friend_page_is_not_clicked_again_before_navigation_is_confirmed(self):
        namespace = load_functions('_wrap_friend_next_entry_func')
        wrapper_factory = namespace['_wrap_friend_next_entry_func']
        frame = types.SimpleNamespace(shape=(800, 428, 3), identity='friend-A')
        scheduler = types.SimpleNamespace(_qqfarm_friend_chain_pending=True)
        navigation_calls = []

        wrapper_factory.__globals__.update({
            '_friend_guard_context': lambda args, kwargs: scheduler,
            '_get_frame_from_bot': lambda owner: frame,
            '_friend_guard_friend_ui_state': lambda candidate: True,
            '_qqfarm_friend_navigation_identity': lambda candidate: candidate.identity,
            '_qqfarm_friend_navigation_identity_changed': (
                lambda before, candidate: before != candidate.identity
            ),
            '_invoke_friend_adjacent_card_navigation': (
                lambda owner, candidate: navigation_calls.append(candidate.identity)
                or (True, 'visual.adjacent-friend-card')
            ),
            '_write': lambda message: None,
        })

        wrapped, _ = wrapper_factory(
            lambda owner, game_frame: False,
            'FarmBotCV.check_friend_farm_bottom_help_all_entry',
        )

        self.assertTrue(wrapped(scheduler, frame))
        self.assertFalse(wrapped(scheduler, frame))
        self.assertEqual(['friend-A'], navigation_calls)

    def test_changed_friend_page_allows_the_next_adjacent_navigation(self):
        namespace = load_functions('_wrap_friend_next_entry_func')
        wrapper_factory = namespace['_wrap_friend_next_entry_func']
        frame_a = types.SimpleNamespace(shape=(800, 428, 3), identity='friend-A')
        frame_b = types.SimpleNamespace(shape=(800, 428, 3), identity='friend-B')
        scheduler = types.SimpleNamespace(_qqfarm_friend_chain_pending=True)
        navigation_calls = []

        wrapper_factory.__globals__.update({
            '_friend_guard_context': lambda args, kwargs: scheduler,
            '_get_frame_from_bot': lambda owner: frame_b,
            '_friend_guard_friend_ui_state': lambda candidate: True,
            '_qqfarm_friend_navigation_identity': lambda candidate: candidate.identity,
            '_qqfarm_friend_navigation_identity_changed': (
                lambda before, candidate: before != candidate.identity
            ),
            '_invoke_friend_adjacent_card_navigation': (
                lambda owner, candidate: navigation_calls.append(candidate.identity)
                or (True, 'visual.adjacent-friend-card')
            ),
            '_write': lambda message: None,
        })

        wrapped, _ = wrapper_factory(
            lambda owner, game_frame: False,
            'FarmBotCV.check_friend_farm_bottom_help_all_entry',
        )

        self.assertTrue(wrapped(scheduler, frame_a))
        self.assertTrue(wrapped(scheduler, frame_b))
        self.assertEqual(['friend-A', 'friend-B'], navigation_calls)

    def test_new_friend_chain_clears_previous_unverified_navigation_identity(self):
        namespace = load_functions('_friend_chain_begin_dispatch')
        begin = namespace['_friend_chain_begin_dispatch']
        scheduler = types.SimpleNamespace(
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_dispatch_depth=0,
            _qqfarm_friend_next_entry_pending_identity='friend-A',
        )

        self.assertTrue(begin(scheduler))
        self.assertIsNone(scheduler._qqfarm_friend_next_entry_pending_identity)


if __name__ == '__main__':
    unittest.main()
