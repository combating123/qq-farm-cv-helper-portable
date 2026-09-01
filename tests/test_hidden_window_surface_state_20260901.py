import ast
import ctypes
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class _FakeWin32Gui:
    def __init__(self, *, client_rect=(0, 0, 428, 800)):
        self.client_rect = client_rect

    def IsWindowVisible(self, _hwnd):
        return True

    def IsIconic(self, _hwnd):
        return False

    def GetWindowRect(self, _hwnd):
        # The real 150% case exposes a logical 428x800 rectangle here.
        return (5, 5, 433, 805)

    def GetClientRect(self, _hwnd):
        return self.client_rect


class _FakeUser32:
    def __init__(self, *, layered=False, alpha=255, cloaked=0):
        self.layered = layered
        self.alpha = alpha
        self.cloaked = cloaked

    def GetWindowLongPtrW(self, _hwnd, _index):
        return 0x00080000 if self.layered else 0

    def GetWindowLongW(self, hwnd, index):
        return self.GetWindowLongPtrW(hwnd, index)

    def GetLayeredWindowAttributes(self, _hwnd, _color, alpha_ptr, flags_ptr):
        ctypes.cast(alpha_ptr, ctypes.POINTER(ctypes.c_ubyte))[0] = self.alpha
        ctypes.cast(flags_ptr, ctypes.POINTER(ctypes.c_ulong))[0] = 0x00000002
        return 1


class _FakeDwmApi:
    def __init__(self, *, cloaked=0):
        self.cloaked = cloaked

    def DwmGetWindowAttribute(self, _hwnd, attribute, value_ptr, _size):
        if int(attribute) != 14:  # DWMWA_CLOAKED
            return 1
        ctypes.cast(value_ptr, ctypes.POINTER(ctypes.c_ulong))[0] = self.cloaked
        return 0


class HiddenWindowSurfaceStateTests(unittest.TestCase):
    def _invoke(self, *, win32gui, user32=None, dwmapi=None):
        namespace = load_functions("_qqfarm_farm_window_is_visible")
        namespace["_share_find_farm_window_hwnd"] = lambda: 591632
        modules = {"win32gui": win32gui}
        windll = types.SimpleNamespace()
        if user32 is not None:
            windll.user32 = user32
        if dwmapi is not None:
            windll.dwmapi = dwmapi
        with mock.patch.dict(sys.modules, modules), mock.patch.object(
            ctypes, "windll", windll, create=True
        ):
            return namespace["_qqfarm_farm_window_is_visible"]()

    def test_layered_alpha_zero_is_not_a_usable_visible_surface(self):
        self.assertFalse(self._invoke(
            win32gui=_FakeWin32Gui(),
            user32=_FakeUser32(layered=True, alpha=0),
            dwmapi=_FakeDwmApi(),
        ))

    def test_dwm_cloaked_surface_is_not_a_usable_visible_surface(self):
        self.assertFalse(self._invoke(
            win32gui=_FakeWin32Gui(),
            user32=_FakeUser32(),
            dwmapi=_FakeDwmApi(cloaked=1),
        ))

    def test_nonzero_layered_alpha_and_uncloaked_surface_remain_usable(self):
        self.assertTrue(self._invoke(
            win32gui=_FakeWin32Gui(),
            user32=_FakeUser32(layered=True, alpha=255),
            dwmapi=_FakeDwmApi(cloaked=0),
        ))

    def test_invalid_client_size_is_not_usable_even_when_outer_rect_is_large(self):
        self.assertFalse(self._invoke(
            win32gui=_FakeWin32Gui(client_rect=(0, 0, 100, 100)),
            user32=_FakeUser32(),
            dwmapi=_FakeDwmApi(),
        ))


if __name__ == "__main__":
    unittest.main()
