import ast
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_share_patch_functions():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {
        "_looks_share_target_module",
        "_wrap_share_target_guard_func",
        "_patch_share_target_guard_for_module",
        "_patch_share_target_guard_loaded",
    }
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    calls = []
    namespace = {
        "_stop_requested_in_args": lambda a, k: False,
        "_stop_gate_return": lambda name: False,
        "_share_target_guard_config": lambda: {
            "enabled": True,
            "target_name": "指定好友",
            "dry_run": False,
            "allow_group": False,
        },
        "_share_log_runtime": lambda *a, **k: None,
        "_share_close_dialog": lambda *a, **k: None,
        "_share_search_and_maybe_confirm": lambda mod, cfg: calls.append((mod, cfg)) or True,
        "_write": lambda *a, **k: None,
        "_SHARE_TARGET_PATCH_LOG_SEEN": set(),
    }
    exec(compile(module, str(HOOK), "exec"), namespace)
    namespace["calls"] = calls
    return namespace


class ShareTargetPatchTests(unittest.TestCase):
    def test_obfuscated_module_with_first_friend_handler_is_recognized(self):
        ns = load_share_patch_functions()
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: "first-friend"

        self.assertTrue(ns["_looks_share_target_module"](mod))

    def test_loaded_scan_patches_obfuscated_share_module(self):
        ns = load_share_patch_functions()
        original_calls = []
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: original_calls.append(True) or True
        ns["sys"] = types.SimpleNamespace(modules={mod.__name__: mod})

        changed = ns["_patch_share_target_guard_loaded"]("unit-test")
        result = mod._click_share_dialog_first_friend_and_confirm()

        self.assertEqual([mod.__name__ + ":1"], changed)
        self.assertTrue(result)
        self.assertEqual([], original_calls)

    def test_obfuscated_first_friend_handler_is_replaced_by_exact_target_guard(self):
        ns = load_share_patch_functions()
        original_calls = []
        mod = types.ModuleType("bot._q8eacf4154f.freebenefits_flow")
        mod._click_share_dialog_first_friend_and_confirm = lambda: original_calls.append(True) or True

        changed = ns["_patch_share_target_guard_for_module"](mod, "unit-test")
        result = mod._click_share_dialog_first_friend_and_confirm()

        self.assertEqual(1, changed)
        self.assertTrue(result)
        self.assertEqual([], original_calls)
        self.assertEqual(1, len(ns["calls"]))
        self.assertIs(mod, ns["calls"][0][0])
        self.assertEqual("指定好友", ns["calls"][0][1]["target_name"])


if __name__ == "__main__":
    unittest.main()


