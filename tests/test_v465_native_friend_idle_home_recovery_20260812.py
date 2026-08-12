import ast
import types
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'


def load_functions(*names):
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    missing = wanted - {n.name for n in nodes}
    if missing:
        raise AssertionError('missing: ' + ', '.join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {'_write': lambda *_args: None}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace


class V465NativeFriendIdleHomeRecoveryTests(unittest.TestCase):
    def test_two_completed_idle_friend_rounds_trigger_bounded_home_recovery(self):
        ns = load_functions('_qqfarm_native_friend_idle_home_recovery')
        frame = object()
        home = object()
        captures = [frame, frame, home]
        clicks = []
        bot = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_active=False,
        )
        ns.update({
            '_get_frame_from_bot': lambda _bot: captures.pop(0),
            '_friend_guard_friend_ui_state': lambda current: False if current is home else True,
            '_friend_guard_help_button_match': lambda _frame: {'matched': False},
            '_friend_guard_steal_button_match': lambda _frame: {'matched': False},
            '_invoke_friend_guard_home_coordinate_click': lambda owner, current: clicks.append((owner, current)) or True,
            '_friend_watchdog_now': lambda: 100.0,
            '_friend_guard_sleep': lambda _seconds: None,
        })

        self.assertFalse(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        self.assertTrue(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        self.assertEqual(1, len(clicks))
        self.assertEqual(0, bot._qqfarm_native_friend_idle_home_attempts)
        self.assertEqual('home', bot._qqfarm_live_scene_hint)

    def test_visible_action_or_pending_navigation_never_triggers_home(self):
        ns = load_functions('_qqfarm_native_friend_idle_home_recovery')
        frame = object()
        clicks = []
        ns.update({
            '_get_frame_from_bot': lambda _bot: frame,
            '_friend_guard_friend_ui_state': lambda _frame: True,
            '_friend_guard_help_button_match': lambda _frame: {'matched': True},
            '_friend_guard_steal_button_match': lambda _frame: {'matched': False},
            '_invoke_friend_guard_home_coordinate_click': lambda *_args: clicks.append(True) or True,
            '_friend_watchdog_now': lambda: 100.0,
        })
        bot = types.SimpleNamespace(_qqfarm_cycle_branch_hint='friend')
        for _ in range(4):
            self.assertFalse(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        bot._qqfarm_friend_entry_pending = True
        ns['_friend_guard_help_button_match'] = lambda _frame: {'matched': False}
        for _ in range(4):
            self.assertFalse(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        self.assertEqual([], clicks)

    def test_run_cycle_bridge_calls_idle_recovery_only_after_native_cycle(self):
        ns = load_functions('_wrap_native_v225_daily_catchup_run_cycle')
        events = []
        ns.update({
            '_run_native_v225_daily_catchup': lambda _bot: '',
            '_native_v225_daily_any_due': lambda _bot: False,
            '_qqfarm_native_friend_idle_home_recovery': lambda _bot: events.append('recover') or True,
        })
        def native(bot):
            events.append('native')
            return 'native-result'
        wrapped, changed = ns['_wrap_native_v225_daily_catchup_run_cycle'](native, 'bot.fixture.FarmBotCV.run_cycle')
        bot = types.SimpleNamespace(_qqfarm_live_scene_hint='friend')
        self.assertTrue(changed)
        self.assertTrue(wrapped(bot))
        self.assertEqual(['native', 'recover'], events)

    def test_night_home_match_clicks_button_body_not_template_top(self):
        ns = load_functions('_invoke_friend_guard_home_coordinate_click')
        clicks = []
        frame = np.zeros((800, 428, 3), dtype=np.uint8)
        bot = types.SimpleNamespace(_last_friend_farm_go_home_present=True)
        ns.update({
            '_friend_guard_friend_ui_state': lambda _frame: True,
            '_FRIEND_HOME_LAST_MATCH': {
                'matched': True,
                'center': (394, 595),
                'match_mode': 'night-home+selected-carousel',
            },
            '_friend_guard_post_client_click': lambda x, y, *_args: clicks.append((x, y)) or True,
        })

        self.assertTrue(ns['_invoke_friend_guard_home_coordinate_click'](bot, frame))
        self.assertEqual([(394, 624)], clicks)

    def test_delivered_home_click_requires_fresh_frame_transition_proof(self):
        ns = load_functions('_qqfarm_native_friend_idle_home_recovery')
        before = object()
        after = object()
        captures = [before, after]
        states = {id(before): True, id(after): True}
        bot = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_native_friend_idle_rounds=1,
        )
        ns.update({
            '_get_frame_from_bot': lambda _bot: captures.pop(0),
            '_friend_guard_friend_ui_state': lambda frame: states[id(frame)],
            '_friend_guard_help_button_match': lambda _frame: {'matched': False},
            '_friend_guard_steal_button_match': lambda _frame: {'matched': False},
            '_invoke_friend_guard_home_coordinate_click': lambda *_args: True,
            '_friend_guard_sleep': lambda _seconds: None,
            '_friend_watchdog_now': lambda: 100.0,
        })

        self.assertFalse(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        self.assertEqual(1, bot._qqfarm_native_friend_idle_home_attempts)

    def test_fresh_frame_leaving_friend_surface_confirms_home_transition(self):
        ns = load_functions('_qqfarm_native_friend_idle_home_recovery')
        before = object()
        after = object()
        captures = [before, after]
        states = {id(before): True, id(after): False}
        bot = types.SimpleNamespace(
            _qqfarm_cycle_branch_hint='friend',
            _qqfarm_friend_entry_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_native_friend_idle_rounds=1,
        )
        ns.update({
            '_get_frame_from_bot': lambda _bot: captures.pop(0),
            '_friend_guard_friend_ui_state': lambda frame: states[id(frame)],
            '_friend_guard_help_button_match': lambda _frame: {'matched': False},
            '_friend_guard_steal_button_match': lambda _frame: {'matched': False},
            '_invoke_friend_guard_home_coordinate_click': lambda *_args: True,
            '_friend_guard_sleep': lambda _seconds: None,
            '_friend_watchdog_now': lambda: 100.0,
        })

        self.assertTrue(ns['_qqfarm_native_friend_idle_home_recovery'](bot))
        self.assertEqual(0, bot._qqfarm_native_friend_idle_home_attempts)
        self.assertEqual(0, bot._qqfarm_native_friend_idle_rounds)
        self.assertEqual('home', bot._qqfarm_live_scene_hint)

    def test_current_night_friend_fixture_is_a_stable_friend_surface(self):
        names = {
            '_friend_guard_friend_ui_state',
            '_friend_guard_match_template',
            '_friend_guard_read_template',
            '_friend_selected_carousel_card_bounds',
            '_friend_guard_help_button_match',
            '_friend_guard_steal_button_match',
            '_friend_list_visit_button_rows',
        }
        ns = load_functions(*names)
        portable = HOOK.parent
        ns.update({
            '_FRIEND_HOME_TEMPLATE_PATH': str(portable / 'friend_home_button.png'),
            '_FRIEND_HELP_ALL_TEMPLATE_PATH': str(portable / 'friend_help_all_button.png'),
            '_FRIEND_STEAL_ALL_TEMPLATE_PATH': str(portable / 'friend_steal_all_button.png'),
            '_FRIEND_LIST_TEMPLATE_PATH': str(portable / 'friend_list_tabs.png'),
            '_FRIEND_GUARD_TEMPLATE_CACHE': {},
        })
        fixture = ROOT / 'tests' / 'fixtures' / 'live-v465-night-friend-stalled-20260812.png'
        encoded = np.fromfile(str(fixture), dtype=np.uint8)
        raw = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        self.assertEqual((1194, 672, 3), raw.shape)
        normalized = cv2.resize(raw, (428, 800), interpolation=cv2.INTER_AREA)
        self.assertIs(True, ns['_friend_guard_friend_ui_state'](normalized))
        self.assertFalse(ns['_friend_guard_help_button_match'](normalized).get('matched'))
        self.assertFalse(ns['_friend_guard_steal_button_match'](normalized).get('matched'))


if __name__ == '__main__':
    unittest.main()
