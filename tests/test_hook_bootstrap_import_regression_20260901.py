import ast
import builtins
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"


def _bootstrap_import_try_node():
    tree = ast.parse(HOOK.read_text(encoding="utf-8-sig"), filename=str(HOOK))
    for node in tree.body:
        if not isinstance(node, ast.Try):
            continue
        for child in node.body:
            if isinstance(child, ast.Import) and any(
                alias.name == "sys" for alias in child.names
            ):
                return node
    raise AssertionError("hook.py bootstrap import block was not found")


class HookBootstrapImportRegressionTests(unittest.TestCase):
    def test_bootstrap_survives_runtime_without_threading_module(self):
        """The embedded proxy loads the hook before threading is available."""
        node = _bootstrap_import_try_node()

        real_import = builtins.__import__

        def restricted_import(name, *args, **kwargs):
            if name == "threading":
                raise ModuleNotFoundError("No module named 'threading'")
            return real_import(name, *args, **kwargs)

        namespace = {
            "__builtins__": dict(vars(builtins), __import__=restricted_import),
            "_write": lambda *_args, **_kwargs: None,
        }

        # This is the actual early-startup contract: a missing threading module
        # must not abort hook loading before the packaged runtime is initialized.
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(HOOK), "exec"), namespace)


if __name__ == "__main__":
    unittest.main()
