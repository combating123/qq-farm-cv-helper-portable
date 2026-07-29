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

    def test_friend_cooldown_helper_is_pure_and_does_not_rewrite_config(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        self.assertIn("def _effective_friend_cooldown", source)
        start = source.index("def _force_autolaunch_config_file")
        end = source.index("def _config_override_value", start)
        self.assertNotIn("friend_colddown_time", source[start:end])

    def test_runtime_config_does_not_override_user_business_switches(self):
        namespace = load_functions("_norm_key", "_config_override_value")
        namespace.update({
            "_active_is_weixin_mode": lambda: False,
            "_VIP_CONFIG_FORCED_BOOL_TRUE": set(),
        })
        override = namespace["_config_override_value"]
        for section, option in (
            ("instance.1.bot", "enable_process_friend"),
            ("instance.1.bot", "enable_rest_window"),
            ("instance.1.bot", "enable_periodic_restart"),
            ("instance.1.friend", "enable_steal"),
            ("instance.1.friend", "enable_bottom_friend_list_steal"),
            ("instance.1.self", "auto_fertilize_one"),
            ("instance.1.planting", "player_level"),
            ("instance.1.bot", "friend_colddown_time"),
        ):
            self.assertIsNone(override(section, option, "bool"), option)
            self.assertIsNone(override(section, option, "str"), option)

    def test_config_file_patch_is_read_only_for_user_settings(self):
        source = HOOK.read_text(encoding="utf-8-sig")
        start = source.index("def _force_autolaunch_config_file")
        end = source.index("def _config_override_value", start)
        body = source[start:end]
        self.assertNotIn("open(cfg, 'wb')", body)
        self.assertNotIn("line = key + ' = True'", body)
        self.assertNotIn("friend_colddown_time = ", body)

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
