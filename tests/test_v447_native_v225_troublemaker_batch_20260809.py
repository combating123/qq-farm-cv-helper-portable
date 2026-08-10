import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    assignments = {
        "_VIP_CONTEXT_BOOL_ATTRS",
        "_VIP_CONTEXT_GATE_NAMES",
        "_VIP_CONTEXT_FALSE_GATE_NAMES",
        "_VIP_CONTEXT_TRUE_METHOD_ATTRS",
        "_VIP_CONTEXT_CHILD_NAMES",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in assignments
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__name__": "v447_native_v225_troublemaker_batch"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class NativeV225TroublemakerBatch20260809Tests(unittest.TestCase):
    def test_narrow_entry_runs_native_batch_under_temporary_vip_context(self):
        namespace = load_functions(
            "_enter_vip_entitlement_context",
            "_restore_vip_entitlement_context",
            "_wrap_first_party_friend_troublemaker_entry",
        )
        native_globals = {}
        exec(
            "def _qf_aa860ac25206(feature_key):\n"
            "    return True\n"
            "def native_troublemaker(bot, frame):\n"
            "    bot.calls.append((\n"
            "        'native-batch',\n"
            "        bot._qf_3dc9b7de9bd9('daily_troublemaker', 'friend_farm'),\n"
            "        _qf_aa860ac25206('daily_troublemaker'),\n"
            "        frame,\n"
            "    ))\n"
            "    bot.user_logs.append('??????????? 6 ?????? 6')\n"
            "    return 6\n",
            native_globals,
        )
        original_security_gate = native_globals["_qf_aa860ac25206"]
        first_party_calls = []
        namespace["_run_first_party_friend_troublemaker"] = (
            lambda *args, **kwargs: first_party_calls.append((args, kwargs)) or True
        )
        namespace["_write"] = lambda *args, **kwargs: None

        wrapped, changed = namespace["_wrap_first_party_friend_troublemaker_entry"](
            native_globals["native_troublemaker"],
            "bot.fixture._run_friend_daily_troublemaker",
        )

        class Bot:
            def __init__(self):
                self.calls = []
                self.user_logs = []

            def _qf_3dc9b7de9bd9(self, feature_key, context=""):
                return False

        bot = Bot()
        frame = types.SimpleNamespace(shape=(800, 428, 3))
        result = wrapped(bot, frame)

        self.assertTrue(changed)
        self.assertEqual(6, result)
        self.assertEqual([("native-batch", True, False, frame)], bot.calls)
        self.assertEqual(
            ["??????????? 6 ?????? 6"],
            bot.user_logs,
        )
        self.assertEqual([], first_party_calls)
        self.assertFalse(
            bot._qf_3dc9b7de9bd9("daily_troublemaker", "friend_farm")
        )
        self.assertIs(
            original_security_gate,
            native_globals["_qf_aa860ac25206"],
        )
        self.assertTrue(
            native_globals["_qf_aa860ac25206"]("daily_troublemaker")
        )

    def test_native_batch_count_is_mirrored_without_a_second_increment(self):
        namespace = load_functions(
            "_enter_vip_entitlement_context",
            "_restore_vip_entitlement_context",
            "_wrap_first_party_friend_troublemaker_entry",
        )
        syncs = []

        def native_troublemaker(bot, frame):
            bot.friend_trouble_daily_date = "2026-08-09"
            bot.friend_trouble_daily_count = 8
            return True

        class Bot:
            friend_trouble_daily_date = "2026-08-09"
            friend_trouble_daily_count = 2

        namespace.update({
            "_friend_guard_context": lambda args, kwargs: args[0],
            "_friend_trouble_counter_snapshot": (
                lambda context: context.friend_trouble_daily_count
            ),
            "_daily_business_date": lambda: "2026-08-09",
            "_daily_metrics_sync_runtime": (
                lambda context, **kwargs: syncs.append((context, kwargs)) or {
                    "friend_trouble_daily_count": context.friend_trouble_daily_count
                }
            ),
            "_write": lambda *_args, **_kwargs: None,
        })
        wrapped, changed = namespace["_wrap_first_party_friend_troublemaker_entry"](
            native_troublemaker,
            "bot.fixture._run_friend_daily_troublemaker",
        )
        bot = Bot()

        self.assertTrue(changed)
        self.assertTrue(wrapped(bot, object()))
        self.assertEqual(8, bot.friend_trouble_daily_count)
        self.assertEqual(1, len(syncs))
        self.assertIs(bot, syncs[0][0])
        self.assertTrue(syncs[0][1]["force"])
        self.assertEqual("2026-08-09", syncs[0][1]["today"])
        self.assertEqual(
            ("friend_trouble_daily_count",),
            syncs[0][1]["exact_context_fields"],
        )

    def test_deferred_route_prefers_native_v225_batch_over_single_land_cv_clicker(self):
        namespace = load_functions("_run_deferred_friend_troublemaker")
        calls = []
        counts = iter((2, 8))
        frame = object()

        class Scheduler:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True
            _qqfarm_friend_chain_troublemaker_ran = False
            friend_troublemaker_adjacent_retry_limit = 1
            _qqfarm_troublemaker_full_miss_until = 0.0

            def _run_friend_daily_troublemaker(self, current_frame):
                calls.append(("native-v225-batch", current_frame))
                return 6

        scheduler = Scheduler()
        namespace.update({
            "_run_first_party_friend_troublemaker": (
                lambda context, current_frame: calls.append(
                    ("single-land-cv", current_frame)
                ) or False
            ),
            "_friend_watchdog_now": lambda: 100.0,
            "_friend_trouble_counter_snapshot": lambda _context: next(counts),
            "_finalize_friend_chain_after_troublemaker": lambda _context: True,
            "_write": lambda *_args, **_kwargs: None,
        })

        self.assertEqual(6, namespace["_run_deferred_friend_troublemaker"](
            scheduler, frame
        ))
        self.assertEqual([("native-v225-batch", frame)], calls)
        self.assertTrue(scheduler._qqfarm_friend_chain_troublemaker_ran)


if __name__ == "__main__":
    unittest.main()
