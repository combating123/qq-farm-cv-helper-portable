import ast
import hashlib
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURE = ROOT / "tests" / "fixtures" / "live-v488-current-friend-list-20260918.png"
FIXTURE_SHA256 = "4A22A48E4B27E01250D60ECC6044958BACF3B9E5BA3A629DBC3F89D86CA0652B"


def load_functions(*wanted):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(wanted)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class V489NativeFriendListPreflight20260918Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest().upper()
        if actual != FIXTURE_SHA256:
            raise AssertionError(f"fixture hash changed: {actual}")
        cls.namespace = load_functions(
            "_wrap_native_v225_friend_help_candidate_cache",
            "_friend_list_card_rows",
            "_friend_list_visit_button_rows",
        )
        cls.frame = cv2.imdecode(
            np.fromfile(str(FIXTURE), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if cls.frame is None:
            raise AssertionError("live friend-list fixture cannot be decoded")

    def test_native_owner_bridge_visits_visible_friend_card_before_native_noop(self):
        namespace = self.namespace
        frame = self.frame
        calls = []
        rows_fn = namespace["_friend_list_visit_button_rows"]
        namespace.update(
            {
                "_friend_guard_original_chain": lambda fn: [fn],
                "_qqfarm_capture_native_friend_help_frame": lambda _owner: frame,
                "_friend_list_visit_button_rows": rows_fn,
                "_handle_friend_list_surface": (
                    lambda owner, candidate: calls.append(
                        ("list", owner, candidate)
                    )
                    or "visited"
                ),
                "_throttled_write": lambda *_args, **_kwargs: None,
                "_write": lambda message: calls.append(("log", message)),
            }
        )
        context = types.SimpleNamespace()

        def native_process_friend(owner, *_args, **_kwargs):
            calls.append(("original", owner))
            return "native-result"

        wrapped, changed = namespace[
            "_wrap_native_v225_friend_help_candidate_cache"
        ](
            native_process_friend,
            "bot.infrastructure.legacy_bot_engine.FarmBotCV.process_friend_farm",
        )

        result = wrapped(context)

        self.assertTrue(changed)
        self.assertFalse(result)
        self.assertTrue(any(item[0] == "list" for item in calls))
        self.assertFalse(any(item[0] == "original" for item in calls))


if __name__ == "__main__":
    unittest.main()
