import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_nodes(functions=(), assignments=(), namespace=None):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted_functions = set(functions)
    wanted_assignments = set(assignments)
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted_functions:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in wanted_assignments
            for target in node.targets
        ):
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    result = dict(namespace or {})
    exec(compile(module, str(HOOK), "exec"), result)
    return result


class V230FeatureCompatibilityTests(unittest.TestCase):
    def test_auto_sell_runtime_aliases_are_wrapped(self):
        ns = load_nodes(
            assignments=("_VIP_BUSINESS_FUNC_NAMES",),
            namespace={"globals": globals},
        )
        names = ns["_VIP_BUSINESS_FUNC_NAMES"]
        self.assertTrue({
            "handle_home_auto_sell_fruit",
            "run_warehouse_sell_button_sequence",
            "self_auto_sell_fruit",
        }.issubset(names))

    def test_guard_dog_gate_accepts_public_predicate_alias(self):
        ns = load_nodes(functions=("_friend_guard_help_action_allowed",))
        calls = []

        def resolver(_context, name):
            calls.append(name)
            if name == "has_guard_dog_for_bottom_help_action":
                return (lambda *_args: True), "fixture.public-alias"
            return None, ""

        ns.update({
            "_guard_dog_ui_config_enabled": lambda: True,
            "_guard_dog_detection_mode_config": lambda: "avatar_frame",
            "_friend_guard_verified_entry_active": lambda _context: False,
            "_resolve_friend_guard_native_callable": resolver,
            "_write": lambda *_args, **_kwargs: None,
        })

        self.assertTrue(ns["_friend_guard_help_action_allowed"](
            object(), object(), (100, 200)
        ))
        self.assertEqual([
            "_has_guard_dog_for_bottom_help_action",
            "has_guard_dog_for_bottom_help_action",
        ], calls)

    def test_hidden_mode_text_settings_preserve_configured_values(self):
        ns = load_nodes(functions=("_configured_text",))
        self.assertIn("_configured_text", ns)
        ns["_cfg_get"] = lambda sections, key, default: {
            "miniapp_hide_mode": "transparent",
            "hidden_miniapp_restart_hide_timing": "detect_window_immediate",
        }.get(key, default)
        self.assertEqual(
            "transparent",
            ns["_configured_text"](("bot",), "miniapp_hide_mode", "minimize"),
        )
        self.assertEqual(
            "detect_window_immediate",
            ns["_configured_text"](
                ("bot",), "hidden_miniapp_restart_hide_timing", "after_capture"
            ),
        )


if __name__ == "__main__":
    unittest.main()
