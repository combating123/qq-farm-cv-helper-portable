import ast
import unittest
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'
FIXTURE = ROOT / 'tests' / 'fixtures' / 'live-v463-quad-confirm-enabled-20260811.png'


def load_function(name):
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace[name]


class V463QuadOverlayFixtureTests(unittest.TestCase):
    def test_home_seed_inventory_is_not_misread_as_confirmation_layer(self):
        observe = load_function('_qqfarm_quad_overlay_observation')
        frame = cv2.imread(str(ROOT / 'tests' / 'fixtures' / 'home_seed_inventory_live_20260729.png'))
        self.assertIsNotNone(frame)
        result = observe(frame)
        self.assertFalse(result['present'], result)

    def test_confirm_enabled_overlay_is_detected_on_user_frame(self):
        observe = load_function('_qqfarm_quad_overlay_observation')
        frame = cv2.imread(str(FIXTURE))
        self.assertIsNotNone(frame)
        result = observe(frame)
        self.assertTrue(result['present'], result)
        self.assertTrue(result['confirm_enabled'], result)
        self.assertIsNotNone(result['confirm_center'], result)
        self.assertIsNotNone(result['cancel_center'], result)
        self.assertLess(abs(result['confirm_center'][0] - 448), 18, result)
        self.assertLess(abs(result['confirm_center'][1] - 497), 18, result)
        self.assertLess(abs(result['cancel_center'][0] - 328), 24, result)
        self.assertLess(abs(result['cancel_center'][1] - 616), 24, result)


if __name__ == '__main__':
    unittest.main()
