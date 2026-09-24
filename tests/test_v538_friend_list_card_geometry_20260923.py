import ast
import hashlib
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
FIXTURE = ROOT / "tests" / "fixtures" / "live-friend-list-card-loop-20260918.png"
FIXTURE_SHA256 = "A2F8325AE67601846A868CD2FBABB4A07C087DC660484295451093D49D304036"


def load_rows_detector():
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = {"_friend_list_card_rows", "_friend_list_visit_button_rows"}
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    if {node.name for node in nodes} != wanted:
        raise AssertionError("friend-list row detector functions are missing")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace["_friend_list_visit_button_rows"]


def read_bgr(path):
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if actual != FIXTURE_SHA256:
        raise AssertionError(f"fixture hash changed: {actual}")
    encoded = np.fromfile(str(path), dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        raise AssertionError(f"fixture cannot be decoded: {path}")
    return frame


class FriendListCardGeometry20260923Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = read_bgr(FIXTURE)
        if cls.frame.shape[:2] != (800, 428):
            raise AssertionError(f"unexpected fixture size: {cls.frame.shape[:2]}")
        cls.detector = staticmethod(load_rows_detector())

    def _assert_card_rows(self, frame):
        rows = list(self.detector(frame) or [])
        self.assertGreaterEqual(len(rows), 3, rows)
        self.assertTrue(
            all(row.get("source") == "friend-card-band" for row in rows[:3]),
            rows,
        )
        centers = [tuple(row["center"]) for row in rows[:3]]
        self.assertEqual([312, 312, 312], [point[0] for point in centers])
        self.assertEqual([434, 576, 720], [point[1] for point in centers])
        # The search field ends before the first card.  A row in this band is
        # the production failure: it produces a successful click acknowledgement
        # without entering any friend's farm.
        self.assertTrue(all(point[1] >= 374 for point in centers), centers)

    def test_bgr_printwindow_uses_card_action_centers(self):
        self._assert_card_rows(self.frame)

    def test_rgb_backed_capture_uses_same_card_action_centers(self):
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self._assert_card_rows(rgb_frame)


if __name__ == "__main__":
    unittest.main()
