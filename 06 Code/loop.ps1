# loop.ps1 - the loop stack's one control surface.
#
#   .\loop.ps1                     status: every lane's state, budget, what's ready
#   .\loop.ps1 run                 run enabled lanes' ralph batches SEQUENTIALLY in this console
#   .\loop.ps1 run -Lanes tim      one lane only
#   .\loop.ps1 run -Windowed       one visible PowerShell window per lane, in parallel
#   .\loop.ps1 stop                kill switch: running ralphs halt at next iteration boundary
#   .\loop.ps1 resume              clear the kill switch
#   .\loop.ps1 budget              show today's iteration budget
param(
    [Parameter(Position=0)][ValidateSet('status','run','stop','resume','budget')][string]$Cmd = 'status',
    [string[]]$Lanes = @(),
    [int]$Iterations = 3,
    [switch]$Windowed
)
$Root = 'C:\Space\06 Code'
$cfg  = Get-Content (Join-Path $Root 'loops.json') -Raw | ConvertFrom-Json
if ($Lanes.Count -eq 0) {
    $Lanes = @($cfg.lanes.PSObject.Properties | Where-Object { $_.Value.enabled } | ForEach-Object { $_.Name })
}

function Show-Budget {
    if (Test-Path $cfg.budget_file) {
        $b = Get-Content $cfg.budget_file -Raw | ConvertFrom-Json
        $today = Get-Date -Format 'yyyy-MM-dd'
        if ($b.date -ne $today) { Write-Host "budget: 0/$($cfg.daily_cap) used today (counter resets on first run)" }
        else { Write-Host "budget: $($b.used)/$($b.cap) iterations used today" }
    } else { Write-Host "budget: 0/$($cfg.daily_cap) used today" }
    if (Test-Path $cfg.stop_flag) { Write-Host 'STOP flag is SET - loops will halt. Clear with: .\loop.ps1 resume' -ForegroundColor Yellow }
}

switch ($Cmd) {
    'status' {
        Write-Host "`n=== LOOP STACK STATUS | $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" -ForegroundColor Cyan
        foreach ($name in $cfg.lanes.PSObject.Properties.Name) {
            $lane = $cfg.lanes.$name
            $tag = if ($lane.enabled) { '' } else { ' (manual-only)' }
            Write-Host "`n-- $name$tag" -ForegroundColor Green
            if (-not (Test-Path $lane.worktree)) { Write-Host '   worktree missing'; continue }
            $last  = git -C $lane.worktree log -1 --format='%h %ar  %s'
            $dirty = @(git -C $lane.worktree status --porcelain).Count
            $cards = @(Get-ChildItem (Join-Path $lane.worktree $lane.kanban) -Filter '*.md' -ErrorAction SilentlyContinue |
                Where-Object { (Get-Content $_.FullName -TotalCount 6 -ErrorAction SilentlyContinue) -match 'status: open' })
            Write-Host "   last commit : $last"
            Write-Host "   uncommitted : $dirty file(s)"
            Write-Host "   open cards  : $($cards.Count)$(if ($cards.Count) { '  -> ready for /ralph' })"
            foreach ($c in $cards) { Write-Host "      - $($c.BaseName)" }
        }
        Write-Host ''
        Show-Budget
    }
    'run' {
        if (Test-Path $cfg.stop_flag) { Write-Host 'STOP flag set - refusing. Clear with .\loop.ps1 resume' -ForegroundColor Yellow; exit 1 }
        foreach ($name in $Lanes) {
            $lane = $cfg.lanes.$name
            if ($null -eq $lane) { Write-Host "unknown lane: $name"; continue }
            if (-not $lane.enabled) { Write-Host "$name is manual-only (founder order) - skipping"; continue }
            $ralphArgs = "-Path `"$($lane.worktree)`" -Loop $Iterations -Effort $($lane.effort) -Tools `"$($lane.tools)`""
            if ($Windowed) {
                Start-Process powershell -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-Command","& '$Root\ralph.ps1' $ralphArgs"
                Write-Host "launched $name in its own window ($Iterations iterations max)"
            } else {
                Write-Host "`n### lane: $name ###" -ForegroundColor Cyan
                Invoke-Expression "& '$Root\ralph.ps1' $ralphArgs"
            }
        }
    }
    'stop'   { New-Item -ItemType File -Path $cfg.stop_flag -Force | Out-Null; Write-Host 'STOP flag set. Running loops halt at the next iteration boundary.' }
    'resume' { if (Test-Path $cfg.stop_flag) { Remove-Item $cfg.stop_flag -Force }; Write-Host 'STOP flag cleared. Loops may run again.' }
    'budget' { Show-Budget }
}
