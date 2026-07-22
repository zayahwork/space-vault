# Claude Code status line: model | effort | folder (wt marker) | branch | context bar
# Input schema: https://code.claude.com/docs/en/statusline.md
$json = [Console]::In.ReadToEnd()
try { $j = $json | ConvertFrom-Json } catch { exit 0 }

$parts = @()

if ($j.model.display_name) { $parts += $j.model.display_name }
if ($j.effort.level)       { $parts += $j.effort.level.ToUpper() }

$dir = $j.workspace.current_dir
if ($dir) {
    $leaf = Split-Path $dir -Leaf
    if ($j.workspace.git_worktree) { $parts += "$leaf [worktree: $($j.workspace.git_worktree)]" }
    else                           { $parts += $leaf }
    try {
        $branch = git -C $dir rev-parse --abbrev-ref HEAD 2>$null
        if ($branch) { $parts += "on $branch" }
    } catch {}
}

# Context bar: [#####-----] 52% left   (used_percentage can be null early in a session)
$used = $j.context_window.used_percentage
if ($used -ne $null) {
    $used = [math]::Min(100, [math]::Max(0, [double]$used))
    $filled = [math]::Round($used / 10)
    $bar = ('#' * $filled) + ('-' * (10 - $filled))
    $left = [math]::Round(100 - $used)
    $tok = $j.context_window.total_input_tokens
    if ($tok) { $parts += "[$bar] $left% left ($([math]::Round($tok/1000))k)" }
    else      { $parts += "[$bar] $left% left" }
}

Write-Output ($parts -join '  |  ')
