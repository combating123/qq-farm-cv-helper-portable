param([switch]$NoLaunch)
$ErrorActionPreference = 'Stop'

function Test-IsAdministrator {
    try {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($identity)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch {
        return $false
    }
}

# The main executable requests elevation. Elevate the launcher itself first so
# Start-Process -Wait supervises the real process instead of the UAC proxy.
if (!$NoLaunch -and !$env:QQFARM_LAUNCHER_ELEVATED -and !(Test-IsAdministrator)) {
    $escapedScriptPath = $PSCommandPath.Replace("'", "''")
    $elevatedCommand = "`$env:QQFARM_LAUNCHER_ELEVATED='1'; & '$escapedScriptPath'"
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($elevatedCommand))
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -WindowStyle Hidden -ArgumentList @(
        '-NoProfile', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encodedCommand
    ) | Out-Null
    exit 0
}
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PortableRoot = Join-Path $AppDir 'UserData'
$LegacyPortable = Join-Path $PortableRoot 'legacy-qq-farm-bot-rev'
$CurrentPortable = Join-Path $PortableRoot 'QQFarmCopilot'
$LegacyProfile = Join-Path $env:LOCALAPPDATA 'qq-farm-bot-rev'
$CurrentProfile = Join-Path $env:APPDATA 'QQFarmCopilot'
$LogDir = Join-Path $AppDir 'logs'
$HookLogDir = Join-Path $env:LOCALAPPDATA 'qq-farm-bot-rev\logs'
$Exe = Join-Path $AppDir 'QQFarmCVHelper.exe'
$ExcludedDirs = @('logs','models','screenshots','captures','cache','__pycache__','crash')

function Show-LauncherMessage([string]$Text, [int]$Icon = 64) {
    try {
        $shell = New-Object -ComObject WScript.Shell
        [void]$shell.Popup($Text, 0, 'QQ经典农场助手', $Icon)
    } catch {
        Write-Host $Text
    }
}

function Test-ExcludedRelativePath([string]$RelativePath) {
    $parts = $RelativePath -split '[\\/]'
    foreach ($part in $parts) {
        if ($ExcludedDirs -contains $part.ToLowerInvariant()) { return $true }
    }
    $name = [IO.Path]::GetFileName($RelativePath)
    if ($name -ieq 'config-multi.ini') { return $true }
    if ($name -like '*.log' -or $name -like '*.tmp' -or $name -like '*.bak*' -or $name -like '*.bad-*') { return $true }
    return $false
}

function Sync-NewerFiles([string]$Source, [string]$Destination) {
    if (!(Test-Path -LiteralPath $Source -PathType Container)) { return }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $prefixLength = $Source.TrimEnd('\').Length + 1
    Get-ChildItem -LiteralPath $Source -Recurse -File -Force | ForEach-Object {
        $relative = $_.FullName.Substring($prefixLength)
        if (Test-ExcludedRelativePath $relative) { return }
        $target = Join-Path $Destination $relative
        $copy = !(Test-Path -LiteralPath $target -PathType Leaf)
        if (!$copy) {
            $targetItem = Get-Item -LiteralPath $target
            $copy = $_.LastWriteTimeUtc -gt $targetItem.LastWriteTimeUtc.AddMilliseconds(500)
        }
        if ($copy) {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        }
    }
}

function Sync-LegacyUserConfig([string]$ProfileConfig, [string]$PortableConfig) {
    # config-multi.ini is never parsed or rewritten by the launcher. The active
    # profile is authoritative while it exists; Copy-Item preserves the exact
    # bytes/BOM and therefore cannot corrupt Chinese setting values.
    if (Test-Path -LiteralPath $ProfileConfig -PathType Leaf) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $PortableConfig) | Out-Null
        Copy-Item -LiteralPath $ProfileConfig -Destination $PortableConfig -Force
        return
    }
    if (Test-Path -LiteralPath $PortableConfig -PathType Leaf) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ProfileConfig) | Out-Null
        Copy-Item -LiteralPath $PortableConfig -Destination $ProfileConfig -Force
    }
}


function Remove-Utf8BomFromConfig([string]$Path) {
    # The packaged application reads config-multi.ini as plain UTF-8. A BOM is
    # interpreted as text before the first section header and makes the entire
    # file look malformed. Remove only those three marker bytes; every setting
    # byte after them stays unchanged.
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 3) { return $false }
    if ($bytes[0] -ne 0xEF -or $bytes[1] -ne 0xBB -or $bytes[2] -ne 0xBF) { return $false }
    $clean = New-Object byte[] ($bytes.Length - 3)
    [Array]::Copy($bytes, 3, $clean, 0, $clean.Length)
    [IO.File]::WriteAllBytes($Path, $clean)
    return $true
}


