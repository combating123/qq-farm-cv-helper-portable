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
        "_NATIVE_V225_AUTO_FERTILIZE_PATCH_LOG_SEEN",
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
    namespace = {
        "__name__": "v448_native_v225_auto_fertilize",
        "_write": lambda *_args, **_kwargs: None,
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class NativeV225AutoFertilize20260810Tests(unittest.TestCase):
    def test_native_auto_fertilize_runs_under_temporary_entitlement_and_restores(self):
        namespace = load_functions(
            "_enter_vip_entitlement_context",
            "_restore_vip_entitlement_context",
            "_wrap_native_v225_auto_fertilize_entry",
        )
        self.assertIn("_wrap_native_v225_auto_fertilize_entry", namespace)

        native_globals = {}
        exec(
            "def _qf_aa860ac25206(feature_key):\n"
            "    return True\n"
            "def native_auto_fertilize(bot):\n"
            "    observed = (\n"
            "        bot.auto_fertilize_one,\n"
            "        bot._qf_3dc9b7de9bd9('auto_fertilize', 'home'),\n"
            "        _qf_aa860ac25206('auto_fertilize'),\n"
            "    )\n"
            "    bot.calls.append(observed)\n"
            "    if not bot.auto_fertilize_one:\n"
            "        return 'disabled'\n"
            "    return 'fertilized' if observed[1:] == (True, False) else 'vip-blocked'\n",
            native_globals,
        )
        original_security_gate = native_globals["_qf_aa860ac25206"]

        class Bot:
            auto_fertilize_one = True

            def __init__(self):
                self.calls = []

            def _qf_3dc9b7de9bd9(self, feature_key, context=""):
                return False

        wrapped, changed = namespace["_wrap_native_v225_auto_fertilize_entry"](
            native_globals["native_auto_fertilize"],
            "bot.fixture._run_auto_fertilize_after_planting",
        )
        bot = Bot()

        self.assertTrue(changed)
        self.assertEqual("fertilized", wrapped(bot))
        self.assertEqual([(True, True, False)], bot.calls)
        self.assertFalse(bot._qf_3dc9b7de9bd9("auto_fertilize", "home"))
        self.assertIs(original_security_gate, native_globals["_qf_aa860ac25206"])
        self.assertTrue(native_globals["_qf_aa860ac25206"]("auto_fertilize"))

    def test_native_auto_fertilize_preserves_user_disabled_switch(self):
        namespace = load_functions(
            "_enter_vip_entitlement_context",
            "_restore_vip_entitlement_context",
            "_wrap_native_v225_auto_fertilize_entry",
        )
        self.assertIn("_wrap_native_v225_auto_fertilize_entry", namespace)

        def native_auto_fertilize(bot):
            bot.observed_switch = bot.auto_fertilize_one
            return "disabled" if not bot.auto_fertilize_one else "ran"

        class Bot:
            auto_fertilize_one = False
            observed_switch = None

        wrapped, changed = namespace["_wrap_native_v225_auto_fertilize_entry"](
            native_auto_fertilize,
            "bot.fixture._run_auto_fertilize_after_planting",
        )
        bot = Bot()

        self.assertTrue(changed)
        self.assertEqual("disabled", wrapped(bot))
        self.assertFalse(bot.observed_switch)
        self.assertFalse(bot.auto_fertilize_one)

    def test_loaded_native_patcher_wraps_class_entry_in_native_owner_mode(self):
        namespace = load_functions(
            "_enter_vip_entitlement_context",
            "_restore_vip_entitlement_context",
            "_wrap_native_v225_auto_fertilize_entry",
            "_patch_native_v225_auto_fertilize_for_module",
            "_patch_native_v225_auto_fertilize_loaded",
        )
        self.assertIn("_patch_native_v225_auto_fertilize_loaded", namespace)

        class PlantingFlow:
            def _run_auto_fertilize_after_planting(self):
                return self._qf_3dc9b7de9bd9("auto_fertilize")

            def _qf_3dc9b7de9bd9(self, feature_key, context=""):
                return False

        module = types.SimpleNamespace(PlantingFlow=PlantingFlow)
        namespace["sys"] = types.SimpleNamespace(
            modules={"bot.application.native_planting": module}
        )

        changed = namespace["_patch_native_v225_auto_fertilize_loaded"]("test")
        bot = PlantingFlow()

        self.assertEqual(["bot.application.native_planting:1"], changed)
        self.assertTrue(bot._run_auto_fertilize_after_planting())
        self.assertFalse(bot._qf_3dc9b7de9bd9("auto_fertilize"))
        self.assertTrue(getattr(
            PlantingFlow._run_auto_fertilize_after_planting,
            "__qqfarm_native_v225_auto_fertilize_wrapped__",
            False,
        ))


if __name__ == "__main__":
    unittest.main()
