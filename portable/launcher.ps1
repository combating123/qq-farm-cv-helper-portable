param([switch]$NoLaunch)
$ErrorActionPreference = 'Stop'
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PortableRoot = Join-Path $AppDir 'UserData'
$LegacyPortable = Join-Path $PortableRoot 'legacy-qq-farm-bot-rev'
$CurrentPortable = Join-Path $PortableRoot 'QQFarmCopilot'
$LegacyProfile = Join-Path $env:LOCALAPPDATA 'qq-farm-bot-rev'
$CurrentProfile = Join-Path $env:APPDATA 'QQFarmCopilot'
$LogDir = Join-Path $AppDir 'logs'
$Exe = Join-Path $AppDir 'QQFarmCVHelper.exe'
$ExcludedDirs = @('logs','models','screenshots','captures','cache','__pycache__','crash')

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

New-Item -ItemType Directory -Force -Path $LogDir,$LegacyPortable,$CurrentPortable | Out-Null
# Merge any newer profile-side changes into the portable snapshot, then seed both profiles.
Sync-NewerFiles $LegacyProfile $LegacyPortable
Sync-NewerFiles $CurrentProfile $CurrentPortable
Sync-NewerFiles $LegacyPortable $LegacyProfile
Sync-NewerFiles $CurrentPortable $CurrentProfile

$env:QQFARM_HOOK_LOG_PATH = Join-Path $LogDir 'hook_runtime_log.txt'
$env:QQFARM_PROXY_LOG_PATH = Join-Path $LogDir 'proxy_dll_load.log'
if (!(Test-Path -LiteralPath $Exe -PathType Leaf)) { throw "Missing main program: $Exe" }
if ($NoLaunch) { exit 0 }

$process = Start-Process -FilePath $Exe -WorkingDirectory $AppDir -PassThru -Wait

# Save settings and statistics changed during this run back into the single folder.
Sync-NewerFiles $LegacyProfile $LegacyPortable
Sync-NewerFiles $CurrentProfile $CurrentPortable
exit $process.ExitCode