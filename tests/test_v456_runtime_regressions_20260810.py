import ast
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'


def load(*names):
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in set(names)]
    mod = ast.Module(body=nodes, type_ignores=[]); ast.fix_missing_locations(mod)
    ns = {'_write': lambda *a, **k: None, '_throttled_write': lambda *a, **k: None}
    exec(compile(mod, str(HOOK), 'exec'), ns)
    return ns


class V456Regressions(unittest.TestCase):
    def test_daily_callable_cycle_unwraps_to_native_leaf(self):
        ns = load('_qqfarm_unwrap_daily_callable', '_native_v225_call_daily')
        events = []
        def native(ctx): events.append('native'); return True
        def wrap_a(ctx): return wrap_b(ctx)
        def wrap_b(ctx): return wrap_a(ctx)
        wrap_a.__qqfarm_daily_flow_status_orig__ = wrap_b
        wrap_b.__qqfarm_share_entry_settle_orig__ = native
        self.assertTrue(ns['_native_v225_call_daily'](wrap_a, object()))
        self.assertEqual(['native'], events)

    def test_unresolved_quad_overlay_retries_ordinary_seed_same_round(self):
        ns = load('_wrap_backpack_seed_priority_planting_fast')
        calls = []
        def native(bot):
            calls.append(bool(getattr(bot, 'enable_quad_act_seeds', True)))
            if len(calls) == 1:
                bot._qqfarm_quad_overlay_block_fallback = True
                return False
            bot._qqfarm_recent_empty_land_count = 2
            return True
        bot = types.SimpleNamespace(
            enable_quad_act_seeds=True,
            quad_act_seeds=True,
            _qqfarm_recent_empty_land_count=3,
        )
        wrapped, changed = ns['_wrap_backpack_seed_priority_planting_fast'](native, 'fixture')
        self.assertTrue(changed)
        wrapped(bot)
        self.assertEqual([True, False], calls)
        self.assertTrue(bot._qqfarm_post_harvest_pending)
        self.assertFalse(getattr(bot, '_qqfarm_quad_overlay_block_fallback', False))

    def test_prompt_not_found_share_is_soft_block_only_until_backoff(self):
        ns = load('_daily_flow_retry_blocked')
        ns['_daily_business_date'] = lambda: '2026-08-11'
        ns['_daily_flow_status_paths'] = lambda paths=None: ['state']
        ns['_daily_flow_read_status'] = lambda path: {
            'date': '2026-08-11',
            'flows': {'share': {
                'status': 'failed', 'attempts': 3,
                'reason': 'share-recovery: prompt-not-found',
                'next_retry_at': 100.0,
            }},
        }
        ns['_daily_retry_max_default'] = lambda: 3
        self.assertTrue(ns['_daily_flow_retry_blocked']('share', now_epoch=99.0))
        self.assertFalse(ns['_daily_flow_retry_blocked']('share', now_epoch=101.0))


    def test_same_day_freebenefits_dispatch_does_not_reenter_native_runner(self):
        ns = load('_run_native_v225_daily_catchup')
        ns['_native_v225_daily_home_ready'] = lambda context: True
        ns['_daily_flow_success_today'] = lambda flow, **kwargs: False
        ns['_daily_flow_attempted_today'] = lambda context, flow: False
        ns['_daily_flow_entry_red_dot_state'] = lambda context, flow: None
        ns['_daily_business_date'] = lambda: '2026-08-11'
        ns['_native_v225_daily_flow_due'] = lambda context, flow: True
        calls = []
        ns['_native_v225_daily_flow_module'] = lambda: types.SimpleNamespace(
            run_daily_freebenefits=lambda context: calls.append('run')
        )
        context = types.SimpleNamespace(
            _qqfarm_native_v225_daily_dispatch_day_freebenefits='2026-08-11'
        )
        self.assertEqual(
            '',
            ns['_run_native_v225_daily_catchup'](context),
        )
        self.assertEqual([], calls)



if __name__ == '__main__': unittest.main()
