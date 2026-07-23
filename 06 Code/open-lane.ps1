# open-lane.ps1 - jump straight into one lane's world in a fresh VS Code window.
#   .\open-lane.ps1 tim       opens Tim's worktree alone
#   .\open-lane.ps1 cto       opens the CTO root (C:\Space, sees everything)
#   .\open-lane.ps1 all       opens the combined multi-root workspace (all lanes at once)
param([Parameter(Mandatory)][string]$Lane)
$cfg = Get-Content (Join-Path $PSScriptRoot 'loops.json') -Raw | ConvertFrom-Json

switch ($Lane.ToLower()) {
    'cto' { code $cfg.root; return }
    'all' { code (Join-Path $cfg.root 'Company.code-workspace'); return }
}
$lane = $cfg.lanes.($Lane.ToLower())
if ($null -eq $lane) {
    Write-Host "Unknown lane '$Lane'. Options: cto, all, $($cfg.lanes.PSObject.Properties.Name -join ', ')" -ForegroundColor Yellow
    exit 1
}
code $lane.worktree
