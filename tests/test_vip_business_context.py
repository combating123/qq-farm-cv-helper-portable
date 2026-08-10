import ast
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_vip_business_wrapper():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {"_diagnose_daily_troublemaker_vip_source", "_enter_vip_entitlement_context", "_restore_vip_entitlement_context", "_friend_chain_should_block_troublemaker", "_friend_chain_begin_dispatch", "_friend_chain_finish_dispatch", "_wrap_vip_business_func"}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in {
                "_VIP_CONTEXT_BOOL_ATTRS", "_VIP_CONTEXT_GATE_NAMES", "_VIP_CONTEXT_FALSE_GATE_NAMES", "_VIP_CONTEXT_TRUE_METHOD_ATTRS", "_VIP_CONTEXT_CHILD_NAMES"
            }
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "_stop_requested_in_args": lambda a, k: False,
        "_stop_gate_return": lambda name: False,
        "_force_vip_business_args": lambda a, k: 0,
        "_warehouse_recently_done": lambda: False,
        "_warehouse_retry_blocked": lambda: False,
        "_runtime_info_once": lambda *a, **k: None,
        "_throttled_write": lambda *a, **k: None,
        "_write": lambda *a, **k: None,
        "_VIP_WAREHOUSE_LAST_SEQUENCE_CLASS": "",
        "_VIP_WAREHOUSE_LAST_SEQUENCE_TS": 0.0,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_home_business_patcher():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted_functions = {
        "_friend_guard_context",
        "_friend_chain_should_block_troublemaker",
        "_friend_chain_should_block_home",
        "_wrap_friend_home_func",
        "_looks_vip_business_module",
        "_patch_vip_business_loaded",
    }
    wanted_assignments = {
        "_VIP_BUSINESS_FUNC_NAMES",
        "_FRIEND_HOME_FUNC_NAMES",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in wanted_assignments
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted_functions:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "_VIP_BUSINESS_PATCH_LOG_SEEN": set(),
        "_force_vip_business_object": lambda *args, **kwargs: 0,
        "_wrap_planting_crop_context_func": lambda fn, *args: (fn, False),
        "_wrap_radish_fertilizer_func": lambda fn, *args: (fn, False),
        "_wrap_vip_business_func": lambda fn, *args: (fn, False),
        "_qqfarm_legacy_wrapper_allowed": lambda _name: True,
        "_throttled_write": lambda *args, **kwargs: None,
        "_write": lambda *args, **kwargs: None,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_claims():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_claims")
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    import time
    namespace = {"time": time}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_claims"]()


def load_vip_module_matcher():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {"_looks_vip_business_module"}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in {
                "_VIP_BUSINESS_FUNC_NAMES", "_FRIEND_HOME_FUNC_NAMES"
            }
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class VipBusinessContextTests(unittest.TestCase):
    def test_withdrawn_v139_state_path_migration_is_not_present(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertNotIn("_VIP_LOCAL_STATE_ROOT =", source)
        private_assignments = [
            line for line in source.splitlines()
            if line.startswith((
                "_VIP_WAREHOUSE_STATE_PATH =",
                "_VIP_WAREHOUSE_RETRY_STATE_PATH =",
                "_QT_DUMP_PATH =",
            ))
        ]
        self.assertEqual(3, len(private_assignments))
    def test_claims_include_all_known_member_feature_aliases(self):
        flags = load_claims()["feature_flags"]
        expected = {
            "wechat_mouse", "wechat_focus_guard", "enable_wechat_focus_guard",
            "high_performance_mode",
            "auto_fertilize", "auto_fertilize_one", "auto_fertilize_more",
            "auto_fill_fertilizer_container", "auto_sell_fruit",
            "daily_troublemaker", "enable_daily_troublemaker",
            "quad_act_seeds", "enable_quad_act_seeds",
            "daily_radish_exp", "enable_daily_radish_exp",
            "skip_radish", "enable_skip_radish",
            "no_steal_window", "enable_no_steal_window",
            "guard_dog_help_only", "enable_guard_dog_help_only",
            "bottom_friend_list_help_all", "enable_bottom_friend_list_help_all",
            "multi_instance", "svip", "daily_svip", "enable_daily_svip",
        }
        self.assertEqual(set(), expected.difference(flags))

    def test_daily_troublemaker_observes_vip_then_restores_bot_state(self):
        ns = load_vip_business_wrapper()

        class Bot:
            is_vip = False
            vip_active = False
            entitlement_active = False

        bot = Bot()

        def run_daily_troublemaker(target):
            return target.is_vip, target.vip_active, target.entitlement_active

        wrapped, changed = ns["_wrap_vip_business_func"](
            run_daily_troublemaker,
            "bot.application.flows._run_friend_daily_troublemaker",
        )
        observed = wrapped(bot)

        self.assertTrue(changed)
        self.assertEqual((True, True, True), observed)
        self.assertEqual((False, False, False), (bot.is_vip, bot.vip_active, bot.entitlement_active))

    def test_daily_troublemaker_observes_vip_gate_then_restores_function_global(self):
        ns = load_vip_business_wrapper()
        gate_namespace = {}
        exec(
            "def _is_vip_active():\n"
            "    return False\n"
            "def run_daily_troublemaker(bot):\n"
            "    return _is_vip_active()\n",
            gate_namespace,
        )
        original_gate = gate_namespace["_is_vip_active"]
        fn = gate_namespace["run_daily_troublemaker"]

        wrapped, _ = ns["_wrap_vip_business_func"](
            fn,
            "bot.application.flows._run_friend_daily_troublemaker",
        )
        self.assertTrue(wrapped(object()))
        self.assertIs(original_gate, gate_namespace["_is_vip_active"])
        self.assertFalse(gate_namespace["_is_vip_active"]())

    def test_real_obfuscated_security_probe_is_temporarily_false(self):
        ns = load_vip_business_wrapper()
        gate_namespace = {}
        exec(
            "def _qf_aa860ac25206(feature_key):\n"
            "    return True\n"
            "def run_daily_troublemaker(bot):\n"
            "    return 'nonvip-skip' if _qf_aa860ac25206('daily_troublemaker') else 'allowed'\n",
            gate_namespace,
        )
        original_gate = gate_namespace["_qf_aa860ac25206"]
        wrapped, _ = ns["_wrap_vip_business_func"](
            gate_namespace["run_daily_troublemaker"],
            "bot._q8eacf4154f._q8a5c61_f956642277._run_friend_daily_troublemaker",
        )
        self.assertEqual("allowed", wrapped(object()))
        self.assertIs(original_gate, gate_namespace["_qf_aa860ac25206"])
        self.assertTrue(gate_namespace["_qf_aa860ac25206"]("daily_troublemaker"))

    def test_real_obfuscated_bot_entitlement_method_is_temporarily_true_and_unshadowed(self):
        ns = load_vip_business_wrapper()

        class Bot:
            def _qf_3dc9b7de9bd9(self, feature_key, context=""):
                return False

        bot = Bot()
        self.assertNotIn("_qf_3dc9b7de9bd9", bot.__dict__)

        def run_daily_troublemaker(target):
            return target._qf_3dc9b7de9bd9("daily_troublemaker", "friend_farm")

        wrapped, _ = ns["_wrap_vip_business_func"](
            run_daily_troublemaker,
            "bot._q8eacf4154f._q8a5c61_f956642277._run_friend_daily_troublemaker",
        )
        self.assertTrue(wrapped(bot))
        self.assertNotIn("_qf_3dc9b7de9bd9", bot.__dict__)
        self.assertFalse(bot._qf_3dc9b7de9bd9("daily_troublemaker", "friend_farm"))

    def test_daily_troublemaker_is_blocked_while_friend_chain_is_pending(self):
        ns = load_vip_business_wrapper()
        calls = []

        class Bot:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_exhausted = False

        wrapped, changed = ns["_wrap_vip_business_func"](
            lambda bot: calls.append(bot) or True,
            "bot.application.flows._run_friend_daily_troublemaker",
        )
        result = wrapped(Bot())

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], calls)

    def test_blocked_daily_troublemaker_caches_wrapped_callable_and_arguments(self):
        ns = load_vip_business_wrapper()
        frame = object()

        class Bot:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_exhausted = False

        bot = Bot()
        wrapped, changed = ns["_wrap_vip_business_func"](
            lambda target, candidate: True,
            "bot.application.flows._run_friend_daily_troublemaker",
        )

        self.assertTrue(changed)
        self.assertFalse(wrapped(bot, frame))
        self.assertTrue(callable(getattr(
            bot, "_qqfarm_friend_chain_deferred_troublemaker", None
        )))
        self.assertEqual(
            (bot, frame),
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_args", ()),
        )
        self.assertEqual(
            {},
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_kwargs", None),
        )

    def test_daily_troublemaker_runs_after_friend_chain_is_exhausted(self):
        ns = load_vip_business_wrapper()
        calls = []

        class Bot:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True

        bot = Bot()
        wrapped, _ = ns["_wrap_vip_business_func"](
            lambda target: calls.append(target) or "ran",
            "bot.application.flows._run_friend_daily_troublemaker",
        )

        self.assertEqual("ran", wrapped(bot))
        self.assertEqual([bot], calls)

    def test_friend_redispatch_preserves_cached_troublemaker_while_chain_pending(self):
        ns = load_vip_business_wrapper()
        cached = lambda target: True

        class Bot:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_exhausted = False

        bot = Bot()
        bot._qqfarm_friend_chain_deferred_troublemaker = cached
        bot._qqfarm_friend_chain_deferred_troublemaker_args = ("saved",)
        bot._qqfarm_friend_chain_deferred_troublemaker_kwargs = {"saved": True}
        self.assertTrue(ns["_friend_chain_begin_dispatch"](bot))

        self.assertIs(
            cached,
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker", None),
        )
        self.assertEqual(
            ("saved",),
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_args", ()),
        )
        self.assertEqual(
            {"saved": True},
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_kwargs", {}),
        )

    def test_new_friend_dispatch_preserves_cached_troublemaker_after_previous_chain(self):
        ns = load_vip_business_wrapper()
        cached = lambda target: True

        class Bot:
            _qqfarm_friend_chain_pending = False
            _qqfarm_friend_chain_exhausted = True

        bot = Bot()
        bot._qqfarm_friend_chain_deferred_troublemaker = cached
        bot._qqfarm_friend_chain_deferred_troublemaker_args = ("saved",)
        bot._qqfarm_friend_chain_deferred_troublemaker_kwargs = {"saved": True}

        self.assertTrue(ns["_friend_chain_begin_dispatch"](bot))

        self.assertIs(
            cached,
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker", None),
        )
        self.assertEqual(
            ("saved",),
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_args", ()),
        )
        self.assertEqual(
            {"saved": True},
            getattr(bot, "_qqfarm_friend_chain_deferred_troublemaker_kwargs", {}),
        )

    def test_friend_dispatch_arms_chain_before_compiled_flow_runs(self):
        ns = load_vip_business_wrapper()
        observed = []

        class Bot:
            pass

        bot = Bot()

        def process_friend_farm(target):
            observed.append((
                getattr(target, "_qqfarm_friend_chain_active", False),
                getattr(target, "_qqfarm_friend_chain_pending", False),
                getattr(target, "_qqfarm_friend_chain_exhausted", True),
            ))
            return "friend-pass"

        wrapped, _ = ns["_wrap_vip_business_func"](
            process_friend_farm,
            "bot.application.flows.process_friend_farm",
        )
        result = wrapped(bot)

        self.assertEqual("friend-pass", result)
        self.assertEqual([(True, True, False)], observed)
        self.assertFalse(getattr(bot, "_qqfarm_friend_chain_active", True))
        self.assertTrue(getattr(bot, "_qqfarm_friend_chain_pending", False))
        self.assertFalse(getattr(bot, "_qqfarm_friend_chain_exhausted", True))

    def test_obfuscated_bot_module_with_daily_troublemaker_is_patched(self):
        ns = load_vip_module_matcher()

        class ObfuscatedBotModule:
            @staticmethod
            def _run_friend_daily_troublemaker(bot):
                return False

        self.assertTrue(
            ns["_looks_vip_business_module"](
                "bot._q8eacf4154f._q8a5c61_f956642277", ObfuscatedBotModule
            )
        )


    def test_bot_module_with_native_home_method_is_selected_for_patching(self):
        ns = load_vip_module_matcher()

        class HomeFlowModule:
            @staticmethod
            def check_go_home_icon(bot, frame):
                return True

        self.assertTrue(
            ns["_looks_vip_business_module"](
                "bot.application.flows", HomeFlowModule
            )
        )


    def test_loaded_business_patcher_wraps_native_home_method(self):
        ns = load_home_business_patcher()
        calls = []

        class FriendFlow:
            _qqfarm_friend_chain_pending = True
            _qqfarm_friend_chain_active = False
            _qqfarm_friend_chain_exhausted = False

            def check_go_home_icon(self, frame):
                calls.append(frame)
                return True

        fake_module = types.SimpleNamespace(FriendFlow=FriendFlow)
        ns["sys"] = types.SimpleNamespace(
            modules={"bot.application.fake_friend_flow": fake_module}
        )

        changed = ns["_patch_vip_business_loaded"]("test")
        frame = object()
        result = FriendFlow().check_go_home_icon(frame)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertEqual([], calls)


    def test_member_aliases_are_temporarily_true_and_restored(self):
        ns = load_vip_business_wrapper()

        class Bot:
            member_active = False
            premium_active = False
            is_svip = False

        bot = Bot()
        def outer_friend_flow(target):
            return target.member_active, target.premium_active, target.is_svip

        wrapped, changed = ns["_wrap_vip_business_func"](outer_friend_flow, "bot.application.flows.process_friend_farm")
        self.assertTrue(changed)
        self.assertEqual((True, True, True), wrapped(bot))
        self.assertEqual((False, False, False), (bot.member_active, bot.premium_active, bot.is_svip))

    def test_outer_friend_dispatch_functions_are_in_vip_context_patch_set(self):
        ns = load_vip_module_matcher()
        names = ns["_VIP_BUSINESS_FUNC_NAMES"]
        self.assertIn("process_friend_farm", names)
        self.assertIn("handle_friend_farm_actions", names)


if __name__ == "__main__":
    unittest.main()
