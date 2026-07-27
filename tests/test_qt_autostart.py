import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'portable' / 'hook.py'


def load_autostart():
    source = HOOK.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(HOOK))
    names = {'_qt_runtime_already_running', '_qt_autostart_running_button'}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == '_QT_AUTOSTART_CLICKED'
            for t in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {'_write': lambda *a, **k: None}
    exec(compile(module, str(HOOK), 'exec'), namespace)
    return namespace


class Button:
    def __init__(self, text, enabled=True, visible=True):
        self._text = text
        self._enabled = enabled
        self._visible = visible
        self.clicks = 0

    def text(self):
        return self._text

    def isEnabled(self):
        return self._enabled

    def isVisible(self):
        return self._visible

    def click(self):
        self.clicks += 1


class RuntimeWindow:
    def __init__(self, running):
        self.bot_running = running
        self._instance_runtime_ui_state = {
            '1': {'running': running, 'starting': False, 'stopping': False}
        }


class App:
    def __init__(self, widgets):
        self._widgets = widgets

    def allWidgets(self):
        return list(self._widgets)

    def topLevelWidgets(self):
        return list(self._widgets)


class QtAutostartTests(unittest.TestCase):
    def test_clicks_exact_visible_enabled_start_button_only_once(self):
        ns = load_autostart()
        wrong = Button('\u5f00\u59cb\u5206\u4eab')
        start = Button('\u5f00\u59cb\u8fd0\u884c')
        app = App([wrong, start])
        self.assertTrue(ns['_qt_autostart_running_button'](app))
        self.assertEqual(0, wrong.clicks)
        self.assertEqual(1, start.clicks)
        self.assertFalse(ns['_qt_autostart_running_button'](app))
        self.assertEqual(1, start.clicks)

    def test_does_not_click_start_when_runtime_is_already_running(self):
        ns = load_autostart()
        runtime = RuntimeWindow(True)
        start = Button('\u5f00\u59cb\u8fd0\u884c')
        app = App([runtime, start])

        self.assertFalse(ns['_qt_autostart_running_button'](app))
        self.assertEqual(0, start.clicks)
        self.assertTrue(ns['_QT_AUTOSTART_CLICKED'])


if __name__ == '__main__':
    unittest.main()
