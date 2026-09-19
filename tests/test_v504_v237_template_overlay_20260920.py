import ast
import hashlib
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
TEMPLATE_ROOT = ROOT / "portable" / "data" / "v237_templates"

PRIORITY_TEMPLATES = (
    "assert/templates/element/friend/seed_land/13.png",
    "assert/templates/element/friend/seed_land/14.png",
    "assert/templates/element/friend/seed_land/15.png",
    "assert/templates/element/friend/seed_land/16.png",
    "assert/templates/element/friend/seed_land/17.png",
    "assert/templates/element/friend_list/enter/0.png",
    "assert/templates/element/friend_list/enter/1.png",
    "assert/templates/element/self/empty_land/11-m-1.png",
    "assert/templates/element/self/empty_land/11-m.png",
    "assert/templates/element/self/empty_land/22-m-1.png",
    "assert/templates/element/self/empty_land/22-m.png",
    "assert/templates/element/self/empty_land/33-m-1.png",
    "assert/templates/element/self/empty_land/33-m.png",
    "assert/templates/element/self/empty_land/44-m-1.png",
    "assert/templates/element/self/empty_land/44-m.png",
    "assert/templates/element/self/empty_land/55-m.png",
)


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {
        "__file__": str(HOOK),
        "_QQFARM_V237_TEMPLATE_CACHE": {},
    }
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


def frame_digest(frame):
    return hashlib.sha256(memoryview(frame).tobytes()).hexdigest()


class V237TemplateOverlayTests(unittest.TestCase):
    def test_priority_templates_are_packaged_and_decodable(self):
        namespace = load_functions(
            "_qqfarm_v237_template_root",
            "_qqfarm_load_v237_template",
        )
        loader = namespace["_qqfarm_load_v237_template"]

        for relative in PRIORITY_TEMPLATES:
            path = TEMPLATE_ROOT / Path(relative)
            self.assertTrue(path.is_file(), path)
            frame = loader(relative)
            self.assertIsNotNone(frame, relative)
            self.assertGreater(int(frame.shape[0]), 0)
            self.assertGreater(int(frame.shape[1]), 0)

    def test_native_template_lists_receive_each_overlay_once(self):
        namespace = load_functions(
            "_qqfarm_v237_template_root",
            "_qqfarm_load_v237_template",
            "_qqfarm_template_frame_digest",
            "_qqfarm_merge_template_frames",
            "_patch_native_v237_template_overlays_for_module",
        )
        namespace["_write"] = lambda _message: None
        loader = namespace["_qqfarm_load_v237_template"]
        original = loader(PRIORITY_TEMPLATES[0])
        module = types.SimpleNamespace(
            __name__="bot._q17ae55bf47.fixture",
            empty_land_frames=[original],
            seed_land_frames=[],
            friend_list_enter_frames=[],
        )

        first = namespace[
            "_patch_native_v237_template_overlays_for_module"
        ](module, "fixture")
        second = namespace[
            "_patch_native_v237_template_overlays_for_module"
        ](module, "fixture-repeat")

        self.assertGreater(first, 0)
        self.assertEqual(0, second)
        self.assertEqual(10, len(module.empty_land_frames))
        self.assertEqual(5, len(module.seed_land_frames))
        self.assertEqual(2, len(module.friend_list_enter_frames))
        for frames in (
            module.empty_land_frames,
            module.seed_land_frames,
            module.friend_list_enter_frames,
        ):
            digests = [frame_digest(frame) for frame in frames]
            self.assertEqual(len(digests), len(set(digests)))

    def test_unrelated_module_is_not_modified(self):
        namespace = load_functions(
            "_qqfarm_v237_template_root",
            "_qqfarm_load_v237_template",
            "_qqfarm_template_frame_digest",
            "_qqfarm_merge_template_frames",
            "_patch_native_v237_template_overlays_for_module",
        )
        module = types.SimpleNamespace(__name__="gui.fixture", empty_land_frames=[])

        changed = namespace[
            "_patch_native_v237_template_overlays_for_module"
        ](module, "fixture")

        self.assertEqual(0, changed)
        self.assertEqual([], module.empty_land_frames)


if __name__ == "__main__":
    unittest.main()
