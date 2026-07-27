import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_effective_friend_cooldown():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_effective_friend_cooldown"
    ]
    if not nodes:
        return None
    node = nodes[0]
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_effective_friend_cooldown"]


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class SchedulerCooldownGuardTests(unittest.TestCase):
    def test_friend_cooldown_is_capped_below_patrol_interval(self):
        effective = load_effective_friend_cooldown()
        self.assertIsNotNone(effective)
        self.assertEqual(10, effective(15, 30))

    def test_valid_short_friend_cooldown_is_preserved(self):
        effective = load_effective_friend_cooldown()
        self.assertIsNotNone(effective)
        self.assertEqual(8, effective(15, 8))

    def test_small_patrol_interval_keeps_positive_cooldown(self):
        effective = load_effective_friend_cooldown()
        self.assertIsNotNone(effective)
        self.assertEqual(1, effective(3, 30))

    def test_config_file_sync_repairs_active_friend_cooldown(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("friend_colddown_time", source)
        self.assertIn("_effective_friend_cooldown(check_interval, friend_cooldown)", source)

    def test_runtime_config_keeps_required_friend_workflow_enabled(self):
        namespace = load_functions("_norm_key", "_config_override_value")
        namespace.update({
            "_friend_pause_active": lambda: False,
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_active_friend_sections": lambda: ["instance.1.friend", "friend"],
            "_cfg_get": lambda sections, option, default=None: default,
            "_effective_friend_cooldown": lambda interval, cooldown: 10,
            "_active_is_weixin_mode": lambda: False,
            "_FRIEND_PAUSE_FORCE_FALSE": set(),
            "_VIP_CONFIG_FORCED_BOOL_TRUE": set(),
            "_REQUIRED_FRIEND_BOT_BOOL_TRUE": {
                "enable_process_friend", "enable_process_friend_help_entry"
            },
            "_REQUIRED_FRIEND_SECTION_BOOL_TRUE": {
                "enable_steal", "enable_help", "enable_friend_steal_one",
                "enable_friend_steal_one_fallback",
                "enable_bottom_friend_list_help_all",
                "enable_bottom_friend_list_steal",
            },
        })
        override = namespace["_config_override_value"]
        for option in namespace["_REQUIRED_FRIEND_BOT_BOOL_TRUE"]:
            self.assertIs(True, override("instance.1.bot", option, "bool"), option)
        for option in namespace["_REQUIRED_FRIEND_SECTION_BOOL_TRUE"]:
            self.assertIs(True, override("instance.1.friend", option, "bool"), option)

    def test_runtime_config_keeps_bottom_steal_navigation_enabled(self):
        namespace = load_functions("_norm_key", "_config_override_value")
        namespace.update({
            "_friend_pause_active": lambda: False,
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_active_friend_sections": lambda: ["instance.1.friend", "friend"],
            "_cfg_get": lambda sections, option, default=None: default,
            "_effective_friend_cooldown": lambda interval, cooldown: 10,
            "_active_is_weixin_mode": lambda: False,
            "_FRIEND_PAUSE_FORCE_FALSE": set(),
            "_VIP_CONFIG_FORCED_BOOL_TRUE": set(),
            "_REQUIRED_FRIEND_BOT_BOOL_TRUE": set(),
            "_REQUIRED_FRIEND_SECTION_BOOL_TRUE": {
                "enable_bottom_friend_list_steal"
            },
        })
        override = namespace["_config_override_value"]
        self.assertIs(True, override(
            "instance.1.friend", "enable_bottom_friend_list_steal", "bool"
        ))
        self.assertEqual("True", override(
            "friend", "enable_bottom_friend_list_steal", "str"
        ))

    def test_config_file_sync_keeps_bottom_steal_navigation_enabled(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("active_friend_secs", source)
        self.assertIn("enable_bottom_friend_list_steal", source)
        self.assertIn("cur_sec in active_friend_secs", source)

    def test_runtime_config_override_uses_repaired_friend_cooldown(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("if o == 'friend_colddown_time'", source)
        self.assertIn("kind == 'int'", source)


    def test_runtime_object_restores_all_required_friend_workflow_switches(self):
        namespace = load_functions("_restore_runtime_business_switches")
        enabled = {
            "enable_process_friend",
            "enable_process_friend_help_entry",
            "enable_steal",
            "enable_help",
            "enable_friend_steal_one",
            "enable_friend_steal_one_fallback",
            "enable_bottom_friend_list_help_all",
            "enable_bottom_friend_list_steal",
        }
        namespace.update({
            "_active_bot_sections": lambda: ["instance.1.bot", "bot"],
            "_active_self_sections": lambda: ["instance.1.self", "self"],
            "_active_friend_sections": lambda: ["instance.1.friend", "friend"],
            "_active_planting_sections": lambda: ["instance.1.planting", "planting"],
            "_configured_bool": lambda sections, key, default=False: key in enabled,
            "_active_is_weixin_mode": lambda: False,
        })

        class Scheduler:
            enable_process_friend = False
            enable_process_friend_help_entry = False
            enable_steal = False
            enable_help = False
            enable_friend_steal = False
            enable_friend_help = False
            enable_friend_steal_one = False
            enable_friend_steal_one_fallback = False
            enable_bottom_friend_list_help_all = False
            enable_bottom_friend_list_steal = False

        scheduler = Scheduler()
        changed = namespace["_restore_runtime_business_switches"](scheduler)

        self.assertGreaterEqual(changed, 10)
        for attr in (
            "enable_process_friend",
            "enable_process_friend_help_entry",
            "enable_steal",
            "enable_help",
            "enable_friend_steal",
            "enable_friend_help",
            "enable_friend_steal_one",
            "enable_friend_steal_one_fallback",
            "enable_bottom_friend_list_help_all",
            "enable_bottom_friend_list_steal",
        ):
            self.assertIs(True, getattr(scheduler, attr), attr)


if __name__ == "__main__":
    unittest.main()
