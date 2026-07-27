import os
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTABLE = ROOT / "portable"
sys.path.insert(0, str(PORTABLE))


class ResourceLimitsTests(unittest.TestCase):
    def setUp(self):
        for name in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "OPENCV_FOR_THREADS_NUM",
            "ORT_INTRA_OP_NUM_THREADS", "ORT_INTER_OP_NUM_THREADS",
        ):
            os.environ.pop(name, None)

    def test_configure_environment_caps_native_worker_pools(self):
        import resource_limits

        applied = resource_limits.configure_environment(max_threads=2)

        self.assertEqual("2", os.environ["OMP_NUM_THREADS"])
        self.assertEqual("2", os.environ["OPENBLAS_NUM_THREADS"])
        self.assertEqual("2", os.environ["MKL_NUM_THREADS"])
        self.assertEqual("2", os.environ["OPENCV_FOR_THREADS_NUM"])
        self.assertEqual("2", os.environ["ORT_INTRA_OP_NUM_THREADS"])
        self.assertEqual("1", os.environ["ORT_INTER_OP_NUM_THREADS"])
        self.assertIn("OMP_NUM_THREADS", applied)

    def test_existing_user_thread_limit_is_preserved_when_lower(self):
        import resource_limits
        os.environ["OMP_NUM_THREADS"] = "1"

        resource_limits.configure_environment(max_threads=2)

        self.assertEqual("1", os.environ["OMP_NUM_THREADS"])

    def test_patch_loaded_cv2_caps_opencv_threads(self):
        import resource_limits
        calls = []
        fake = types.SimpleNamespace(setNumThreads=lambda n: calls.append(n))

        changed = resource_limits.patch_loaded_modules({"cv2": fake}, max_threads=2)

        self.assertEqual([2], calls)
        self.assertIn("cv2", changed)

    def test_apply_process_limits_sets_current_process_affinity_and_priority(self):
        import resource_limits

        class FakeKernel32:
            def __init__(self):
                self.affinity = None
                self.priority = None
            def GetCurrentProcess(self):
                return 123
            def SetProcessAffinityMask(self, handle, mask):
                self.affinity = (handle, mask)
                return 1
            def SetPriorityClass(self, handle, priority):
                self.priority = (handle, priority)
                return 1

        fake = FakeKernel32()
        result = resource_limits.apply_process_limits(affinity_cores=4, kernel32=fake)

        self.assertEqual((123, 0b1111), fake.affinity)
        self.assertEqual((123, resource_limits.BELOW_NORMAL_PRIORITY_CLASS), fake.priority)
        self.assertTrue(result["affinity"])
        self.assertTrue(result["priority"])
    def test_apply_process_limits_degrades_when_native_backend_is_missing(self):
        import resource_limits

        def missing_backend():
            raise ModuleNotFoundError("No module named 'ctypes'")

        result = resource_limits.apply_process_limits(
            affinity_cores=4, kernel32_loader=missing_backend
        )

        self.assertFalse(result["affinity"])
        self.assertFalse(result["priority"])
        self.assertEqual(0b1111, result["mask"])
        self.assertIn("ctypes", result["error"])

    def test_launcher_exports_native_thread_caps_before_starting_app(self):
        text = (PORTABLE / "launcher.ps1").read_text(encoding="utf-8-sig")
        for name in (
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "OPENCV_FOR_THREADS_NUM",
            "ORT_INTRA_OP_NUM_THREADS", "ORT_INTER_OP_NUM_THREADS",
        ):
            self.assertIn(name, text)
        self.assertIn("function Set-AssistantProcessLimits", text)
        self.assertIn("ProcessorAffinity", text)
        self.assertIn("PriorityClass", text)
        self.assertIn("BelowNormal", text)
        self.assertIn("resource_control.log", text)
        self.assertIn("Start-Process -FilePath $Exe -WorkingDirectory $AppDir -PassThru", text)
        self.assertIn("Set-AssistantProcessLimits $assistantProcess", text)
        self.assertNotIn("Start-Process -FilePath $Exe -WorkingDirectory $AppDir -PassThru -Wait", text)


if __name__ == "__main__":
    unittest.main()
