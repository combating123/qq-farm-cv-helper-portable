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
    def test_launcher_file_parses_in_windows_powershell(self):
        launcher_escaped = str(LAUNCHER).replace("'", "''")
        command = (
            "$tokens=$null; $errors=$null; "
            f"[void][System.Management.Automation.Language.Parser]::ParseFile('{launcher_escaped}', [ref]$tokens, [ref]$errors); "
            "if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
        )
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)

    def test_launcher_does_not_rewrite_user_settings(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertNotIn("Disable-CloseReopenPeriodicRestart", text)
        self.assertNotIn("Disable-PeriodicRestartJson", text)
        self.assertNotIn("enable_periodic_restart = False", text)
        self.assertIn("Sync-LegacyUserConfig", text)

    def test_generic_profile_sync_excludes_legacy_user_config(self):
        self.assertEqual(
            "True",
            call_powershell_function("Test-ExcludedRelativePath", "config-multi.ini"),
        )

    def test_config_encoding_normalizer_removes_only_utf8_bom(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        function_text = extract_powershell_function(text, "Remove-Utf8BomFromConfig")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config-multi.ini"
            content = "[planting]\r\npreferred_crop = 金花茶\r\nplayer_level = 121\r\n".encode("utf-8")
            config_path.write_bytes(b"\xef\xbb\xbf" + content)
            escaped = str(config_path).replace("'", "''")
            command = function_text + "\nRemove-Utf8BomFromConfig -Path '" + escaped + "'"
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
            self.assertEqual(content, config_path.read_bytes())

    def test_launcher_normalizes_config_encoding_before_profile_sync(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        runtime = text[text.index("New-Item -ItemType Directory -Force -Path $LogDir,$HookLogDir"):]
        normalize_index = runtime.index("Remove-Utf8BomFromConfig -Path $LegacyProfileConfig")
        sync_index = runtime.index("Sync-LegacyUserConfig `")
        self.assertLess(normalize_index, sync_index)

    def test_legacy_user_config_sync_keeps_active_profile_authoritative_and_byte_exact(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        function_text = extract_powershell_function(text, "Sync-LegacyUserConfig")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active = root / "active.ini"
            portable = root / "portable.ini"
            active_bytes = (
                "[instance.1.bot]\r\nenable_rest_window = False\r\n"
                "[instance.1.planting]\r\npreferred_crop = 金花茶\r\n"
            ).encode("utf-8-sig")
            active.write_bytes(active_bytes)
            portable.write_text(
                "[instance.1.bot]\nenable_rest_window = True\n",
                encoding="utf-8",
            )
            active_escaped = str(active).replace("'", "''")
            portable_escaped = str(portable).replace("'", "''")
            command = (
                function_text
                + "\nSync-LegacyUserConfig -ProfileConfig '"
                + active_escaped
                + "' -PortableConfig '"
                + portable_escaped
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
            self.assertEqual(active_bytes, active.read_bytes())
            self.assertEqual(active_bytes, portable.read_bytes())

    def test_legacy_user_config_sync_restores_only_when_active_profile_is_missing(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        function_text = extract_powershell_function(text, "Sync-LegacyUserConfig")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active = root / "missing" / "active.ini"
            portable = root / "portable.ini"
            portable_bytes = (
                "[instance.1.bot]\r\nenable_rest_window = False\r\n"
            ).encode("utf-8-sig")
            portable.write_bytes(portable_bytes)
            active_escaped = str(active).replace("'", "''")
            portable_escaped = str(portable).replace("'", "''")
            command = (
                function_text
                + "\nSync-LegacyUserConfig -ProfileConfig '"
                + active_escaped
                + "' -PortableConfig '"
                + portable_escaped
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
            self.assertEqual(portable_bytes, active.read_bytes())

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