function Stop-ExistingAssistantInstances {
    $existing = @(Get-Process -Name 'QQFarmCVHelper' -ErrorAction SilentlyContinue)
    if ($existing.Count -eq 0) { return $true }

    # 检测到旧实例时直接尝试关闭；只有权限不足时才显示系统权限确认。

    foreach ($item in $existing) {
        try { [void]$item.CloseMainWindow() } catch {}
    }
    Start-Sleep -Milliseconds 1200

    $remaining = @($existing | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    if ($remaining.Count -eq 0) { return $true }

    foreach ($item in $remaining) {
        try { Stop-Process -Id $item.Id -Force -ErrorAction Stop } catch {}
    }
    Start-Sleep -Milliseconds 500
    $remaining = @($remaining | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    if ($remaining.Count -eq 0) { return $true }

    $pidList = ($remaining.Id -join ',')
    $killScript = "Stop-Process -Id $pidList -Force -ErrorAction Stop"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($killScript))
    try {
        $admin = Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList @(
            '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encoded
        ) -PassThru -Wait
        if ($admin.ExitCode -ne 0) { throw "管理员结束进程返回代码 $($admin.ExitCode)" }
    } catch {
        Show-LauncherMessage '旧实例仍在运行。请在权限确认窗口点击“是”，然后重新双击启动文件。' 48
        return $false
    }

    foreach ($item in $remaining) {
        Wait-Process -Id $item.Id -Timeout 10 -ErrorAction SilentlyContinue
    }
    $stillRunning = @($remaining | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    if ($stillRunning.Count -gt 0) {
        Show-LauncherMessage '旧实例仍未退出。请在任务管理器中结束 QQFarmCVHelper.exe 后重新启动。' 48
        return $false
    }
    return $true
}

function Set-AssistantProcessLimits([System.Diagnostics.Process]$Process) {
    $resourceLog = Join-Path $LogDir 'resource_control.log'
    try {
        if ($null -eq $Process) { throw 'assistant process handle is missing' }
        try { $requestedCores = [Math]::Max(1, [int]$env:QQFARM_CPU_AFFINITY_CORES) }
        catch { $requestedCores = 4 }
        $usableCores = [Math]::Min([Math]::Max(1, [Environment]::ProcessorCount), 63)
        $affinityCores = [Math]::Min($requestedCores, $usableCores)
        [uint64]$mask = 0
        for ($index = 0; $index -lt $affinityCores; $index++) {
            $mask = $mask -bor ([uint64]1 -shl $index)
        }
        $Process.ProcessorAffinity = [IntPtr][int64]$mask
        $Process.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal
        $Process.Refresh()
        Add-Content -LiteralPath $resourceLog -Encoding UTF8 -Value (
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' pid=' + $Process.Id +
            ' affinity=0x' + $mask.ToString('X') + ' cores=' + $affinityCores +
            ' priority=' + $Process.PriorityClass
        )
        return $true
    } catch {
        Add-Content -LiteralPath $resourceLog -Encoding UTF8 -Value (
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' pid=' + $Process.Id +
            ' resource-limit-error=' + $_.Exception.Message
        )
        return $false
    }
}


function Get-AssistantExitDisposition([int]$ExitCode) {
    # The observed native failures are STATUS_ACCESS_VIOLATION (0xC0000005)
    # and STATUS_STACK_BUFFER_OVERRUN / fail-fast (0xC0000409).
    $recoverableCrashCodes = @(-1073741819, -1073740791)
    if ($recoverableCrashCodes -contains $ExitCode) { return 'restart' }
    return 'stop'
}

function Get-AssistantRestartDelaySeconds([int]$ConsecutiveCrashCount) {
    if ($ConsecutiveCrashCount -ge 3) { return 300 }
    if ($ConsecutiveCrashCount -eq 2) { return 30 }
    return 10
}

function Write-WatchdogLog([string]$Message) {
    try {
        Add-Content -LiteralPath (Join-Path $LogDir 'watchdog.log') -Encoding UTF8 -Value (
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $Message
        )
    } catch {}
}

New-Item -ItemType Directory -Force -Path $LogDir,$HookLogDir,$LegacyPortable,$CurrentPortable | Out-Null
$LegacyProfileConfig = Join-Path $LegacyProfile 'config-multi.ini'
$LegacyPortableConfig = Join-Path $LegacyPortable 'config-multi.ini'
# Preserve all setting bytes while removing the UTF-8 BOM that the packaged
# application's plain UTF-8 parser treats as a malformed first section.
[void](Remove-Utf8BomFromConfig -Path $LegacyProfileConfig)
[void](Remove-Utf8BomFromConfig -Path $LegacyPortableConfig)
# Generic profile sync explicitly excludes config-multi.ini so timestamp
# ordering can never replace the active settings.
Sync-LegacyUserConfig `
    $LegacyProfileConfig `
    $LegacyPortableConfig
Sync-NewerFiles $LegacyProfile $LegacyPortable
Sync-NewerFiles $CurrentProfile $CurrentPortable
Sync-NewerFiles $LegacyPortable $LegacyProfile
Sync-NewerFiles $CurrentPortable $CurrentProfile

$env:QQFARM_HOOK_LOG_PATH = Join-Path $HookLogDir 'hook_runtime_log.txt'
$env:QQFARM_PROXY_LOG_PATH = Join-Path $LogDir 'proxy_dll_load.log'
$env:QQFARM_MAX_NATIVE_THREADS = '2'
$env:QQFARM_CPU_AFFINITY_CORES = '4'
# Cap native CV/OCR worker pools before the elevated executable starts.
$env:OMP_NUM_THREADS = '2'
$env:OPENBLAS_NUM_THREADS = '2'
$env:MKL_NUM_THREADS = '2'
$env:NUMEXPR_NUM_THREADS = '2'
$env:OPENCV_FOR_THREADS_NUM = '2'
$env:ORT_INTRA_OP_NUM_THREADS = '2'
$env:ORT_INTER_OP_NUM_THREADS = '1'
$env:OMP_WAIT_POLICY = 'PASSIVE'
if (!(Test-Path -LiteralPath $Exe -PathType Leaf)) { throw "Missing main program: $Exe" }
if ($NoLaunch) { exit 0 }
if (!(Stop-ExistingAssistantInstances)) { exit 5 }

$RecoverableCrashBurstLimit = 3
$StableRuntimeResetSeconds = 600
$CrashCooldownSeconds = 300
$consecutiveCrashCount = 0
$lastExitCode = 0

while ($true) {
    $startedAt = Get-Date
    $assistantProcess = Start-Process -FilePath $Exe -WorkingDirectory $AppDir -PassThru
    [void](Set-AssistantProcessLimits $assistantProcess)
    Write-WatchdogLog (
        'started pid=' + $assistantProcess.Id +
        ' consecutiveCrashCount=' + $consecutiveCrashCount
    )

    $assistantProcess.WaitForExit()
    try { $assistantProcess.Refresh() } catch {}
    $lastExitCode = [int]$assistantProcess.ExitCode
    $runtimeSeconds = [int]((Get-Date) - $startedAt).TotalSeconds

    # Save the active settings as an exact byte copy; never parse or normalize it.
    Sync-LegacyUserConfig `
        (Join-Path $LegacyProfile 'config-multi.ini') `
        (Join-Path $LegacyPortable 'config-multi.ini')
    Sync-NewerFiles $LegacyProfile $LegacyPortable
    Sync-NewerFiles $CurrentProfile $CurrentPortable

    $disposition = Get-AssistantExitDisposition $lastExitCode
    if ($disposition -ne 'restart') {
        Write-WatchdogLog (
            'controlled_or_unclassified_exit pid=' + $assistantProcess.Id +
            ' exitCode=' + $lastExitCode +
            ' runtimeSeconds=' + $runtimeSeconds +
            ' action=stop-supervisor'
        )
        break
    }

    if ($runtimeSeconds -ge $StableRuntimeResetSeconds) {
        $consecutiveCrashCount = 0
    }
    $consecutiveCrashCount++
    $delaySeconds = Get-AssistantRestartDelaySeconds $consecutiveCrashCount

    if ($consecutiveCrashCount -ge $RecoverableCrashBurstLimit) {
        $delaySeconds = $CrashCooldownSeconds
        Write-WatchdogLog (
            'recoverable_native_crash pid=' + $assistantProcess.Id +
            ' exitCode=' + $lastExitCode +
            ' runtimeSeconds=' + $runtimeSeconds +
            ' attempt=' + $consecutiveCrashCount + '/' + $RecoverableCrashBurstLimit +
            ' action=cooldown delaySeconds=' + $delaySeconds
        )
        Start-Sleep -Seconds $delaySeconds
        $consecutiveCrashCount = 0
        continue
    }

    Write-WatchdogLog (
        'recoverable_native_crash pid=' + $assistantProcess.Id +
        ' exitCode=' + $lastExitCode +
        ' runtimeSeconds=' + $runtimeSeconds +
        ' attempt=' + $consecutiveCrashCount + '/' + $RecoverableCrashBurstLimit +
        ' action=restart delaySeconds=' + $delaySeconds
    )
    Start-Sleep -Seconds $delaySeconds
}

if ($lastExitCode -eq 0 -or $lastExitCode -eq -1) { exit 0 }
exit $lastExitCode
