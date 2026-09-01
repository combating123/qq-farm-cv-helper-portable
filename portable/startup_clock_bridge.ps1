Set-StrictMode -Version 2

function Test-StartupClockBridgeRequired {
    param(
        [datetime]$Now = (Get-Date),
        [datetime]$SupportedDate = ([datetime]'2026-08-20')
    )
    return $Now.Date -gt $SupportedDate.Date
}

function Enter-StartupClockBridge {
    param([datetime]$SupportedDate = ([datetime]'2026-08-20'))

    $realStart = Get-Date
    $stopwatch = [Diagnostics.Stopwatch]::StartNew()
    # Use a fixed daytime bootstrap instant. Reusing the current wall-clock
    # hour makes startup cross the packaged cutoff again later the same day.
    $temporary = Get-Date -Year $SupportedDate.Year -Month $SupportedDate.Month `
        -Day $SupportedDate.Day -Hour 12 -Minute 0 -Second 0
    Set-Date -Date $temporary | Out-Null
    [pscustomobject]@{
        RealStart = $realStart
        Stopwatch = $stopwatch
        TemporaryDate = $temporary
    }
}

function Exit-StartupClockBridge {
    param([Parameter(Mandatory=$true)]$Context)

    $elapsed = $Context.Stopwatch.Elapsed
    $Context.Stopwatch.Stop()
    Set-Date -Date ($Context.RealStart + $elapsed) | Out-Null
}
