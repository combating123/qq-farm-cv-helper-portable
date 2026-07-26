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
    $elevatedLauncher = Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encodedCommand
    ) -PassThru -Wait
    exit $elevatedLauncher.ExitCode
}
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PortableRoot = Join-Path $AppDir 'UserData'
$LegacyPortable = Join-Path $PortableRoot 'legacy-qq-farm-bot-rev'
$CurrentPortable = Join-Path $PortableRoot 'QQFarmCopilot'
$LegacyProfile = Join-Path $env:LOCALAPPDATA 'qq-farm-bot-rev'
$CurrentProfile = Join-Path $env:APPDATA 'QQFarmCopilot'
$LogDir = Join-Path $AppDir 'logs'
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

function Disable-CloseReopenPeriodicRestart([string]$ConfigPath) {
    if (!(Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { return }
    $text = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8
    $updated = [regex]::Replace(
        $text,
        '(?m)^enable_periodic_restart\s*=\s*.*$',
        'enable_periodic_restart = False'
    )
    if ($updated -ne $text) {
        [IO.File]::WriteAllText($ConfigPath, $updated, (New-Object Text.UTF8Encoding($false)))
    }
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

New-Item -ItemType Directory -Force -Path $LogDir,$LegacyPortable,$CurrentPortable | Out-Null
# Merge any newer profile-side changes into the portable snapshot, then seed both profiles.
Sync-NewerFiles $LegacyProfile $LegacyPortable
Sync-NewerFiles $CurrentProfile $CurrentPortable
Sync-NewerFiles $LegacyPortable $LegacyProfile
Sync-NewerFiles $CurrentPortable $CurrentProfile

# A close/reopen periodic restart can leave the assistant offline if relaunch fails.
# Keep scheduled quiet hours, but disable self-closing in every active copy.
Disable-CloseReopenPeriodicRestart $LegacyProfile
Disable-CloseReopenPeriodicRestart $LegacyPortable
Disable-CloseReopenPeriodicRestart $CurrentProfile
Disable-CloseReopenPeriodicRestart $CurrentPortable

$env:QQFARM_HOOK_LOG_PATH = Join-Path $LogDir 'hook_runtime_log.txt'
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

$UnexpectedRestartLimit = 3
$unexpectedRestartCount = 0
$lastExitCode = 0

while ($true) {
    $startedAt = Get-Date
    $process = Start-Process -FilePath $Exe -WorkingDirectory $AppDir -PassThru -Wait
    $lastExitCode = $process.ExitCode

    # Save settings and statistics after every run before deciding whether to recover.
    Sync-NewerFiles $LegacyProfile $LegacyPortable
    Sync-NewerFiles $CurrentProfile $CurrentPortable

    if ($process.ExitCode -eq 0) { break }

    $runtimeSeconds = [int]((Get-Date) - $startedAt).TotalSeconds
    if ($runtimeSeconds -ge 600) { $unexpectedRestartCount = 0 }
    $unexpectedRestartCount++
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') unexpected_exit exitCode=$($process.ExitCode) runtimeSeconds=$runtimeSeconds attempt=$unexpectedRestartCount/$UnexpectedRestartLimit" |
        Add-Content -LiteralPath (Join-Path $LogDir 'watchdog.log') -Encoding UTF8

    if ($unexpectedRestartCount -ge $UnexpectedRestartLimit) { break }
    Start-Sleep -Seconds 10
}

exit $lastExitCode
