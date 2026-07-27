import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "portable" / "launcher.ps1"
START_CMD = next((ROOT / "portable").glob("*.cmd"))


def extract_powershell_function(text, name):
    marker = f"function {name}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"missing PowerShell function: {name}")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"missing opening brace for: {name}")
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError(f"missing closing brace for: {name}")


def call_powershell_function(name, *args):
    text = LAUNCHER.read_text(encoding="utf-8-sig")
    function_text = extract_powershell_function(text, name)
    argument_text = " ".join(str(value) for value in args)
    command = function_text + "\n" + f"{name} {argument_text}"
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


class LauncherStabilityTests(unittest.TestCase):
    def test_launcher_forces_close_reopen_periodic_restart_off(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("Disable-CloseReopenPeriodicRestart", text)
        self.assertIn("enable_periodic_restart = False", text)
        self.assertIn(
            "Disable-CloseReopenPeriodicRestart (Join-Path $LegacyProfile 'config-multi.ini')",
            text,
        )
        self.assertIn(
            "Disable-CloseReopenPeriodicRestart (Join-Path $LegacyPortable 'config-multi.ini')",
            text,
        )
        self.assertIn(
            r"Disable-PeriodicRestartJson (Join-Path $CurrentProfile 'instances\default\configs\config.json')",
            text,
        )
        self.assertIn(
            r"Disable-PeriodicRestartJson (Join-Path $CurrentPortable 'instances\default\configs\config.json')",
            text,
        )

    def test_periodic_restart_json_function_disables_restart_task(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        function_text = extract_powershell_function(text, "Disable-PeriodicRestartJson")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps({"tasks": {"restart": {"enabled": True}}}),
                encoding="utf-8",
            )
            escaped = str(config_path).replace("'", "''")
            command = (
                function_text
                + "\nDisable-PeriodicRestartJson -ConfigPath '"
                + escaped
                + "'"
            )
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
            data = json.loads(config_path.read_text(encoding="utf-8-sig"))
            self.assertFalse(data["tasks"]["restart"]["enabled"])

    def test_known_native_faults_are_restartable(self):
        self.assertEqual("restart", call_powershell_function("Get-AssistantExitDisposition", -1073741819))
        self.assertEqual("restart", call_powershell_function("Get-AssistantExitDisposition", -1073740791))

    def test_normal_user_and_unknown_exits_stop_supervision(self):
        self.assertEqual("stop", call_powershell_function("Get-AssistantExitDisposition", 0))
        self.assertEqual("stop", call_powershell_function("Get-AssistantExitDisposition", -1))
        self.assertEqual("stop", call_powershell_function("Get-AssistantExitDisposition", 1))

    def test_crash_burst_uses_short_retries_then_cooldown(self):
        self.assertEqual("10", call_powershell_function("Get-AssistantRestartDelaySeconds", 1))
        self.assertEqual("30", call_powershell_function("Get-AssistantRestartDelaySeconds", 2))
        self.assertEqual("300", call_powershell_function("Get-AssistantRestartDelaySeconds", 3))

    def test_launcher_waits_logs_and_reapplies_limits_for_each_process(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("$RecoverableCrashBurstLimit = 3", text)
        self.assertIn("$StableRuntimeResetSeconds = 600", text)
        self.assertIn("$CrashCooldownSeconds = 300", text)
        self.assertIn("while ($true)", text)
        self.assertIn("$assistantProcess.WaitForExit()", text)
        self.assertIn("Set-AssistantProcessLimits $assistantProcess", text)
        self.assertIn("watchdog.log", text)
        self.assertIn("pid=", text)
        self.assertIn("exitCode=", text)
        self.assertIn("runtimeSeconds=", text)
        self.assertIn("recoverable_native_crash", text)
        self.assertIn("controlled_or_unclassified_exit", text)

    def test_elevated_launcher_is_hidden_and_does_not_wait_for_supervisor_child(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        elevated = text[text.index("Start-Process -FilePath 'powershell.exe' -Verb RunAs"):text.index("$AppDir =")]
        self.assertIn("-WindowStyle Hidden", elevated)
        self.assertNotIn("-Wait", elevated)

    def test_cmd_starts_powershell_hidden(self):
        text = START_CMD.read_text(encoding="utf-8-sig")
        self.assertIn("-WindowStyle Hidden", text)
        self.assertIn("launcher.ps1", text)

    def test_hook_log_uses_ascii_localappdata_path_instead_of_chinese_install_path(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn(r"$HookLogDir = Join-Path $env:LOCALAPPDATA 'qq-farm-bot-rev\logs'", text)
        self.assertIn("New-Item -ItemType Directory -Force -Path $LogDir,$HookLogDir", text)
        self.assertIn("$env:QQFARM_HOOK_LOG_PATH = Join-Path $HookLogDir 'hook_runtime_log.txt'", text)
        self.assertNotIn("$env:QQFARM_HOOK_LOG_PATH = Join-Path $LogDir 'hook_runtime_log.txt'", text)


if __name__ == "__main__":
    unittest.main()
