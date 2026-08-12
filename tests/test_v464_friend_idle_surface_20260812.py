import ast
import hashlib
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
CURRENT_FIXTURE = ROOT / "tests" / "fixtures" / "live-v464-friend-idle-surface-20260812.png"
SELF_HOME_FIXTURE = ROOT / "tests" / "fixtures" / "live-v410-visible-home-bottom-friend-nav-20260808-220233.png"

CLASSIFIER_FUNCTIONS = {
    "_friend_guard_friend_ui_state",
    "_friend_guard_match_template",
    "_friend_guard_read_template",
    "_friend_selected_carousel_card_bounds",
    "_friend_guard_help_button_match",
    "_friend_guard_steal_button_match",
    "_friend_list_visit_button_rows",
}


def load_classifier():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in CLASSIFIER_FUNCTIONS
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    portable = HOOK.parent
    namespace.update({
        "_FRIEND_HOME_TEMPLATE_PATH": str(portable / "friend_home_button.png"),
        "_FRIEND_HELP_ALL_TEMPLATE_PATH": str(portable / "friend_help_all_button.png"),
        "_FRIEND_STEAL_ALL_TEMPLATE_PATH": str(portable / "friend_steal_all_button.png"),
        "_FRIEND_LIST_TEMPLATE_PATH": str(portable / "friend_list_tabs.png"),
        "_FRIEND_GUARD_TEMPLATE_CACHE": {},
    })
    return namespace


def decode(path):
    encoded = np.fromfile(str(path), dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        raise AssertionError("fixture decode failed: " + str(path))
    return frame


class V464FriendIdleSurfaceTests(unittest.TestCase):
    def test_current_672x1193_friend_surface_stays_friend_after_runtime_normalization(self):
        namespace = load_classifier()
        raw = decode(CURRENT_FIXTURE)
        self.assertEqual((1193, 672, 3), raw.shape)
        normalized = cv2.resize(raw, (428, 800), interpolation=cv2.INTER_AREA)

        self.assertIs(
            True,
            namespace["_friend_guard_friend_ui_state"](normalized),
            repr(namespace.get("_FRIEND_HOME_LAST_MATCH", {})),
        )

    def test_expanded_return_home_tolerance_does_not_promote_self_home(self):
        namespace = load_classifier()
        raw = decode(SELF_HOME_FIXTURE)
        normalized = cv2.resize(raw, (428, 800), interpolation=cv2.INTER_AREA)

        self.assertIs(False, namespace["_friend_guard_friend_ui_state"](normalized))


if __name__ == "__main__":
    unittest.main()
