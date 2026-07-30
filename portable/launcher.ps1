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
# Keep the original host paths only as one-time, read-only migration sources.
# The packaged assistant itself receives E:\...\UserData paths through its
# inherited environment, so regular runs do not create or sync user state on C:.
$HostLocalAppData = $env:LOCALAPPDATA
$HostAppData = $env:APPDATA
$PortableRoot = Join-Path $AppDir 'UserData'
$PortableProfileRoot = Join-Path $PortableRoot 'WindowsProfile'
$PortableLocalAppData = Join-Path $PortableProfileRoot 'LocalAppData'
$PortableAppData = Join-Path $PortableProfileRoot 'RoamingAppData'
$PortableTemp = Join-Path $PortableProfileRoot 'Temp'
$HostLegacyProfile = Join-Path $HostLocalAppData 'qq-farm-bot-rev'
$HostCurrentProfile = Join-Path $HostAppData 'QQFarmCopilot'
# These were used by earlier portable launchers. They are migration sources only.
$PreviousLegacyProfile = Join-Path $PortableRoot 'legacy-qq-farm-bot-rev'
$PreviousCurrentProfile = Join-Path $PortableRoot 'QQFarmCopilot'
$LegacyProfile = Join-Path $PortableLocalAppData 'qq-farm-bot-rev'
$CurrentProfile = Join-Path $PortableAppData 'QQFarmCopilot'
$MigrationMarker = Join-Path $PortableProfileRoot 'migration-v1.complete'
$LogDir = Join-Path $AppDir 'logs'
$HookLogDir = Join-Path $AppDir 'logs'
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
    if ($name -in @('daily_flow_status.json', 'daily_counters.json', 'daily_counters.hook.json', 'daily_task_retry_state.json')) { return $true }
    if ($name -like '*.log' -or $name -like '*.tmp' -or $name -like '*.bak*' -or $name -like '*.bad-*') { return $true }
    return $false
}

function Import-MissingProfileFiles([string]$Source, [string]$Destination) {
    if (!(Test-Path -LiteralPath $Source -PathType Container)) { return }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $prefixLength = $Source.TrimEnd('\\').Length + 1
    Get-ChildItem -LiteralPath $Source -Recurse -File -Force | ForEach-Object {
        $relative = $_.FullName.Substring($prefixLength)
        if (Test-ExcludedRelativePath $relative) { return }
        $target = Join-Path $Destination $relative
        if (!(Test-Path -LiteralPath $target -PathType Leaf)) {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        }
    }
}

function Remove-Utf8BomFromConfig([string]$Path) {
    # The packaged application reads config-multi.ini as plain UTF-8. A BOM is
    # interpreted as text before the first section header and makes the entire
    # file look malformed. This function is intentionally called on the E: copy
    # only; the original C: config is never opened for writing by this launcher.
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 3) { return $false }
    if ($bytes[0] -ne 0xEF -or $bytes[1] -ne 0xBB -or $bytes[2] -ne 0xBF) { return $false }
    $clean = New-Object byte[] ($bytes.Length - 3)
    [Array]::Copy($bytes, 3, $clean, 0, $clean.Length)
    [IO.File]::WriteAllBytes($Path, $clean)
    return $true
}

function Initialize-PortableConfiguration(
    [string]$HostConfig,
    [string]$PreviousPortableConfig,
    [string]$PortableConfig
) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $PortableConfig) | Out-Null
    # On the first portable migration, the user's existing C: config wins even
    # if an older E: portable copy exists. Copy-Item is byte-for-byte.
    if (Test-Path -LiteralPath $HostConfig -PathType Leaf) {
        Copy-Item -LiteralPath $HostConfig -Destination $PortableConfig -Force
    } elseif (Test-Path -LiteralPath $PreviousPortableConfig -PathType Leaf) {
        Copy-Item -LiteralPath $PreviousPortableConfig -Destination $PortableConfig -Force
    }
    [void](Remove-Utf8BomFromConfig -Path $PortableConfig)
}

