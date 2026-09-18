import ast
import hashlib
import types
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
CURRENT_FIXTURE = ROOT / "tests" / "fixtures" / "live-v486-current-friend-list-20260918.png"
CURRENT_FIXTURE_SHA256 = "4E17430E968C506A3566A952A29C9197D6E5F683E27D1DF96A20DF64BED482B4"
TASK_FIXTURE = ROOT / "tests" / "fixtures" / "live-v422-current-friend-list-20260808.png"


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


class V487CurrentFriendCardRows20260918Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        actual = hashlib.sha256(CURRENT_FIXTURE.read_bytes()).hexdigest().upper()
        if actual != CURRENT_FIXTURE_SHA256:
            raise AssertionError(f"fixture hash changed: {actual}")
        cls.namespace = load_functions(
            "_friend_list_card_rows",
            "_friend_list_visit_button_rows",
            "_handle_friend_list_surface",
        )
        cls.rows = staticmethod(cls.namespace["_friend_list_visit_button_rows"])
        cls.current = cv2.imdecode(
            np.fromfile(str(CURRENT_FIXTURE), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        cls.task = cv2.imdecode(
            np.fromfile(str(TASK_FIXTURE), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if cls.current is None or cls.task is None:
            raise AssertionError("regression fixtures cannot be decoded")

    def test_current_three_card_friend_list_produces_ordered_click_rows(self):
        rows = self.rows(self.current)

        self.assertGreaterEqual(len(rows), 3)
        centers = [row["center"] for row in rows]
        self.assertEqual(sorted(centers, key=lambda item: item[1]), centers)
        self.assertEqual(3, len({center[1] for center in centers}))
        self.assertTrue(380 <= centers[0][1] <= 500, centers)
        self.assertTrue(510 <= centers[1][1] <= 645, centers)
        self.assertTrue(650 <= centers[2][1] <= 790, centers)
        for x, _y in centers[:3]:
            self.assertTrue(0.60 * self.current.shape[1] <= x <= 0.82 * self.current.shape[1], centers)

    def test_task_surface_does_not_become_friend_card_rows(self):
        self.assertEqual([], self.rows(self.task))

    def test_current_card_row_enters_first_friend_and_emits_visit_proof(self):
        clicks = []
        logs = []
        namespace = self.namespace
        namespace.update(
            {
                "_guard_dog_ui_config_enabled": lambda: False,
                "_guard_dog_detection_mode_config": lambda: "avatar_frame",
                "_friend_guard_post_client_click": (
                    lambda *args: clicks.append(args) or True
                ),
                "_set_friend_chain_fast_interval": lambda *_args: None,
                "_write": lambda message: logs.append(str(message)),
                "_throttled_write": lambda *_args: None,
            }
        )
        context = types.SimpleNamespace()

        result = namespace["_handle_friend_list_surface"](context, self.current)

        self.assertEqual("visited", result)
        self.assertEqual((312, 438, 428, 800), clicks[0])
        self.assertTrue(any("v203 friend list visit row=(312, 438)" in line for line in logs))


if __name__ == "__main__":
    unittest.main()
