import ast
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'
FIXTURE = ROOT / 'tests' / 'fixtures' / 'live-v460-friend-action-stalled-sanitized-20260811.png'


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


class V460FriendRuntimeWrapperIdempotencyTests(unittest.TestCase):
    def test_recurring_patch_does_not_stack_bridge_below_unrelated_outer_wrapper(self):
        ns = load_functions(
            '_friend_guard_original_chain',
            '_wrap_native_v225_friend_help_candidate_cache',
            '_wrap_native_v225_friend_help_confirmation',
            '_patch_native_v225_friend_help_confirmation_for_module',
        )
        ns['_qqfarm_legacy_wrapper_allowed'] = lambda _label: False
        ns['_write'] = lambda *_args: None

        class FarmBotCV:
            def process_friend_farm(self):
                return 'process'
            def _record_friend_help_action(self):
                return 'record'

        module = types.SimpleNamespace(__name__='bot.synthetic.friend_runtime', FarmBotCV=FarmBotCV)
        self.assertEqual(2, ns['_patch_native_v225_friend_help_confirmation_for_module'](module, 'first'))

        def unrelated_outer(fn):
            def wrapped(self, *args, **kwargs):
                return fn(self, *args, **kwargs)
            wrapped.__wrapped__ = fn
            return wrapped

        FarmBotCV.process_friend_farm = unrelated_outer(FarmBotCV.process_friend_farm)
        FarmBotCV._record_friend_help_action = unrelated_outer(FarmBotCV._record_friend_help_action)
        self.assertEqual(0, ns['_patch_native_v225_friend_help_confirmation_for_module'](module, 'tick'))

    def test_recurring_patch_uses_class_marker_when_outer_wrapper_is_opaque(self):
        ns = load_functions(
            '_friend_guard_original_chain',
            '_wrap_native_v225_friend_help_candidate_cache',
            '_wrap_native_v225_friend_help_confirmation',
            '_patch_native_v225_friend_help_confirmation_for_module',
        )
        ns['_qqfarm_legacy_wrapper_allowed'] = lambda _label: False
        ns['_write'] = lambda *_args: None

        class FarmBotCV:
            def process_friend_farm(self):
                return 'process'
            def _record_friend_help_action(self):
                return 'record'

        module = types.SimpleNamespace(__name__='bot.synthetic.opaque_runtime', FarmBotCV=FarmBotCV)
        self.assertEqual(2, ns['_patch_native_v225_friend_help_confirmation_for_module'](module, 'first'))

        def opaque_outer(fn):
            def wrapped(self, *args, **kwargs):
                return fn(self, *args, **kwargs)
            return wrapped

        FarmBotCV.process_friend_farm = opaque_outer(FarmBotCV.process_friend_farm)
        FarmBotCV._record_friend_help_action = opaque_outer(FarmBotCV._record_friend_help_action)
        self.assertEqual(0, ns['_patch_native_v225_friend_help_confirmation_for_module'](module, 'tick'))

    def test_reported_frame_still_has_strong_friend_action_proof(self):
        import cv2
        ns = load_functions(
            '_friend_guard_read_template', '_friend_guard_match_template',
            '_friend_guard_help_button_match', '_friend_guard_steal_button_match',
            '_friend_selected_carousel_card_bounds', '_friend_guard_friend_ui_state',
        )
        ns.update({
            '_FRIEND_GUARD_TEMPLATE_CACHE': {},
            '_FRIEND_HOME_TEMPLATE_PATH': str(ROOT/'tests'/'fixtures'/'friend_home_button.png'),
            '_FRIEND_LIST_TEMPLATE_PATH': str(ROOT/'tests'/'fixtures'/'friend_list_tabs.png'),
            '_FRIEND_HELP_ALL_TEMPLATE_PATH': str(ROOT/'portable'/'friend_help_all_button.png'),
            '_FRIEND_STEAL_ALL_TEMPLATE_PATH': str(ROOT/'portable'/'friend_steal_all_button.png'),
        })
        frame = cv2.imread(str(FIXTURE))
        self.assertIsNotNone(frame)
        self.assertIsInstance(ns['_friend_selected_carousel_card_bounds'](frame), dict)
        self.assertTrue(ns['_friend_guard_help_button_match'](frame).get('matched'))
        self.assertIs(ns['_friend_guard_friend_ui_state'](frame), True)


if __name__ == '__main__':
    unittest.main()
