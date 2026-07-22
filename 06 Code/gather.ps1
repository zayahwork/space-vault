# gather.ps1 - the CTO's zero-token plumbing pass.
# Merges every lane branch into master, syncs origin, relays master back into every lane
# worktree (sparse views filter what each lane materializes), then prints loop status.
# A merge CONFLICT stops the script and names the file - conflicts are judgment calls and
# belong to the CTO, never to automation.
#
#   .\gather.ps1            full pass
#   .\gather.ps1 -NoPush    local only (offline)
param([switch]$NoPush)
$Root   = 'C:\Space'
$cfg    = Get-Content (Join-Path $Root '06 Code\loops.json') -Raw | ConvertFrom-Json
$lanes  = @($cfg.lanes.PSObject.Properties | Where-Object { $_.Value.enabled } | ForEach-Object { $_.Name })

Set-Location $Root
foreach ($name in $lanes) {
    git merge $name --no-edit -q 2>$null
    if ($LASTEXITCODE -ne 0) {
        $conflicts = git diff --name-only --diff-filter=U
        Write-Host "CONFLICT merging '$name' into master: $conflicts" -ForegroundColor Red
        Write-Host 'Stopped. Resolve in the CTO session (honest-dispute style), commit, re-run.' -ForegroundColor Red
        exit 1
    }
    Write-Host "gathered $name"
}
if (-not $NoPush) {
    git pull --no-edit -q origin master 2>$null
    git push -q origin master
    if ($LASTEXITCODE -eq 0) { Write-Host 'origin synced' } else { Write-Host 'push failed - check remote' -ForegroundColor Yellow }
}
foreach ($name in $lanes) {
    $wt = $cfg.lanes.$name.worktree
    git -C $wt merge master --no-edit -q 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "relay into $name skipped (busy or conflicted tree) - it catches up next pass" -ForegroundColor Yellow }
    else { Write-Host "relayed master -> $name" }
}
& (Join-Path $Root '06 Code\loop.ps1') status
