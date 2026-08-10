import ast
import importlib.util
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
ROUTER = ROOT / "portable" / "v225_native_execution_router.py"


NATIVE_V225_CALLABLES = (
    "process_self_farm",
    "process_friend_farm",
    "handle_friend_farm_actions",
    "handle_home_harvest",
    "handle_home_planting",
    "_run_planting_flow",
    "_drag_seed_over_lands",
    "_plant_seed_over_lands",
    "_run_backpack_seed_priority_planting",
    "_detect_empty_lands",
    "_execute_planting_by_mode",
    "_buy_seed_for_crop",
    "_find_quad_empty_land_groups",
    "_try_plant_quad_act_seeds",
    "check_friend_help_request_entry",
    "check_friend_icon",
    "check_go_home_icon",
    "_has_go_home_icon",
    "go_home",
    "return_home",
    "_return_home",
    "check_friend_farm_bottom_help_all_entry",
    "check_friend_farm_bottom_steal_entry",
)


def load_hook_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    missing = wanted - {node.name for node in nodes}
    if missing:
        raise AssertionError("hook.py is missing: " + ", ".join(sorted(missing)))
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK), "__name__": "v430_isolated_hook"}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def load_router(testcase):
    testcase.assertTrue(
        ROUTER.is_file(),
        "native-v2.2.5 execution router must be a small independent module",
    )
    spec = importlib.util.spec_from_file_location("v430_native_router", ROUTER)
    if spec is None or spec.loader is None:
        raise AssertionError("native-v2.2.5 execution router cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native_method(name):
    def _method(self, *args, **kwargs):
        return name

    _method.__name__ = name
    return _method


def counting_wrapper(calls):
    def _wrapper(fn, *args, **kwargs):
        calls.append(getattr(fn, "__name__", "callable"))

        def wrapped(*call_args, **call_kwargs):
            return fn(*call_args, **call_kwargs)

        return wrapped, True

    return _wrapper


class NativeExecutionOwnerRoute20260809Tests(unittest.TestCase):
    def test_default_owner_reserves_native_v225_farm_and_friend_callables(self):
        """The default owner is v2.2.5, with a deliberate legacy rollback switch."""
        router = load_router(self)

        self.assertEqual("native-v225", router.execution_owner(environ={}))
        for name in NATIVE_V225_CALLABLES:
            self.assertFalse(
                router.legacy_wrapper_allowed(name, environ={}),
                name,
            )
        self.assertTrue(router.legacy_wrapper_allowed("FarmBotCV.start", environ={}))
        self.assertTrue(router.legacy_wrapper_allowed("unrelated_method", environ={}))
        self.assertEqual(
            "legacy",
            router.execution_owner(
                environ={"QQFARM_EXECUTION_OWNER": "legacy"}
            ),
        )
        self.assertTrue(
            router.legacy_wrapper_allowed(
                "process_self_farm",
                environ={"QQFARM_EXECUTION_OWNER": "legacy"},
            )
        )

    def test_vip_business_patch_keeps_native_v225_farm_friend_and_planting_callables(self):
        """The old VIP-business patch must not stack another business wrapper."""
        router = load_router(self)

        class FarmBotCV:
            pass

        for name in NATIVE_V225_CALLABLES:
            setattr(FarmBotCV, name, native_method(name))
        original = {name: FarmBotCV.__dict__[name] for name in NATIVE_V225_CALLABLES}
        module = types.ModuleType("bot.application.farm")
        module.FarmBotCV = FarmBotCV
        wrapper_calls = []
        wrapper = counting_wrapper(wrapper_calls)
        namespace = load_hook_functions("_patch_vip_business_loaded")
        namespace.update({
            "sys": types.SimpleNamespace(modules={module.__name__: module}),
            "_looks_vip_business_module": lambda _name, _module: True,
            "_force_vip_business_object": lambda _object, _depth: 0,
            "_write_planting_callable_inventory": lambda _module: None,
            "_VIP_BUSINESS_FUNC_NAMES": set(NATIVE_V225_CALLABLES),
            "_FRIEND_HOME_FUNC_NAMES": set(),
            "_FRIEND_NEXT_ENTRY_FUNC_NAMES": set(),
            "_BACKPACK_PROFILE_FUNC_NAMES": set(),
            "_VIP_BUSINESS_PATCH_LOG_SEEN": set(),
            "_write": lambda *_args, **_kwargs: None,
            "_qqfarm_legacy_wrapper_allowed": (
                lambda name: router.legacy_wrapper_allowed(name, environ={})
            ),
            "_wrap_friend_entry_verified_func": wrapper,
            "_wrap_friend_home_func": wrapper,
            "_wrap_friend_next_entry_func": wrapper,
            "_wrap_vip_business_func": wrapper,
            "_wrap_friend_guard_continuous_poll_func": wrapper,
            "_wrap_self_farm_friend_surface_guard": wrapper,
            "_wrap_home_harvest_planting_trigger": wrapper,
            "_wrap_home_planting_cooldown": wrapper,
            "_wrap_post_harvest_rescan_planting_gate": wrapper,
            "_wrap_planting_flow_fast": wrapper,
            "_wrap_single_land_seed_drag": wrapper,
            "_wrap_planting_crop_context_func": wrapper,
            "_wrap_planting_outcome_verify_func": wrapper,
            "_wrap_backpack_seed_priority_planting_fast": wrapper,
            "_wrap_detect_empty_lands_state": wrapper,
            "_wrap_buy_seed_for_crop_backpack_guard": wrapper,
            "_wrap_quad_empty_land_groups": wrapper,
            "_wrap_quad_act_seed_transaction": wrapper,
            "_wrap_backpack_profile_helper": wrapper,
        })

        changed = namespace["_patch_vip_business_loaded"]("v430-test")

        self.assertEqual([], changed)
        self.assertEqual([], wrapper_calls)
        for name, old in original.items():
            self.assertIs(old, FarmBotCV.__dict__[name], name)

    def test_friend_pause_patch_keeps_native_v225_friend_callables(self):
        """The old pause lock cannot sit in front of native friend work."""
        router = load_router(self)

        class FarmBotCV:
            process_friend_farm = native_method("process_friend_farm")
            handle_friend_farm_actions = native_method("handle_friend_farm_actions")

        original = {
            name: FarmBotCV.__dict__[name]
            for name in ("process_friend_farm", "handle_friend_farm_actions")
        }
        module = types.ModuleType("bot.application.actions_friend")
        module.FarmBotCV = FarmBotCV
        calls = []
        namespace = load_hook_functions("_patch_friend_pause_loaded")
        namespace.update({
            "sys": types.SimpleNamespace(modules={module.__name__: module}),
            "_looks_friend_runtime_module": lambda _name, _module: True,
            "_FRIEND_PAUSE_FUNC_NAMES": set(original),
            "_FRIEND_PAUSE_PATCH_LOG_SEEN": set(),
            "_write": lambda *_args, **_kwargs: None,
            "_qqfarm_legacy_wrapper_allowed": (
                lambda name: router.legacy_wrapper_allowed(name, environ={})
            ),
            "_wrap_friend_pause_func": counting_wrapper(calls),
        })

        changed = namespace["_patch_friend_pause_loaded"]("v430-test")

        self.assertEqual([], changed)
        self.assertEqual([], calls)
        for name, old in original.items():
            self.assertIs(old, FarmBotCV.__dict__[name], name)

    def test_runtime_diagnostics_leave_native_cycle_methods_unwrapped(self):
        """Startup diagnostics may remain, but must not own the native work cycle."""
        router = load_router(self)

        class FarmBotCV:
            start = native_method("start")
            run_cycle = native_method("run_cycle")
            process_self_farm = native_method("process_self_farm")
            process_friend_farm = native_method("process_friend_farm")
            handle_home_planting = native_method("handle_home_planting")

        native_names = (
            "run_cycle",
            "process_self_farm",
            "process_friend_farm",
            "handle_home_planting",
        )
        original_start = FarmBotCV.__dict__["start"]
        original = {name: FarmBotCV.__dict__[name] for name in native_names}
        module = types.ModuleType("bot.application.runtime")
        module.FarmBotCV = FarmBotCV
        calls = []
        namespace = load_hook_functions("_patch_runtime_start_diagnostics_for_module")
        namespace.update({
            "_RUNTIME_START_DIAG_PATCHED_METHODS": set(),
            "_RUNTIME_START_DIAG_PATCH_LOG_SEEN": set(),
            "_write": lambda *_args, **_kwargs: None,
            "_throttled_write": lambda *_args, **_kwargs: None,
            "_qqfarm_legacy_wrapper_allowed": (
                lambda name: router.legacy_wrapper_allowed(name, environ={})
            ),
            "_wrap_runtime_diag_method": (
                lambda fn, label: (calls.append(label) or counting_wrapper([])(fn)[0], True)
            ),
        })

        changed = namespace["_patch_runtime_start_diagnostics_for_module"](
            module, "v430-test"
        )

        self.assertEqual(1, changed)
        self.assertEqual(["FarmBotCV.start"], calls)
        for name, old in original.items():
            self.assertIs(old, FarmBotCV.__dict__[name], name)
        self.assertIsNot(original_start, FarmBotCV.__dict__["start"])


if __name__ == "__main__":
    unittest.main()
