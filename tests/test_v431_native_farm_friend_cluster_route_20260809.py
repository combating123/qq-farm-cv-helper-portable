import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


LEGACY_FARM_FRIEND_PATCHERS = (
    "_friend_radish_diag_dump",
    "_patch_friend_radish_behavior_loaded",
    "_patch_friend_radish_diag_loaded",
    "_patch_friend_pause_loaded",
    "_patch_guard_dog_config_loaded",
    "_patch_vip_business_loaded",
)


ROOT_SUPPORT_PATCHERS = (
    "_patch_security_watchdogs_loaded",
    "_install_runtime_log_patch",
    "_install_config_override_patch",
    "_force_autolaunch_config_file",
    "_install_path_license_patch",
    "_runtime_scan",
    "_patch_wechat_focus_loaded",
    "_patch_share_target_guard_loaded",
    "_patch_share_entry_settle_loaded",
    "_patch_share_retry_backoff_loaded",
    "_patch_daily_flow_status_loaded",
    "_patch_daily_task_soft_retry_loaded",
    "_patch_start_debounce_loaded",
    "_patch_runtime_start_diagnostics_loaded",
    "_patch_native_v225_full_board_preflight_loaded",
    "_patch_native_v225_friend_help_confirmation_loaded",
    "_patch_gui_entitlement_aliases_loaded",
    "_patch_core_runtime_loaded",
    "_repair_daily_task_retry_state_file",
)


def load_hook_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v431_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class AdvancingClock:
    def __init__(self):
        self.value = 0.0

    def time(self):
        self.value += 10.0
        return self.value


def build_patch_namespace(*, legacy_owner):
    namespace = load_hook_functions(
        "_patch_tag_relevant",
        "_qqfarm_legacy_farm_friend_wrappers_enabled",
        "_patch_loaded",
    )
    calls = []

    def record(name):
        def _patcher(*_args, **_kwargs):
            calls.append(name)
            return 0

        return _patcher

    namespace.update({
        "time": AdvancingClock(),
        "sys": types.SimpleNamespace(modules={}),
        "_PATCH_LOADED_RUNNING": False,
        "_PATCH_LOADED_LAST_TS": 0.0,
        "_PATCH_LOADED_SEEN_RELEVANT": set(),
        "_PATCH_LOG_SEEN": set(),
        "_qqfarm_legacy_wrapper_allowed": lambda _label: bool(legacy_owner),
        "_is_target_module_name": lambda _name: False,
        "_looks_integrity_exit_module": lambda _module: False,
        "_patch_module": record("_patch_module"),
        "_patch_gui_tick_throttle_for_module": record(
            "_patch_gui_tick_throttle_for_module"
        ),
        "_write": lambda *_args, **_kwargs: None,
        "_daily_flow_repair_unverified_status": None,
    })
    for name in LEGACY_FARM_FRIEND_PATCHERS + ROOT_SUPPORT_PATCHERS:
        namespace[name] = record(name)
    return namespace, calls


class NativeFarmFriendClusterRoute20260809Tests(unittest.TestCase):
    def test_native_v225_skips_all_legacy_farm_friend_patchers_on_initial_and_ticks(self):
        """The old business cluster must not be reinstalled by the Qt timer."""
        namespace, calls = build_patch_namespace(legacy_owner=False)

        for tag in ("initial", "qt-safe-tick", "qt-safe-tick"):
            namespace["_patch_loaded"](tag)

        invoked_legacy = [
            name for name in calls if name in LEGACY_FARM_FRIEND_PATCHERS
        ]
        self.assertEqual([], invoked_legacy, calls)
        for name in ROOT_SUPPORT_PATCHERS:
            self.assertIn(name, calls, name)

    def test_explicit_legacy_owner_retains_the_old_cluster_as_a_rollback_path(self):
        """The emergency legacy switch keeps the existing hook behavior available."""
        namespace, calls = build_patch_namespace(legacy_owner=True)

        for tag in ("initial", "qt-safe-tick", "qt-safe-tick"):
            namespace["_patch_loaded"](tag)

        invoked_legacy = [
            name for name in calls if name in LEGACY_FARM_FRIEND_PATCHERS
        ]
        self.assertEqual(list(LEGACY_FARM_FRIEND_PATCHERS) * 3, invoked_legacy)
        for name in ROOT_SUPPORT_PATCHERS:
            self.assertIn(name, calls, name)


if __name__ == "__main__":
    unittest.main()
