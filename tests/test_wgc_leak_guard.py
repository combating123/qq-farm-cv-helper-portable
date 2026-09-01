import ast
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


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


class WgcLeakGuardTests(unittest.TestCase):
    def test_rebuild_cooldown_and_burst_limit_are_bounded(self):
        namespace = load_functions(
            "_qqfarm_wgc_rebuild_allowed",
            "_qqfarm_wgc_note_rebuild",
        )
        namespace.update({
            "_QQFARM_WGC_REBUILD_HISTORY": [],
            "_QQFARM_WGC_REBUILD_COOLDOWN_UNTIL": 0.0,
            "_QQFARM_WGC_REBUILD_WINDOW_SECONDS": 300.0,
            "_QQFARM_WGC_REBUILD_MAX_PER_WINDOW": 3,
            "_QQFARM_WGC_REBUILD_COOLDOWN_SECONDS": 30.0,
            "_QQFARM_WGC_REBUILD_BURST_COOLDOWN_SECONDS": 300.0,
        })

        self.assertTrue(namespace["_qqfarm_wgc_rebuild_allowed"](now=100.0))
        namespace["_qqfarm_wgc_note_rebuild"]("blank-surface", now=100.0)
        self.assertFalse(namespace["_qqfarm_wgc_rebuild_allowed"](now=100.1))
        self.assertTrue(namespace["_qqfarm_wgc_rebuild_allowed"](now=131.0))
        namespace["_qqfarm_wgc_note_rebuild"]("blank-surface", now=131.0)
        namespace["_qqfarm_wgc_note_rebuild"]("blank-surface", now=162.0)
        namespace["_qqfarm_wgc_note_rebuild"]("blank-surface", now=193.0)
        self.assertFalse(namespace["_qqfarm_wgc_rebuild_allowed"](now=194.0))
        self.assertFalse(namespace["_qqfarm_wgc_rebuild_allowed"](now=493.0))
        self.assertTrue(namespace["_qqfarm_wgc_rebuild_allowed"](now=493.1))

    def test_generation_rejects_callbacks_from_previous_session(self):
        namespace = load_functions("_qqfarm_wgc_callback_is_current")
        namespace["_QQFARM_WGC_GENERATION"] = 8
        self.assertTrue(namespace["_qqfarm_wgc_callback_is_current"](8))
        self.assertFalse(namespace["_qqfarm_wgc_callback_is_current"](7))
        self.assertFalse(namespace["_qqfarm_wgc_callback_is_current"](None))

    def test_kernel_pool_guard_uses_provider_and_latches_trip(self):
        namespace = load_functions("_qqfarm_kernel_pool_guard")
        samples = iter([
            {"nonpaged_bytes": 100 * 1024 * 1024},
            {"nonpaged_bytes": 3 * 1024 * 1024 * 1024},
            {"nonpaged_bytes": 100 * 1024 * 1024},
        ])
        events = []
        namespace.update({
            "_QQFARM_KERNEL_POOL_LAST_SAMPLE_TS": 0.0,
            "_QQFARM_KERNEL_POOL_GUARD_ACTIVE": False,
            "_QQFARM_KERNEL_POOL_LAST_BYTES": 0,
            "_QQFARM_KERNEL_POOL_SAMPLE_INTERVAL": 0.0,
            "_qqfarm_kernel_pool_sample": lambda: next(samples),
            "_throttled_write": lambda *args, **kwargs: events.append(args),
        })
        self.assertFalse(namespace["_qqfarm_kernel_pool_guard"](now=1.0))
        self.assertTrue(namespace["_qqfarm_kernel_pool_guard"](now=2.0))
        self.assertTrue(namespace["_QQFARM_KERNEL_POOL_GUARD_ACTIVE"])
        # The latch remains active even if a later sample is healthy.
        self.assertTrue(namespace["_qqfarm_kernel_pool_guard"](now=3.0))
        self.assertTrue(events)


if __name__ == "__main__":
    unittest.main()
