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
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace


class V542FriendUncertainNoActionTests(unittest.TestCase):
    def test_friend_list_or_transition_miss_is_not_confirmed_empty_friend(self):
        namespace = load_functions('_qqfarm_friend_no_action_is_unconfirmed')
        context = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_live_scene_hint='friend-list',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_dispatch_visual_unconfirmed=False,
        )
        self.assertTrue(namespace['_qqfarm_friend_no_action_is_unconfirmed'](context))

    def test_confirmed_friend_farm_can_still_finish_as_empty(self):
        namespace = load_functions('_qqfarm_friend_no_action_is_unconfirmed')
        context = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_live_scene_hint='friend',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_dispatch_visual_unconfirmed=False,
            _qqfarm_native_friend_surface_state='friend-farm',
        )
        self.assertFalse(namespace['_qqfarm_friend_no_action_is_unconfirmed'](context))

    def test_unconfirmed_log_is_rewritten_to_waiting_retry(self):
        namespace = load_functions(
            '_qqfarm_friend_no_action_is_unconfirmed',
            '_rewrite_unconfirmed_friend_no_action_log',
        )
        context = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_live_scene_hint='friend-list',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_dispatch_visual_unconfirmed=False,
        )
        message = '好友农场已无可执行的任务，下一轮巡查将回家查看是否有可执行的任务'
        rewritten = namespace['_rewrite_unconfirmed_friend_no_action_log'](
            message, context
        )
        self.assertIn('页面未完成确认', rewritten)
        self.assertIn('等待新画面后重试', rewritten)
        self.assertNotIn('回家查看', rewritten)


if __name__ == '__main__':
    unittest.main()
