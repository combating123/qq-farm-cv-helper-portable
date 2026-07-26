# Native worker-pool limits for the embedded CV/OCR runtime.
# This module intentionally uses only the standard library so it can run before
# numpy, OpenCV and ONNX Runtime are imported.
import os

_PATCHED_MODULE_IDS = set()

BELOW_NORMAL_PRIORITY_CLASS = 0x00004000


def apply_process_limits(affinity_cores=4, kernel32=None):
    if kernel32 is None:
        if os.name != "nt":
            return {"affinity": False, "priority": False, "mask": 0}
        import ctypes
        kernel32 = ctypes.windll.kernel32
    available = max(1, int(os.cpu_count() or 1))
    affinity_cores = max(1, min(int(affinity_cores), available))
    mask = (1 << affinity_cores) - 1
    handle = kernel32.GetCurrentProcess()
    affinity_ok = bool(kernel32.SetProcessAffinityMask(handle, mask))
    priority_ok = bool(kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS))
    return {"affinity": affinity_ok, "priority": priority_ok, "mask": mask}

def _bounded_env(name, desired):
    current = os.environ.get(name)
    try:
        if current is not None and int(current) <= int(desired):
            return False
    except (TypeError, ValueError):
        pass
    os.environ[name] = str(int(desired))
    return True


def configure_environment(max_threads=2):
    max_threads = max(1, int(max_threads))
    applied = []
    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "OPENCV_FOR_THREADS_NUM",
        "ORT_INTRA_OP_NUM_THREADS",
    ):
        if _bounded_env(name, max_threads):
            applied.append(name)
    if _bounded_env("ORT_INTER_OP_NUM_THREADS", 1):
        applied.append("ORT_INTER_OP_NUM_THREADS")
    os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
    return applied


def patch_loaded_modules(modules, max_threads=2):
    changed = []
    cv2_module = modules.get("cv2") if modules else None
    if cv2_module is not None and id(cv2_module) not in _PATCHED_MODULE_IDS:
        setter = getattr(cv2_module, "setNumThreads", None)
        if callable(setter):
            setter(max(1, int(max_threads)))
            _PATCHED_MODULE_IDS.add(id(cv2_module))
            changed.append("cv2")
    return changed
