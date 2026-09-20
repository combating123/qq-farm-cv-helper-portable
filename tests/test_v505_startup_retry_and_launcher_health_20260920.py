import subprocess
import re
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
LAUNCHER = ROOT / "portable" / "launcher.ps1"


def load_hook_functions(*names):
    lines = HOOK.read_text(encoding="utf-8-sig").splitlines()
    wanted = set(names)
    blocks = []
    for name in names:
        assignment = next(
            (line for line in lines if line.startswith(name + " =")),
            None,
        )
        if assignment is not None:
            blocks.append(assignment)
            continue
        marker = f"def {name}("
        start = next(
            (index for index, line in enumerate(lines) if line.startswith(marker)),
            None,
        )
        if start is None:
            continue
        end = len(lines)
        for index in range(start + 1, len(lines)):
            line = lines[index]
            if line and not line[0].isspace() and not line.startswith("#"):
                end = index
                break
        blocks.append("\n".join(lines[start:end]))
    namespace = {}
    exec(compile("\n\n".join(blocks), str(HOOK), "exec"), namespace)
    return namespace


def extract_powershell_function(text, name):
    marker = f"function {name}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"missing PowerShell function: {name}")
    brace = text.find("{", start)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError(f"unterminated PowerShell function: {name}")


def call_powershell_function(name, *args):
    text = LAUNCHER.read_text(encoding="utf-8-sig")
    function_text = extract_powershell_function(text, name)
    command = function_text + "\n" + name + " " + " ".join(map(str, args))
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr or completed.stdout)
    return completed.stdout.strip().splitlines()[-1]


class StartRetryRegressionTests(unittest.TestCase):
    def test_failed_native_start_releases_debounce_for_a_real_retry(self):
        namespace = load_hook_functions(
            "_qqfarm_start_request_has_runtime_evidence",
            "_wrap_start_debounce_method",
        )
        namespace["time"] = types.SimpleNamespace(time=lambda: 100.0)
        namespace["_START_DEBOUNCE_SECONDS"] = 15.0
        namespace["_start_debounce_log"] = lambda *_args, **_kwargs: None

        calls = []

        def failed_start(owner):
            calls.append(owner)
            return None

        wrapped, patched = namespace["_wrap_start_debounce_method"](failed_start)
        self.assertTrue(patched)
        owner = types.SimpleNamespace(
            running=False,
            bot_running=False,
            _instance_runtime_ui_state={
                "1": {"running": False, "starting": False, "stopping": False}
            },
        )

        self.assertIsNone(wrapped(owner))
        self.assertEqual(0.0, getattr(owner, "_qqfarm_last_start_request_ts", 0.0))
        self.assertIsNone(wrapped(owner))
        self.assertEqual(2, len(calls))

    def test_async_native_start_keeps_debounce_while_runtime_is_starting(self):
        namespace = load_hook_functions(
            "_qqfarm_start_request_has_runtime_evidence",
            "_wrap_start_debounce_method",
        )
        namespace["time"] = types.SimpleNamespace(time=lambda: 100.0)
        namespace["_START_DEBOUNCE_SECONDS"] = 15.0
        namespace["_start_debounce_log"] = lambda *_args, **_kwargs: None
        calls = []

        def starting(owner):
            calls.append(owner)
            owner._instance_runtime_ui_state["1"]["starting"] = True
            return None

        wrapped, _patched = namespace["_wrap_start_debounce_method"](starting)
        owner = types.SimpleNamespace(
            running=False,
            bot_running=False,
            _instance_runtime_ui_state={
                "1": {"running": False, "starting": False, "stopping": False}
            },
        )

        self.assertIsNone(wrapped(owner))
        self.assertEqual(100.0, owner._qqfarm_last_start_request_ts)
        self.assertFalse(wrapped(owner))
        self.assertEqual(1, len(calls))

    def test_qt_autostart_retries_when_first_click_did_not_enter_starting_state(self):
        namespace = load_hook_functions(
            "_QT_AUTOSTART_CLICKED",
            "_QT_AUTOSTART_ATTEMPTS",
            "_QT_AUTOSTART_LAST_ATTEMPT_TS",
            "_QT_AUTOSTART_COOLDOWN_UNTIL",
            "_QT_AUTOSTART_MAX_ATTEMPTS",
            "_QT_AUTOSTART_RETRY_SECONDS",
            "_qt_runtime_already_running",
            "_qt_autostart_running_button",
        )
        namespace["time"] = types.SimpleNamespace(monotonic=lambda: 0.0)
        namespace["_QT_AUTOSTART_RETRY_SECONDS"] = 0.0
        namespace["_QT_AUTOSTART_MAX_ATTEMPTS"] = 3
        namespace["_write"] = lambda *_args, **_kwargs: None

        runtime = types.SimpleNamespace(
            bot_running=False,
            _instance_runtime_ui_state={
                "1": {"running": False, "starting": False, "stopping": False}
            },
        )

        class StartButton:
            def __init__(self):
                self.clicks = 0

            def text(self):
                return "开始运行"

            def isEnabled(self):
                return True

            def isVisible(self):
                return True

            def click(self):
                self.clicks += 1
                if self.clicks == 2:
                    runtime._instance_runtime_ui_state["1"]["starting"] = True

        button = StartButton()
        app = types.SimpleNamespace(allWidgets=lambda: [runtime, button])

        self.assertTrue(namespace["_qt_autostart_running_button"](app))
        self.assertTrue(namespace["_qt_autostart_running_button"](app))
        self.assertEqual(2, button.clicks)

    def test_stale_qt_starting_latch_is_cleared_and_disabled_start_is_reenabled(self):
        namespace = load_hook_functions(
            "_QT_STARTING_STALE_SECONDS",
            "_qqfarm_clear_stale_qt_starting_state",
            "_qqfarm_reenable_start_without_window",
        )
        namespace["_QT_STARTING_STALE_SECONDS"] = 20.0
        namespace["_active_is_qq_mode"] = lambda: True
        namespace["_qt_runtime_already_running"] = lambda _app: False

        class StartButton:
            def __init__(self):
                self.enabled = False

            def text(self):
                return "开始运行"

            def isVisible(self):
                return True

            def isEnabled(self):
                return self.enabled

            def setEnabled(self, value):
                self.enabled = bool(value)

            def setDisabled(self, value):
                self.enabled = not bool(value)

        button = StartButton()
        state = {"running": False, "starting": True, "stopping": True, "started_at": 80.0}
        app = types.SimpleNamespace(
            allWidgets=lambda: [
                types.SimpleNamespace(_instance_runtime_ui_state={"1": state}),
                button,
            ]
        )

        self.assertEqual(
            1,
            namespace["_qqfarm_clear_stale_qt_starting_state"](app, now=100.0),
        )
        self.assertFalse(state["starting"])
        self.assertFalse(state["stopping"])
        self.assertEqual(1, namespace["_qqfarm_reenable_start_without_window"](app))
        self.assertTrue(button.enabled)


