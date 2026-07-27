param(
    [string]$SourceDir = 'E:\CV农场助手',
    [string]$OutputDir = 'E:\CodexBuilds\qq-farm\releases',
    [string]$Version = ''
)
$ErrorActionPreference = 'Stop'

if (-not $Version) {
    $Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\VERSION') -Raw -Encoding UTF8).Trim()
}
if (-not $Version) { throw 'VERSION is empty' }
if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) { throw "Source directory missing: $SourceDir" }

$source = (Resolve-Path -LiteralPath $SourceDir).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$output = (Resolve-Path -LiteralPath $OutputDir).Path
$stage = Join-Path $output ('.stage-CVFarm-' + $Version)
$zip = Join-Path $output ('CV农场助手-v' + $Version + '-便携完整版.zip')
$hashFile = $zip + '.sha256'
$outputPrefix = $output.TrimEnd('\') + '\'
$stageFull = [IO.Path]::GetFullPath($stage)
if (-not $stageFull.StartsWith($outputPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Stage path escaped output root: $stageFull"
}
if (Test-Path -LiteralPath $stageFull) {
    Remove-Item -LiteralPath $stageFull -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stageFull | Out-Null

$excludedDirs = @('UserData', 'logs', '__pycache__', 'screenshots', 'captures', 'cache', 'crash')
$sourcePrefixLength = $source.TrimEnd('\').Length + 1
Get-ChildItem -LiteralPath $source -Recurse -File -Force | ForEach-Object {
    $relative = $_.FullName.Substring($sourcePrefixLength)
    $parts = $relative -split '[\\/]'
    if (@($parts | Where-Object { $excludedDirs -contains $_ }).Count -gt 0) { return }
    if ($_.Name -like '*.bak-*' -or $_.Name -like '*.tmp*' -or $_.Name -like '*.log' -or $_.Name -like '*.pyc') { return }
    $target = Join-Path $stageFull $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $target -Force
}

if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $stageFull '*') -DestinationPath $zip -CompressionLevel Optimal
$hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
[IO.File]::WriteAllText($hashFile, ($hash + '  ' + [IO.Path]::GetFileName($zip) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
Remove-Item -LiteralPath $stageFull -Recurse -Force
[pscustomobject]@{ Version = $Version; Zip = $zip; Sha256 = $hash; Bytes = (Get-Item -LiteralPath $zip).Length }