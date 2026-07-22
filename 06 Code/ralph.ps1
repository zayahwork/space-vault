# ralph.ps1 - the night shift. Loops headless Claude over the AFK issues in issues/.
#
#   .\ralph.ps1                        one iteration, watch it work (tune before looping)
#   .\ralph.ps1 -Loop 5                up to 5 issues back-to-back, stops early on NO MORE TASKS
#   .\ralph.ps1 -Path <worktree>       run against a specific worktree (recommended: not master)
#   .\ralph.ps1 -Effort high           default medium - implementation is cheap, review is not
#
# Safety: file edits are auto-accepted; bash is limited to python/pip/git. It cannot
# send email, touch the network beyond pip, or leave the repo. Each iteration is a
# fresh context window (Memento-style) - state lives in issues/ and git, not the chat.
param(
    [string]$Path = (Join-Path $env:USERPROFILE '.claude\worktrees\C--Space-detector'),
    [int]$Loop = 1,
    [string]$Effort = 'medium',
    # Lane worktrees are sparse: a worker only has issues/<lane>/ on disk, so the recursive
    # scan below naturally picks up only that lane's cards. Extra tools per lane (e.g.
    # research needs WebSearch) ride in via -Tools.
    [string]$Tools = 'Bash(python *),Bash(pip *),Bash(git *)'
)

if (-not (Test-Path (Join-Path $Path 'issues'))) {
    Write-Error "No issues/ folder in $Path - run /issues first (and merge/commit so the worktree sees it)."
    exit 1
}
Set-Location -LiteralPath $Path

for ($i = 1; $i -le $Loop; $i++) {
    Write-Host "`n=== ralph iteration $i of $Loop | $(Get-Date -Format 'HH:mm') | $Path ===" -ForegroundColor Cyan

    $issues  = (Get-ChildItem 'issues' -Recurse -Filter '*.md' | Where-Object { $_.Name -notmatch '^(PRD|README)' } | ForEach-Object {
        $rel = $_.FullName.Substring((Get-Location).Path.Length + 1) -replace '\\','/'
        "--- FILE: $rel ---`n" + (Get-Content $_.FullName -Raw)
    }) -join "`n`n"
    $commits = (git log -5 --oneline) -join "`n"
    $prompt  = @"
You are the night shift working alone in this repo. The full issue backlog and recent
commits are below. Follow the repo's /ralph rules exactly: pick ONE open, unblocked,
type: AFK issue (bug fixes > feedback-loop infrastructure > tracer bullets > polish),
complete it test-first where possible, run the feedback loops, mark it status: done,
commit, and stop. If no issue qualifies, output exactly: NO MORE TASKS
HARD RULES: work only in this worktree on its own branch; never merge, switch branch or
push; NEVER send email or run any script in --live/--send mode - drafting is the ceiling;
stay inside the folders present in this worktree.

RECENT COMMITS:
$commits

ISSUE BACKLOG:
$issues
"@

    $out = $prompt | claude -p --permission-mode acceptEdits --effort $Effort `
        --allowedTools "Bash(python *),Bash(pip *),Bash(git *)" 2>&1 | Out-String
    Write-Host $out

    if ($out -match 'NO MORE TASKS') {
        Write-Host "Backlog is dry - stopping after $i iteration(s)." -ForegroundColor Green
        break
    }
    if ($out -match 'session limit|rate limit|usage limit') {
        # Burning the remaining iterations against a closed gate wastes nothing but
        # produces 10 failure lines and no work. Stop; the CTO cycle relaunches after reset.
        Write-Host "Hit the plan's session limit - stopping. Relaunch after the reset time above." -ForegroundColor Yellow
        exit 2
    }
}
