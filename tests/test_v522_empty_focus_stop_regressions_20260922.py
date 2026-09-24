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
    nodes = []
    assignments = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            nodes.append(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    assignments.append(node)
                    break
    module = ast.Module(body=assignments + nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class EmptyLandProofRegressionTests(unittest.TestCase):
    def test_native_buy_seed_log_does_not_arm_home_priority_without_fresh_empty_proof(self):
        namespace = load_functions(
            "_qqfarm_runtime_buy_seed_has_fresh_empty_proof",
        )
        checker = namespace["_qqfarm_runtime_buy_seed_has_fresh_empty_proof"]
        context = types.SimpleNamespace(
            _qqfarm_recent_empty_land_count=0,
            _qqfarm_recent_empty_lands=[],
            _qqfarm_empty_land_board_gate_state="bypass",
        )
        self.assertFalse(checker(context, now_ts=100.0))

    def test_fresh_zero_with_unconfirmed_board_is_not_planting_or_shop_authority(self):
        namespace = load_functions("_qqfarm_zero_empty_observation_is_actionable")
        checker = namespace["_qqfarm_zero_empty_observation_is_actionable"]
        context = types.SimpleNamespace(
            _qqfarm_home_visual_recheck_required=False,
            _qqfarm_empty_land_scene_confirmed_full=True,
        )
        self.assertFalse(checker(context, "bypass", fresh=True))
        self.assertFalse(checker(context, "unknown", fresh=True))
        self.assertTrue(checker(context, "confirmed", fresh=True))
        context._qqfarm_empty_land_scene_confirmed_full = False
        self.assertFalse(checker(context, "confirmed", fresh=True))


class WechatFocusProofRegressionTests(unittest.TestCase):
    def test_native_none_result_with_applied_hwnd_is_proven(self):
        namespace = load_functions(
            "_wechat_focus_coerce_hwnd",
            "_wechat_focus_state_snapshot",
            "_wechat_focus_apply_proved",
        )
        owner = types.SimpleNamespace(
            bound_hwnd=0x1234,
            bound_pid=2468,
            bound_process_name="wechatappex.exe",
            existing_window_probe_done=True,
            applied_hwnd=0x1234,
        )
        self.assertTrue(
            namespace["_wechat_focus_apply_proved"](
                owner, 0x1234, None, before_state=()
            )
        )


class StopAutostartRegressionTests(unittest.TestCase):
    def test_stop_latch_blocks_qt_autostart_until_manual_start_clears_it(self):
        namespace = load_functions(
            "_QT_AUTOSTART_BLOCKED_BY_STOP",
            "_QT_AUTOSTART_CLICKED",
            "_QT_AUTOSTART_ATTEMPTS",
            "_QT_AUTOSTART_LAST_ATTEMPT_TS",
            "_QT_AUTOSTART_COOLDOWN_UNTIL",
            "_QT_AUTOSTART_MAX_ATTEMPTS",
            "_QT_AUTOSTART_RETRY_SECONDS",
            "_qt_runtime_already_running",
            "_qt_autostart_running_button",
        )
        namespace["_QT_AUTOSTART_BLOCKED_BY_STOP"] = True
        namespace["time"] = types.SimpleNamespace(monotonic=lambda: 1.0)

        class Button:
            def __init__(self):
                self.clicks = 0

            def text(self):
                return "开始运行"

            def isEnabled(self):
                return True

            def isVisible(self):
                return True

            def click(self):
                self.clicks += 1

        button = Button()
        app = types.SimpleNamespace(
            allWidgets=lambda: [button],
            topLevelWidgets=lambda: [button],
        )
        self.assertFalse(namespace["_qt_autostart_running_button"](app))
        self.assertEqual(0, button.clicks)

    def test_manual_start_clears_explicit_stop_latch_before_native_start(self):
        namespace = load_functions(
            "_prepare_runtime_start_request",
        )
        namespace["_QT_AUTOSTART_BLOCKED_BY_STOP"] = True
        runtime = types.SimpleNamespace(
            _qqfarm_explicit_stop_latched=True,
            stop_requested=False,
        )
        changed = namespace["_prepare_runtime_start_request"]((runtime,), {})
        self.assertGreaterEqual(changed, 1)
        self.assertFalse(runtime._qqfarm_explicit_stop_latched)
        self.assertFalse(namespace["_QT_AUTOSTART_BLOCKED_BY_STOP"])


if __name__ == "__main__":
    unittest.main()