class LauncherHealthRegressionTests(unittest.TestCase):
    def test_slow_qt_bootstrap_keeps_existing_process_for_five_minutes(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        health = extract_powershell_function(
            text,
            "Test-AssistantInstanceHealthy",
        )
        match = re.search(
            r"\[int\]\$StartupGraceSeconds\s*=\s*(\d+)",
            health,
        )
        self.assertIsNotNone(match)
        startup_grace_seconds = int(match.group(1))

        self.assertGreaterEqual(startup_grace_seconds, 300)
        self.assertLess(120, startup_grace_seconds)
        self.assertIn("$ageSeconds -lt $StartupGraceSeconds", health)

    def test_stale_existing_process_is_restarted_by_default_launch(self):
        self.assertEqual(
            "restart-stale",
            call_powershell_function("Get-ExistingAssistantInstanceAction", 1, 0, 0),
        )

    def test_clr_crash_code_is_recoverable(self):
        self.assertEqual(
            "restart",
            call_powershell_function("Get-AssistantExitDisposition", -532462766),
        )

    def test_launcher_contains_health_probe_before_preserving_existing_process(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("function Test-AssistantInstanceHealthy", text)
        self.assertIn("-ExistingHealthy", text)
        self.assertIn("Test-AssistantInstanceHealthy", text[text.index("$existingAssistantInstances"):])

    def test_clock_bridged_child_uses_supervisor_age_for_startup_grace(self):
        self.assertEqual(
            "5",
            call_powershell_function(
                "Get-AssistantEffectiveAgeSeconds",
                2678400,
                5,
            ),
        )
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        health = extract_powershell_function(
            text,
            "Test-AssistantInstanceHealthy",
        )
        self.assertIn("Get-AssistantSupervisorAgeSeconds", health)
        self.assertIn("Get-AssistantEffectiveAgeSeconds", health)


class CaptureRetryRegressionTests(unittest.TestCase):
    def test_visible_capture_has_one_bounded_retry_before_native_fallback(self):
        namespace = load_hook_functions("_get_frame_from_bot")
        frames = [None, "fresh-frame"]
        calls = []

        def visible_capture(*_args, **_kwargs):
            calls.append("visible")
            return frames.pop(0) if frames else None

        namespace.update({
            "_active_is_qq_mode": lambda: True,
            "_active_is_weixin_mode": lambda: False,
            "_qqfarm_capture_visible_farm_frame": visible_capture,
            "_qqfarm_prepare_visible_frame_for_business": lambda frame: frame,
            "_qqfarm_visible_capture_frame_is_trusted": lambda frame: frame == "fresh-frame",
            "_qqfarm_visible_frame_has_farm_scene": lambda frame: frame == "fresh-frame",
            "_qqfarm_native_capture_fallback_allowed": lambda: False,
            "_qqfarm_recent_good_capture_frame": lambda: None,
        })

        result = namespace["_get_frame_from_bot"](types.SimpleNamespace())
        self.assertEqual("fresh-frame", result)
        self.assertEqual(["visible", "visible"], calls)


if __name__ == "__main__":
    unittest.main()
