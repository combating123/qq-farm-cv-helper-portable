import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_function(name):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    node = next(
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace[name], namespace


class RuntimeNoFrameDiagnosticsTests(unittest.TestCase):
    def test_first_no_frame_cycle_records_reason_state_and_retry(self):
        diagnostic, namespace = load_function(
            "_qqfarm_runtime_no_frame_diagnostic"
        )
        events = []
        context = types.SimpleNamespace()
        namespace.update({
            "_throttled_write": lambda key, message, seconds: events.append(
                (key, message, seconds)
            ),
        })

        emitted = diagnostic(
            context,
            reason="no-frame",
            label="FarmBotCV.run_cycle",
            now_ts=100.0,
            retry_after=112.0,
            wgc_state="pending",
            scene_hint="friend",
        )

        self.assertTrue(emitted)
        self.assertEqual(1, len(events))
        self.assertEqual("v555-runtime-no-frame", events[0][0])
        self.assertIn("reason=no-frame", events[0][1])
        self.assertIn("wgc=pending", events[0][1])
        self.assertIn("scene=friend", events[0][1])
        self.assertEqual(112.0, context._qqfarm_runtime_gate_retry_after)

    def test_same_no_frame_state_is_debounced_until_retry_or_state_change(self):
        diagnostic, namespace = load_function(
            "_qqfarm_runtime_no_frame_diagnostic"
        )
        events = []
        context = types.SimpleNamespace()
        namespace.update({
            "_throttled_write": lambda key, message, seconds: events.append(
                (key, message, seconds)
            ),
        })

        self.assertTrue(
            diagnostic(context, "no-frame", "FarmBotCV.run_cycle", 100.0, 112.0, "pending", "friend")
        )
        self.assertFalse(
            diagnostic(context, "no-frame", "FarmBotCV.run_cycle", 105.0, 112.0, "pending", "friend")
        )
        self.assertTrue(
            diagnostic(context, "no-frame", "FarmBotCV.run_cycle", 113.0, 125.0, "pending", "friend")
        )
        self.assertTrue(
            diagnostic(context, "non-farm-frame", "FarmBotCV.run_cycle", 114.0, 126.0, "blank", "friend")
        )
        self.assertEqual(3, len(events))


if __name__ == "__main__":
    unittest.main()
