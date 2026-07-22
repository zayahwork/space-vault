# install.ps1 - set up the crew grid on a new machine (laptop, new PC, anywhere).
#
# Prereqs on the machine: git, Claude Code (signed in: `claude` once to log in).
# Then:   powershell -ExecutionPolicy Bypass -File "06 Code\install.ps1"
# After:  open a NEW terminal and type `t`.
#
# What it does (all idempotent, safe to re-run):
#   1. Status line -> ~\.claude\statusline.ps1 + wires it into ~\.claude\settings.json
#   2. `t` command  -> PowerShell profile function + t.cmd for Command Prompt
#   3. Everything else (personas, worktrees, colors, sessions) is created by t.ps1
#      itself on first launch, from wherever this repo was cloned.

$vault     = Split-Path $PSScriptRoot -Parent
$claudeDir = Join-Path $env:USERPROFILE '.claude'
if (-not (Test-Path $claudeDir)) { New-Item -ItemType Directory -Path $claudeDir | Out-Null }

# --- 1. Status line ---
Copy-Item (Join-Path $PSScriptRoot 'statusline.ps1') (Join-Path $claudeDir 'statusline.ps1') -Force
$settingsFile = Join-Path $claudeDir 'settings.json'
$statusCmd = "powershell -NoProfile -ExecutionPolicy Bypass -File $claudeDir\statusline.ps1"
if (Test-Path $settingsFile) {
    $j = Get-Content $settingsFile -Raw | ConvertFrom-Json
} else {
    $j = [pscustomobject]@{}
}
if ($j.PSObject.Properties['statusLine']) {
    $j.statusLine.command = $statusCmd
} else {
    $j | Add-Member -NotePropertyName statusLine -NotePropertyValue ([pscustomobject]@{
        type = 'command'; command = $statusCmd
    })
}
$j | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsFile -Encoding UTF8
Write-Host "[OK] status line installed + wired into settings.json"

# --- 2. The `t` command ---
$profileDir = Split-Path $PROFILE
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force | Out-Null }
$tLine = "function t { & '$vault\06 Code\t.ps1' @args }"
if (-not (Test-Path $PROFILE) -or (Get-Content $PROFILE -Raw) -notmatch 'function t ') {
    Add-Content -Path $PROFILE -Value $tLine
    Write-Host "[OK] 't' added to PowerShell profile"
} else {
    Write-Host "[OK] 't' already in PowerShell profile (left as is)"
}
$syncLine = "function sync { & '$vault\06 Code\sync.ps1' @args }"
if (-not (Test-Path $PROFILE) -or (Get-Content $PROFILE -Raw) -notmatch 'function sync ') {
    Add-Content -Path $PROFILE -Value $syncLine
    Write-Host "[OK] 'sync' added to PowerShell profile"
}
$binDir = Join-Path $env:USERPROFILE '.local\bin'
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$binDir", 'User')
        Write-Host "[OK] added $binDir to your PATH (new terminals only)"
    }
}
Set-Content -Path (Join-Path $binDir 't.cmd') -Encoding Ascii -Value @"
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "$vault\06 Code\t.ps1" %*
"@
Write-Host "[OK] t.cmd installed for Command Prompt"

Write-Host ""
Write-Host "Done. Open a NEW terminal and type: t" -ForegroundColor Green
Write-Host "(If the code needs to run here too, copy 06 Code\spacetrack_auth.json from the PC manually - it is never in git.)"
