import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "portable" / "launcher.ps1"
START_CMD = next((ROOT / "portable").glob("*.cmd"))
START_VBS = ROOT / "portable" / "StartFarmAssistant.vbs"


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

    def test_launcher_keeps_user_settings_out_of_its_source_edits(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertNotIn("Disable-CloseReopenPeriodicRestart", text)
        self.assertNotIn("Disable-PeriodicRestartJson", text)
        self.assertNotIn("enable_periodic_restart = False", text)
        self.assertIn("Initialize-PortableProfile", text)
        self.assertNotIn("Sync-LegacyUserConfig", text)
        self.assertNotIn("Sync-NewerFiles", text)

    def test_launcher_redirects_child_appdata_to_portable_windows_profile_without_reverse_sync(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("$HostLocalAppData = $env:LOCALAPPDATA", text)
        self.assertIn("$HostAppData = $env:APPDATA", text)
        self.assertIn("$PortableProfileRoot = Join-Path $PortableRoot 'WindowsProfile'", text)
        self.assertIn("$PortableLocalAppData = Join-Path $PortableProfileRoot 'LocalAppData'", text)
        self.assertIn("$PortableAppData = Join-Path $PortableProfileRoot 'RoamingAppData'", text)
        self.assertIn("$env:LOCALAPPDATA = $PortableLocalAppData", text)
        self.assertIn("$env:APPDATA = $PortableAppData", text)
        self.assertIn("$MigrationMarker = Join-Path $PortableProfileRoot 'migration-v1.complete'", text)
        self.assertNotIn("Sync-NewerFiles $LegacyProfile $HostLegacyProfile", text)
        self.assertNotIn("Sync-NewerFiles $CurrentProfile $HostCurrentProfile", text)
        self.assertNotIn("Copy-Item -LiteralPath $LegacyProfileConfig -Destination $HostLegacyConfig", text)
        self.assertNotIn("Remove-Utf8BomFromConfig -Path $HostLegacyConfig", text)

    def test_launcher_redirects_temp_files_to_the_portable_windows_profile(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("$PortableTemp = Join-Path $PortableProfileRoot 'Temp'", text)
        self.assertIn("$PortableTemp", text[text.index("New-Item -ItemType Directory -Force -Path"):])
        self.assertIn("$env:TEMP = $PortableTemp", text)
        self.assertIn("$env:TMP = $PortableTemp", text)

    def test_portable_initial_migration_keeps_host_config_byte_exact_and_never_reimports_after_marker(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        required_functions = (
            "Test-ExcludedRelativePath",
            "Import-MissingProfileFiles",
            "Remove-Utf8BomFromConfig",
            "Import-MostRecentFile",
            "Initialize-PortableConfiguration",
            "Initialize-PortableProfile",
        )
        function_text = "\n\n".join(
            extract_powershell_function(text, name) for name in required_functions
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            host_legacy = root / "host-local" / "qq-farm-bot-rev"
            host_current = root / "host-roaming" / "QQFarmCopilot"
            previous_legacy = root / "previous-portable" / "legacy-qq-farm-bot-rev"
            previous_current = root / "previous-portable" / "QQFarmCopilot"
            portable_legacy = root / "portable-profile" / "LocalAppData" / "qq-farm-bot-rev"
            portable_current = root / "portable-profile" / "RoamingAppData" / "QQFarmCopilot"
            marker = root / "portable-profile" / "migration-v1.complete"
            host_legacy.mkdir(parents=True)
            host_current.mkdir(parents=True)
            previous_legacy.mkdir(parents=True)
            previous_current.mkdir(parents=True)
            portable_legacy.mkdir(parents=True)
            portable_current.mkdir(parents=True)

            host_config_bytes = (
                b"\xef\xbb\xbf[instance.1.bot]\r\n"
                b"enable_rest_window = False\r\n"
                b"[instance.1.planting]\r\nplayer_level = 121\r\n"
            )
            host_config = host_legacy / "config-multi.ini"
            host_config.write_bytes(host_config_bytes)
            (previous_legacy / "config-multi.ini").write_text(
                "[instance.1.bot]\nenable_rest_window = True\n",
                encoding="utf-8",
            )
            (portable_legacy / "config-multi.ini").write_text(
                "[instance.1.bot]\nenable_rest_window = True\n",
                encoding="utf-8",
            )
            (host_legacy / "daily_flow_status.json").write_text('{"source":"host"}', encoding="utf-8")
            newest_daily = previous_current / "daily_flow_status.json"
            newest_daily.write_text('{"source":"previous-portable"}', encoding="utf-8")
            newest_time = newest_daily.stat().st_mtime + 60
            import os
            os.utime(newest_daily, (newest_time, newest_time))

            def escape(value):
                return str(value).replace("'", "''")

            command = (
                function_text
                + "\n$first = Initialize-PortableProfile"
                + " -HostLegacyProfile '" + escape(host_legacy) + "'"
                + " -HostCurrentProfile '" + escape(host_current) + "'"
                + " -PreviousLegacyProfile '" + escape(previous_legacy) + "'"
                + " -PreviousCurrentProfile '" + escape(previous_current) + "'"
                + " -LegacyProfile '" + escape(portable_legacy) + "'"
                + " -CurrentProfile '" + escape(portable_current) + "'"
                + " -MigrationMarker '" + escape(marker) + "'"
                + "; Write-Output ('first=' + $first)"
            )
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
            self.assertIn("first=True", completed.stdout)
            self.assertEqual(host_config_bytes, host_config.read_bytes())
            self.assertEqual(host_config_bytes[3:], (portable_legacy / "config-multi.ini").read_bytes())
            self.assertEqual('{"source":"previous-portable"}', (portable_current / "daily_flow_status.json").read_text(encoding="utf-8"))
            self.assertTrue(marker.is_file())

            host_config.write_bytes(b"[instance.1.bot]\r\nenable_rest_window = True\r\n")
            second_command = (
                function_text
                + "\n$second = Initialize-PortableProfile"
                + " -HostLegacyProfile '" + escape(host_legacy) + "'"
                + " -HostCurrentProfile '" + escape(host_current) + "'"
                + " -PreviousLegacyProfile '" + escape(previous_legacy) + "'"
                + " -PreviousCurrentProfile '" + escape(previous_current) + "'"
                + " -LegacyProfile '" + escape(portable_legacy) + "'"
                + " -CurrentProfile '" + escape(portable_current) + "'"
                + " -MigrationMarker '" + escape(marker) + "'"
                + "; Write-Output ('second=' + $second)"
            )
            completed = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", second_command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
            self.assertIn("second=False", completed.stdout)
            self.assertEqual(host_config_bytes[3:], (portable_legacy / "config-multi.ini").read_bytes())

    def test_config_encoding_normalizer_removes_only_utf8_bom(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        function_text = extract_powershell_function(text, "Remove-Utf8BomFromConfig")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config-multi.ini"
            content = "[planting]\r\npreferred_crop = ???\r\nplayer_level = 121\r\n".encode("utf-8")
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

    def test_vbs_one_click_entry_exists_and_explains_a_missing_launcher(self):
        self.assertTrue(START_VBS.is_file(), "missing one-click VBS entry")
        text = START_VBS.read_text(encoding="utf-8-sig")
        self.assertIn("--check", text)
        self.assertIn("launcher.ps1", text)
        self.assertIn("Launcher not found", text)
        self.assertIn("shell.Run commandLine, 0, False", text)

    def test_vbs_check_mode_executes_without_a_script_parse_error(self):
        completed = subprocess.run(
            ["cscript.exe", "//nologo", str(START_VBS), "--check"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        self.assertIn("one-click launcher parsed", completed.stdout)

    def test_vbs_builds_a_single_quoted_launcher_path(self):
        text = START_VBS.read_text(encoding="utf-8-sig")
        instrumented = text.replace(
            "shell.Run commandLine, 0, False",
            "WScript.Echo commandLine\nWScript.Quit 0",
            1,
        )
        self.assertNotEqual(text, instrumented)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            script_path = temp_root / "StartFarmAssistant.vbs"
            launcher_path = temp_root / "launcher.ps1"
            script_path.write_text(instrumented, encoding="utf-8")
            launcher_path.write_text("# launcher fixture\n", encoding="utf-8")
            completed = subprocess.run(
                ["cscript.exe", "//nologo", str(script_path)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        expected = (
            "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass "
            f'-File "{launcher_path}"'
        )
        self.assertEqual(expected, completed.stdout.strip())

    def test_cmd_starts_powershell_hidden(self):
        text = START_CMD.read_text(encoding="utf-8-sig")
        self.assertIn("-WindowStyle Hidden", text)
        self.assertIn("launcher.ps1", text)

    def test_runtime_logs_and_daily_state_stay_under_the_portable_app_directory(self):
        text = LAUNCHER.read_text(encoding="utf-8-sig")
        self.assertIn("$HookLogDir = Join-Path $AppDir 'logs'", text)
        self.assertIn("$LogDir, $HookLogDir, $PortableProfileRoot", text)
        self.assertIn("$env:QQFARM_HOOK_LOG_PATH = Join-Path $HookLogDir 'hook_runtime_log.txt'", text)
        self.assertIn(
            "$env:QQFARM_DAILY_FLOW_STATUS_PATH = Join-Path $CurrentProfile 'daily_flow_status.json'",
            text,
        )
        self.assertIn(
            "$env:QQFARM_DAILY_COUNTERS_PATH = Join-Path $CurrentProfile 'daily_counters.json'",
            text,
        )
        self.assertNotIn("$HookLogDir = Join-Path $env:LOCALAPPDATA", text)
        self.assertNotIn("$CurrentPortable", text)


if __name__ == "__main__":
    unittest.main()
