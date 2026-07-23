# build_workspace.ps1 - generates the multi-root VS Code workspace from loops.json,
# so the "who owns what folder" view never drifts from the actual lane registry.
#
# Re-run any time a lane is added/removed in loops.json:
#   .\build_workspace.ps1
#
# Output: C:\Space\Company.code-workspace (gitignored - the worktree paths below are
# absolute and machine-specific; regenerate on any new machine instead of syncing it).
$cfg = Get-Content (Join-Path $PSScriptRoot 'loops.json') -Raw | ConvertFrom-Json

# Plain ASCII labels on purpose - PowerShell 5.1's ConvertTo-Json/Out-File pipeline
# mangles emoji on round-trip (verified: wrote garbled bytes on first attempt).
$tags = @{ tim = '[TIM]'; randy = '[RANDY]'; mark = '[MARK]'; video = '[VIDEO]' }
$folders = @(@{ name = '[CTO] everything'; path = $cfg.root })
foreach ($p in $cfg.lanes.PSObject.Properties) {
    $tag = if ($tags.ContainsKey($p.Name)) { $tags[$p.Name] } else { "[$($p.Name.ToUpper())]" }
    $folders += @{ name = "$tag $($p.Name)"; path = $p.Value.worktree }
}

$workspace = [ordered]@{
    folders  = $folders
    settings = @{}
}
$out = Join-Path $cfg.root 'Company.code-workspace'
$workspace | ConvertTo-Json -Depth 5 | Out-File $out -Encoding ascii
Write-Host "Wrote $out with $($folders.Count) folders:"
$folders | ForEach-Object { Write-Host "  $($_.name)  ->  $($_.path)" }
Write-Host "`nOpen it: code `"$out`"  (or double-click it in Explorer)"
