# standup.ps1 - the 8am harsh standup. Deterministic assembly + ONE low-effort claude pass.
# Register (founder runs once, from an admin prompt):
#   schtasks /Create /TN "Morning Standup" /TR "powershell -ExecutionPolicy Bypass -File \"C:\Space\06 Code\standup.ps1\"" /SC DAILY /ST 07:57
#
# Output: C:\Space\STANDUP - <date>.md  (linked from the day file if it exists)
$Root  = 'C:\Space'
$cfg   = Get-Content (Join-Path $Root '06 Code\loops.json') -Raw | ConvertFrom-Json
$today = Get-Date -Format 'yyyy-MM-dd'
$out   = Join-Path $Root "STANDUP - $today.md"

# --- 1. Deterministic raw material (zero tokens) ---
$raw = "RAW STANDUP MATERIAL $today`n"
foreach ($p in $cfg.lanes.PSObject.Properties) {
    $name = $p.Name; $lane = $p.Value
    if (-not (Test-Path $lane.worktree)) { continue }
    $raw += "`n== LANE: $name ==`n"
    $raw += "commits last 24h:`n" + ((git -C $lane.worktree log --since='24 hours ago' --format='%h %s') -join "`n") + "`n"
    $cards = Get-ChildItem (Join-Path $lane.worktree $lane.kanban) -Filter '*.md' -ErrorAction SilentlyContinue
    foreach ($c in $cards) {
        $head = (Get-Content $c.FullName -TotalCount 6) -join ' '
        if ($head -match 'status: (open|blocked)') { $raw += "card [$($Matches[1])]: $($c.BaseName)`n" }
    }
    $next = Join-Path $lane.worktree '02 Task Guides'
    $nf = Get-ChildItem $next -Filter 'NEXT - *.md' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($nf) {
        $body = Get-Content $nf.FullName -Raw
        $idx = $body.LastIndexOf('CTO report')
        if ($idx -ge 0) { $raw += "latest worker report (tail):`n" + $body.Substring($idx, [Math]::Min(1500, $body.Length - $idx)) + "`n" }
    }
}
if (Test-Path $cfg.budget_file) { $raw += "`nBUDGET: " + (Get-Content $cfg.budget_file -Raw) + " (cap $($cfg.daily_cap)/day = the 10-14% weekly rule)`n" }
$days = [int]([datetime]'2026-07-29' - (Get-Date)).TotalDays
$raw += "COUNTDOWN: ~$days day(s) to quiet.py unlock (Jul 29); broker meeting window Jul 30-Aug 1.`n"

# --- 2. One cheap claude pass for the harsh verdict ---
$prompt = @"
You are the CTO writing the 8am HARSH standup for the founder (ADHD-friendly: plain words,
short lines, jargon explained or omitted). From the raw material below produce
'# Standup $today' in markdown, and NOTHING else:
- Per lane (tim/randy/mark, video only if it committed): 4 lines max - SHIPPED (with a
  number), BLOCKED (name whose fault: founder/CTO/worker/external), TODAY'S ONE MUST-DO,
  and any MISSED promise in **bold**. No praise padding. Misses get named, not softened.
- One company line: countdown, sends vs target, budget used yesterday.
- Final line: the single most important thing in the company today.
- SECTION 'This Week's Grind List' (founder order): a LONG structured per-lane list for the week - enough that finishing it is a grind, not a sprint - plus the #1 named bottleneck (current CTO read: zero customers; investor conversations + traffic channels are the fix in motion).
Do not invent facts not present in the material; write 'no data' where the material is silent.

$raw
"@
$verdict = $prompt | claude -p --model claude-opus-4-8 --effort low 2>&1 | Out-String
if ($verdict -match 'session limit|rate limit|usage limit' -or [string]::IsNullOrWhiteSpace($verdict)) {
    $verdict = "# Standup $today`n(claude pass unavailable - raw material below, unjudged)`n`n" + $raw
}
$verdict | Out-File $out -Encoding utf8

# --- 3. Link from the day file if one exists ---
$day = Join-Path $Root "$today.md"
if (Test-Path $day) { Add-Content $day "`n> [!todo] Morning standup: [[STANDUP - $today]]" -Encoding utf8 }
