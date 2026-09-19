import ast
import hashlib
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURE = (
    ROOT / "tests" / "fixtures" /
    "live-v499-current-self-home-sanitized-20260919.png"
)
FIXTURE_SHA256 = "C52A3F4DDB5F71BF2FFDB1A50587B8CCFB463F35195DA009D0767ABEC6CF07CA"


def load_functions(*names):
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
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    portable = HOOK.parent
    namespace.update({
        "_FRIEND_HOME_TEMPLATE_PATH": str(portable / "friend_home_button.png"),
        "_FRIEND_HELP_ALL_TEMPLATE_PATH": str(
            portable / "friend_help_all_button.png"
        ),
        "_FRIEND_STEAL_ALL_TEMPLATE_PATH": str(
            portable / "friend_steal_all_button.png"
        ),
        "_FRIEND_LIST_TEMPLATE_PATH": str(portable / "friend_list_tabs.png"),
        "_FRIEND_GUARD_TEMPLATE_CACHE": {},
    })
    return namespace


class V499CurrentSelfSurfaceNotFriendList20260919Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest().upper()
        if actual != FIXTURE_SHA256:
            raise AssertionError(f"fixture hash changed: {actual}")
        encoded = np.fromfile(str(FIXTURE), dtype=np.uint8)
        cls.frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if cls.frame is None:
            raise AssertionError("current self-home fixture cannot be decoded")

    def test_current_self_home_with_green_controls_is_not_friend_list(self):
        """Self-home controls must not be treated as four friend-list rows."""
        namespace = load_functions(
            "_friend_guard_friend_ui_state",
            "_friend_guard_match_template",
            "_friend_guard_read_template",
            "_friend_selected_carousel_card_bounds",
            "_friend_guard_help_button_match",
            "_friend_guard_steal_button_match",
            "_friend_list_visit_button_rows",
            "_friend_list_card_rows",
        )

        actual = namespace["_friend_guard_friend_ui_state"](self.frame)
        rows = namespace["_friend_list_visit_button_rows"](self.frame)

        self.assertIs(
            False,
            actual,
            "self-home was misclassified as friend-list: "
            + repr(namespace.get("_FRIEND_LIST_LAST_MATCH", {})),
        )
        self.assertEqual([], rows, "self-home controls leaked as friend rows: " + repr(rows))

    def test_visible_self_surface_releases_stale_friend_terminal_state(self):
        """A real home frame must not remain behind the friend terminal latch."""
        namespace = load_functions(
            "_wrap_native_v225_friend_help_candidate_cache",
            "_qqfarm_native_friend_surface_cache_fresh",
            "_qqfarm_reconcile_visible_self_surface",
            "_friend_list_visit_button_rows",
        )
        calls = []
        namespace.update({
            "_friend_guard_original_chain": lambda fn: [fn],
            "_qqfarm_capture_native_friend_help_frame": lambda _owner: self.frame,
            "_friend_list_visit_button_rows": lambda _frame: [],
            "_friend_guard_friend_ui_state": lambda _frame: False,
            "_friend_selected_carousel_card_bounds": lambda _frame: None,
            "_daily_business_date": lambda: "2026-09-19",
            "_friend_progress_journal_rearm_for_business_date": lambda *_args, **_kwargs: False,
            "_friend_guard_poll_dispatch_allowed": lambda _owner: False,
            "_qqfarm_native_friend_surface_cache_fresh": lambda _owner: False,
            "_throttled_write": lambda *args, **_kwargs: calls.append(args),
            "_write": lambda message: calls.append((message,)),
        })
        context = types.SimpleNamespace(
            _qqfarm_friend_guard_empty_latched=True,
            _qqfarm_friend_chain_pending=False,
            _qqfarm_friend_chain_active=False,
            _qqfarm_friend_chain_exhausted=True,
            _qqfarm_friend_chain_allow_home=True,
            _qqfarm_friend_cycle_seen=True,
            _qqfarm_friend_entry_pending=False,
            _last_friend_farm_go_home_present=True,
            _qqfarm_cycle_branch_hint="friend",
            _qqfarm_live_scene_hint="friend",
        )

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](native_process_friend, "FarmBotCV.process_friend_farm")

        result = wrapped(context)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertFalse(context._qqfarm_friend_guard_empty_latched)
        self.assertFalse(context._qqfarm_friend_cycle_seen)
        self.assertEqual("self", context._qqfarm_cycle_branch_hint)
        self.assertEqual("home", context._qqfarm_live_scene_hint)
        self.assertFalse(any(item[0] == "original" for item in calls))


if __name__ == "__main__":
    unittest.main()
