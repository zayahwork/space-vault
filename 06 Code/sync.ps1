# sync.ps1 - one command to sync the vault with GitHub (private repo zayahwork/space-vault).
# Run it when you sit down (get everything) and when you stand up (send everything).
# Type `sync` in any terminal after install.ps1 has run.
$vault = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $vault

$branch = git rev-parse --abbrev-ref HEAD
Write-Host "Pulling $branch..." -ForegroundColor Cyan
git pull --rebase origin $branch
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull hit a conflict - fix it here (or ask a Claude window) before pushing." -ForegroundColor Yellow
    exit 1
}
Write-Host "Pushing all branches..." -ForegroundColor Cyan
git push origin --all
Write-Host "Synced. Crew branches included - merge decisions still happen only on this machine's master." -ForegroundColor Green
