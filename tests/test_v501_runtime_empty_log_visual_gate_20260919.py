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
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class RuntimeEmptyLogVisualGateTests(unittest.TestCase):
    def _namespace(self, context, logs):
        namespace = load_functions(
            "_qqfarm_home_priority_active",
            "_qqfarm_update_home_priority",
            "_note_runtime_planting_outcome",
        )
        namespace.update({
            "time": types.SimpleNamespace(time=lambda: 100.0),
            "_LAST_SUCCESSFUL_FULL_PLANTING_TS": 0.0,
            "_ACTIVE_RUN_CYCLE_CONTEXT": context,
            "_write": lambda message: logs.append(str(message)),
        })
        return namespace

    def test_native_empty_count_log_does_not_arm_home_priority_without_visual_proof(self):
        """A native count line is telemetry, not permission to click land or block friends."""
        context = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_recent_empty_lands=[],
        )
        logs = []
        namespace = self._namespace(context, logs)

        namespace["_note_runtime_planting_outcome"](
            "\u2714 \u68c0\u6d4b\u5230\u3010\u7a7a\u5730\u3011\u5171 5 \u5757, \u76ee\u6807\u4f5c\u7269\uff1a\u9cc4\u68a8"
        )

        self.assertFalse(namespace["_qqfarm_home_priority_active"](context))
        self.assertEqual(0, context._qqfarm_recent_empty_land_count)
        self.assertEqual(5, context._qqfarm_native_empty_log_claim_count)
        self.assertEqual(100.0, context._qqfarm_native_empty_log_claim_ts)
        self.assertTrue(any(
            "native empty-land log held for visual verification" in message
            for message in logs
        ))

    def test_native_empty_count_log_does_not_overwrite_existing_visual_count(self):
        """An already-confirmed visual queue keeps its own count and coordinates."""
        visual_lands = [
            {"center": (180, 420)},
            {"center": (220, 440)},
        ]
        context = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=2,
            _qqfarm_recent_empty_lands=list(visual_lands),
        )
        logs = []
        namespace = self._namespace(context, logs)
        namespace["_qqfarm_update_home_priority"](
            context,
            2,
            now_ts=99.0,
            reason="detect-empty-lands:confirmed",
        )

        namespace["_note_runtime_planting_outcome"](
            "\u68c0\u6d4b\u5230\u3010\u7a7a\u5730\u3011\u5171 9 \u5757"
        )

        self.assertTrue(namespace["_qqfarm_home_priority_active"](context))
        self.assertEqual(2, context._qqfarm_home_empty_land_remaining)
        self.assertEqual(2, context._qqfarm_recent_empty_land_count)
        self.assertEqual(visual_lands, context._qqfarm_recent_empty_lands)
        self.assertEqual(9, context._qqfarm_native_empty_log_claim_count)


if __name__ == "__main__":
    unittest.main()
