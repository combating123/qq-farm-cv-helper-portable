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

$excludedDirs = @('UserData', 'logs', '__pycache__', 'screenshots', 'captures', 'cache', 'crash', 'backups', 'artifacts', 'diagnostics', 'maintenance-backup', 'runtime-v2.2.5', 'deployment-backups', 'migration-archive')
$sourcePrefixLength = $source.TrimEnd('\').Length + 1
Get-ChildItem -LiteralPath $source -Recurse -File -Force | ForEach-Object {
    $relative = $_.FullName.Substring($sourcePrefixLength)
    $parts = $relative -split '[\\/]'
    if (@($parts | Where-Object { $excludedDirs -contains $_ }).Count -gt 0) { return }
    if ($_.Name -like '*.bak-*' -or $_.Name -like '*.backup-*' -or $_.Name -like '*.tmp*' -or $_.Name -like '*.log' -or $_.Name -like '*.pyc' -or $_.Name -like '*.lnk') { return }
    if ($parts.Count -eq 1 -and (
        $_.Name -like 'desktop-*.png' -or
        $_.Name -like '_analysis*.png' -or
        $_.Name -like 'live-*.png' -or
        $_.Name -like 'annotated-*.png' -or
        $_.Name -eq 'StartFarmAssistant-Clean.ps1'
    )) { return }
    $target = Join-Path $stageFull $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $target -Force
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$readmeSource = Join-Path $repoRoot 'README.md'
$changelogSource = Join-Path $repoRoot 'CHANGELOG.md'
if (!(Test-Path -LiteralPath $readmeSource -PathType Leaf)) { throw "README missing: $readmeSource" }
if (!(Test-Path -LiteralPath $changelogSource -PathType Leaf)) { throw "CHANGELOG missing: $changelogSource" }
Copy-Item -LiteralPath $readmeSource -Destination (Join-Path $stageFull 'README.md') -Force
$releaseNotesName = (
    [char]0x7248 + [char]0x672C + [char]0x4E0E + [char]0x66F4 +
    [char]0x65B0 + [char]0x65E5 + [char]0x5FD7 + '.md'
)
Copy-Item -LiteralPath $changelogSource -Destination (Join-Path $stageFull $releaseNotesName) -Force
[IO.File]::WriteAllText(
    (Join-Path $stageFull 'VERSION'),
    $Version + [Environment]::NewLine,
    [Text.UTF8Encoding]::new($false)
)
$projectInfoName = (
    [char]0x9879 + [char]0x76EE + [char]0x8BF4 + [char]0x660E + '.txt'
)
$projectInfo = @(
    'CV 农场助手 v' + $Version,
    '项目仓库：https://github.com/combating123/qq-farm-cv-helper-portable',
    '发布页：https://github.com/combating123/qq-farm-cv-helper-portable/releases',
    '费用声明：本项目免费发布，维护者不会向任何用户收取费用。',
    '',
    '更新说明：',
    '1. 启动、更新和监督重启均保留用户原设置；',
    '2. 自家收获、种满、施肥和空地复核优先于好友巡检；',
    '3. 2x2 特殊种子仅使用真实相邻田字型，失败后继续普通种子；',
    '4. 好友链保留首位、护主、偷取后务农、封禁返回和装扮门禁；',
    '5. 每日分享只在精确目标、单联系人、直接发送和对话框关闭全部校验后记录成功。',
    '6. LocalAppData、RoamingAppData、TEMP、TMP、日志和每日状态都在 UserData\WindowsProfile，更新时保留 UserData。',
    '',
    '完整迭代内容请查看 README.md 和 版本与更新日志.md。'
) -join [Environment]::NewLine
[IO.File]::WriteAllText(
    (Join-Path $stageFull $projectInfoName),
    $projectInfo + [Environment]::NewLine,
    [Text.UTF8Encoding]::new($false)
)

if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $stageFull '*') -DestinationPath $zip -CompressionLevel Optimal
$hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
[IO.File]::WriteAllText($hashFile, ($hash + '  ' + [IO.Path]::GetFileName($zip) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
Remove-Item -LiteralPath $stageFull -Recurse -Force
[pscustomobject]@{ Version = $Version; Zip = $zip; Sha256 = $hash; Bytes = (Get-Item -LiteralPath $zip).Length }