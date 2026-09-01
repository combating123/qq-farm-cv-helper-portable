param(
    [Parameter(Mandatory = $true)][int]$TargetPid,
    [Parameter(Mandatory = $true)][string]$GuardPath,
    [Parameter(Mandatory = $true)][string]$LogPath,
    [int]$WarnMB = 2048,
    [int]$TripMB = 3072,
    [int]$IntervalSeconds = 10
)

$ErrorActionPreference = 'SilentlyContinue'

function Write-ResourceWatchdogLog([string]$Message) {
    try {
        $parent = Split-Path -Parent $LogPath
        if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
        Add-Content -LiteralPath $LogPath -Encoding UTF8 -Value (
            (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' pid=' + $TargetPid +
            ' ' + $Message
        )
    } catch {}
}

function Set-GuardFlag([double]$NonpagedBytes, [double]$PagedBytes) {
    try {
        $parent = Split-Path -Parent $GuardPath
        if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
        $temp = $GuardPath + '.tmp-' + [guid]::NewGuid().ToString('N')
        $payload = [ordered]@{
            pid = $TargetPid
            utc = [DateTime]::UtcNow.ToString('o')
            nonpaged_bytes = [int64]$NonpagedBytes
            paged_bytes = [int64]$PagedBytes
            warn_mb = $WarnMB
            trip_mb = $TripMB
        } | ConvertTo-Json -Compress
        Set-Content -LiteralPath $temp -Encoding UTF8 -Value $payload
        Move-Item -LiteralPath $temp -Destination $GuardPath -Force
    } catch {}
}

try {
    if (Test-Path -LiteralPath $GuardPath -PathType Leaf) {
        Remove-Item -LiteralPath $GuardPath -Force -ErrorAction SilentlyContinue
    }
    $warnBytes = [double]([Math]::Max(256, $WarnMB)) * 1MB
    $tripBytes = [double]([Math]::Max($WarnMB + 128, $TripMB)) * 1MB
    $interval = [Math]::Max(2, [Math]::Min(60, $IntervalSeconds))
    Write-ResourceWatchdogLog ('resource_watchdog_started warnMB=' + $WarnMB +
        ' tripMB=' + $TripMB + ' intervalSeconds=' + $interval)
    while ($true) {
        $process = Get-Process -Id $TargetPid -ErrorAction SilentlyContinue
        if ($null -eq $process) { break }
        try {
            $samples = @(Get-Counter -Counter '\Memory\Pool Nonpaged Bytes',
                '\Memory\Pool Paged Bytes' -ErrorAction Stop).CounterSamples
            $nonpaged = 0.0
            $paged = 0.0
            foreach ($sample in $samples) {
                $name = [string]$sample.Path
                if ($name -match 'pool nonpaged bytes') { $nonpaged = [double]$sample.CookedValue }
                elseif ($name -match 'pool paged bytes') { $paged = [double]$sample.CookedValue }
            }
            if ($nonpaged -ge $tripBytes) {
                Set-GuardFlag $nonpaged $paged
                Write-ResourceWatchdogLog ('kernel_pool_trip nonpagedMB=' +
                    [math]::Round($nonpaged / 1MB, 1) + ' pagedMB=' +
                    [math]::Round($paged / 1MB, 1) + ' action=block-wgc')
            } elseif ($nonpaged -ge $warnBytes) {
                Write-ResourceWatchdogLog ('kernel_pool_warning nonpagedMB=' +
                    [math]::Round($nonpaged / 1MB, 1) + ' pagedMB=' +
                    [math]::Round($paged / 1MB, 1))
            }
        } catch {
            Write-ResourceWatchdogLog ('counter_error=' + $_.Exception.Message)
        }
        Start-Sleep -Seconds $interval
    }
} finally {
    try {
        if (Test-Path -LiteralPath $GuardPath -PathType Leaf) {
            Remove-Item -LiteralPath $GuardPath -Force -ErrorAction SilentlyContinue
        }
    } catch {}
    Write-ResourceWatchdogLog 'resource_watchdog_stopped'
}
