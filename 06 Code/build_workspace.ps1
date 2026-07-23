# build_workspace.ps1 - generates the multi-root VS Code workspace from loops.json,
# so the "who owns what folder" view never drifts from the actual lane registry.
#
# Re-run any time a lane is added/removed in loops.json:
#   .\build_workspace.ps1
#
# Output: C:\Space\Company.code-workspace (gitignored - the worktree paths below are
# absolute and machine-specific; regenerate on any new machine instead of syncing it).
$cfg = Get-Content (Join-Path $PSScriptRoot 'loops.json') -Raw | ConvertFrom-Json

$icons = @{ tim = '🔧'; randy = '📚'; mark = '📣'; video = '🎥' }
$folders = @(@{ name = "🎯 CTO - everything"; path = $cfg.root })
foreach ($p in $cfg.lanes.PSObject.Properties) {
    $icon = if ($icons.ContainsKey($p.Name)) { $icons[$p.Name] } else { '📁' }
    $label = "$icon $($p.Name.ToUpper())"
    $folders += @{ name = $label; path = $p.Value.worktree }
}

$workspace = [ordered]@{
    folders  = $folders
    settings = @{}
}
$out = Join-Path $cfg.root 'Company.code-workspace'
$workspace | ConvertTo-Json -Depth 5 | Out-File $out -Encoding utf8
Write-Host "Wrote $out with $($folders.Count) folders:"
$folders | ForEach-Object { Write-Host "  $($_.name)  ->  $($_.path)" }
Write-Host "`nOpen it: code `"$out`"  (or double-click it in Explorer)"
