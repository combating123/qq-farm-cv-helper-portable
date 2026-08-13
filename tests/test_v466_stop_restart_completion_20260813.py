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
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V466StopRestartCompletionTests(unittest.TestCase):
    def test_stop_completion_callback_runs_even_when_stop_signal_is_still_set(self):
        ns = load_functions("_wrap_runtime_diag_method")
        events = []
        owner = types.SimpleNamespace(_bot_stopping=True, bot_running=True)
        ns.update({
            "time": types.SimpleNamespace(time=lambda: 10.0),
            "_runtime_start_entry_label": lambda _label: False,
            "_runtime_stop_completion_entry_label": (
                lambda label: label == "FarmBotWindow._on_bot_stopped"
            ),
            "_stop_requested_in_args": (
                lambda *_args, **_kwargs: events.append("stop-check") or True
            ),
            "_stop_gate_return": (
                lambda name: events.append(("blocked", name)) or False
            ),
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_runtime_diag_repr": lambda *_args, **_kwargs: "{}",
            "_runtime_diag_state": lambda *_args, **_kwargs: "{}",
            "_daily_metrics_sync_runtime": lambda *_args, **_kwargs: None,
            "_qqfarm_install_visible_capture_priority": lambda *_args: None,
            "_qqfarm_runtime_page_readiness_gate": lambda *_args: True,
        })

        def native_stopped(window):
            events.append("native-stopped")
            window._bot_stopping = False
            window.bot_running = False
            return "completed"

        wrapped, changed = ns["_wrap_runtime_diag_method"](
            native_stopped, "FarmBotWindow._on_bot_stopped"
        )

        self.assertTrue(changed)
        self.assertEqual("completed", wrapped(owner))
        self.assertIn("native-stopped", events)
        self.assertFalse(owner._bot_stopping)
        self.assertFalse(owner.bot_running)
        self.assertFalse(any(isinstance(item, tuple) and item[0] == "blocked" for item in events))

    def test_ordinary_action_remains_blocked_after_stop_request(self):
        ns = load_functions("_wrap_runtime_diag_method")
        events = []
        owner = types.SimpleNamespace()
        ns.update({
            "time": types.SimpleNamespace(time=lambda: 10.0),
            "_runtime_start_entry_label": lambda _label: False,
            "_runtime_stop_completion_entry_label": lambda _label: False,
            "_stop_requested_in_args": lambda *_args, **_kwargs: True,
            "_stop_gate_return": lambda name: events.append(name) or False,
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_runtime_diag_repr": lambda *_args, **_kwargs: "{}",
            "_runtime_diag_state": lambda *_args, **_kwargs: "{}",
            "_daily_metrics_sync_runtime": lambda *_args, **_kwargs: None,
        })
        wrapped, _ = ns["_wrap_runtime_diag_method"](
            lambda _owner: events.append("native-action") or True,
            "FarmBotCV.process_self_farm",
        )
        self.assertFalse(wrapped(owner))
        self.assertNotIn("native-action", events)


if __name__ == "__main__":
    unittest.main()