function Import-MostRecentFile([string[]]$Sources, [string]$Destination) {
    if (Test-Path -LiteralPath $Destination -PathType Leaf) { return $false }
    $available = @(
        $Sources |
            Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
            Sort-Object { (Get-Item -LiteralPath $_).LastWriteTimeUtc } -Descending
    )
    if ($available.Count -eq 0) { return $false }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    Copy-Item -LiteralPath $available[0] -Destination $Destination -Force
    return $true
}

function Initialize-PortableProfile(
    [string]$HostLegacyProfile,
    [string]$HostCurrentProfile,
    [string]$PreviousLegacyProfile,
    [string]$PreviousCurrentProfile,
    [string]$LegacyProfile,
    [string]$CurrentProfile,
    [string]$MigrationMarker
) {
    # A marker turns migration into a one-time import. No automatic E: -> C:
    # sync exists, and later C: changes cannot overwrite E: user settings.
    if (Test-Path -LiteralPath $MigrationMarker -PathType Leaf) { return $false }

    New-Item -ItemType Directory -Force -Path `
        $LegacyProfile, $CurrentProfile, (Split-Path -Parent $MigrationMarker) | Out-Null

    Import-MissingProfileFiles -Source $HostLegacyProfile -Destination $LegacyProfile
    Import-MissingProfileFiles -Source $PreviousLegacyProfile -Destination $LegacyProfile
    Import-MissingProfileFiles -Source $HostCurrentProfile -Destination $CurrentProfile
    Import-MissingProfileFiles -Source $PreviousCurrentProfile -Destination $CurrentProfile

    Initialize-PortableConfiguration `
        -HostConfig (Join-Path $HostLegacyProfile 'config-multi.ini') `
        -PreviousPortableConfig (Join-Path $PreviousLegacyProfile 'config-multi.ini') `
        -PortableConfig (Join-Path $LegacyProfile 'config-multi.ini')

    # Daily completion records must follow the same-day newest state exactly
    # once; after migration, every update remains under E:\\...\\UserData.
    foreach ($stateName in @(
        'daily_flow_status.json',
        'daily_counters.json',
        'daily_counters.hook.json',
        'daily_task_retry_state.json'
    )) {
        [void](Import-MostRecentFile -Sources @(
            (Join-Path $HostLegacyProfile $stateName),
            (Join-Path $HostCurrentProfile $stateName),
            (Join-Path $PreviousLegacyProfile $stateName),
            (Join-Path $PreviousCurrentProfile $stateName)
        ) -Destination (Join-Path $CurrentProfile $stateName))
    }

    [IO.File]::WriteAllText(
        $MigrationMarker,
        'completed=' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + "`r`n",
        [Text.UTF8Encoding]::new($false)
    )
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

New-Item -ItemType Directory -Force -Path `
    $LogDir, $HookLogDir, $PortableProfileRoot, $PortableLocalAppData, $PortableAppData, $PortableTemp, $LegacyProfile, $CurrentProfile | Out-Null
[void](Initialize-PortableProfile `
    -HostLegacyProfile $HostLegacyProfile `
    -HostCurrentProfile $HostCurrentProfile `
    -PreviousLegacyProfile $PreviousLegacyProfile `
    -PreviousCurrentProfile $PreviousCurrentProfile `
    -LegacyProfile $LegacyProfile `
    -CurrentProfile $CurrentProfile `
    -MigrationMarker $MigrationMarker)

# Every child process, including QQFarmCVHelper.exe, inherits the E: profile.
$env:LOCALAPPDATA = $PortableLocalAppData
$env:APPDATA = $PortableAppData
$env:TEMP = $PortableTemp
$env:TMP = $PortableTemp

$env:QQFARM_HOOK_LOG_PATH = Join-Path $HookLogDir 'hook_runtime_log.txt'
$env:QQFARM_DAILY_FLOW_STATUS_PATH = Join-Path $CurrentProfile 'daily_flow_status.json'
$env:QQFARM_DAILY_COUNTERS_PATH = Join-Path $CurrentProfile 'daily_counters.json'
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

    # The child uses the portable E: profile and writes its current settings there.
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
