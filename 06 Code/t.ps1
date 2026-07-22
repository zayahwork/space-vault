# t.ps1 - launch 4 Claude Code cmd windows in a 2x2 grid, one per work stream.
#
#   t                 4 windows on the space project (see layout below)
#   t C:\SomeRepo     same grid in another folder (windows whose branch doesn't
#                     exist there just open in the folder itself)
#   t -Fresh          start all 4 with blank conversations instead of resuming
#
# Layout - the crew. Each window boots as a persona on its own branch in its own
# git worktree, walled off from the others. Zayah alone merges finished work to master.
#   Top-left     CTO    high effort     cto     technical direction, orders, review
#   Top-right    TIM    high effort     tim     software/ML engineering
#   Bottom-left  MARK   medium effort   mark    outreach, social, income
#   Bottom-right RANDY  medium effort   randy   research, brainstorming
#
# Each window slot owns a permanent session ID, so closing the grid and typing `t`
# again resumes each window exactly where it left off. Use -Fresh to wipe that and
# start over (old sessions stay on disk; `claude --resume` can still find them).
#
# Worktrees live in ~\.claude\worktrees\. On creation, gitignored essentials are
# seeded in: auth files are copied, and the SupGP archive is junction-linked (one
# real archive on disk, visible from every stream).
param(
    # Default: the vault this script lives in (works wherever the repo is cloned).
    [string]$Path = (Split-Path $PSScriptRoot -Parent),
    [switch]$Fresh
)

if (-not (Test-Path -LiteralPath $Path)) { Write-Error "No such folder: $Path"; exit 1 }
$Path = (Resolve-Path -LiteralPath $Path).Path

Add-Type -AssemblyName System.Windows.Forms
Add-Type -Namespace Win32 -Name Native -MemberDefinition @'
[DllImport("user32.dll")]
public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
'@

$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$w  = [math]::Floor($wa.Width / 2)
$h  = [math]::Floor($wa.Height / 2)

# ScreenColors: low nibble = text, high nibble = background. All black on white.
# Palette slot 8 stays repainted dark grey in case any window wants 0x8F later.
$darkGrey = 0x2B2B2B   # conhost stores colours as 0x00BBGGRR - grey reads the same either way
# The crew: each window is a persona on its OWN branch in its OWN worktree.
# They are walled off from each other - Zayah is the only one who merges to master.
# Model split (usage balancing): Fable 5 is reserved for the CTO - the decision layer.
# Everyone else runs Opus 4.8; effort tiers still differ per role.
$layout = @(
    @{ Effort = 'high';   Model = 'fable'; Col = 0; Row = 0; Title = 'Claude - CTO';   Branch = 'cto';   Persona = 'cto';   Colors = 0x0F },
    @{ Effort = 'high';   Model = 'opus';  Col = 1; Row = 0; Title = 'Claude - TIM';   Branch = 'tim';   Persona = 'tim';   Colors = 0x0F },
    @{ Effort = 'medium'; Model = 'opus';  Col = 0; Row = 1; Title = 'Claude - MARK';  Branch = 'mark';  Persona = 'mark';  Colors = 0x0F },
    @{ Effort = 'high';   Model = 'opus';  Col = 1; Row = 1; Title = 'Claude - RANDY'; Branch = 'randy'; Persona = 'randy'; Colors = 0x0F },
    # VIDEO sits centered on top of the grid (launched last = top of z-order); the four
    # corners of the other windows stay visible and clickable to tab between them.
    @{ Effort = 'medium'; Model = 'opus';  Center = $true;   Title = 'Claude - VIDEO'; Branch = 'video'; Persona = 'video'; Colors = 0x0F }
)

# --- Persona system prompts (regenerated every launch so edits here take effect).
$personaDir = Join-Path $env:USERPROFILE '.claude\t-personas'
if (-not (Test-Path $personaDir)) { New-Item -ItemType Directory -Path $personaDir | Out-Null }
$commonRules = @"

HARD BOUNDARIES (Zayah's standing orders - these override politeness and initiative):
- Work ONLY inside this folder (your own worktree) on your own branch. Never git switch, never merge, never push.
- Other agents' worktrees, branches, and diffs are OFF LIMITS. Never read, list, or reference them. Missing facts come through Zayah, not through their files.
- Never touch master/main. Zayah reviews your committed work and merges it to main himself when he decides it's done.
- Commit your own work on your own branch as you go, with clear messages - your commits are your handoff to Zayah.
"@
$personas = @{
    cto   = "You are the CTO of Zayah's space startup (maneuver detection from public orbital data). You own technical direction: architecture, priorities, review standards, risk calls. You turn Zayah's goals into precise, written technical orders and honest assessments. Skeptical, brief, numbers over adjectives, no hype.$commonRules"
    tim   = "You are Tim, the software engineer / ML engineer of Zayah's space startup. You build and harden the code: the maneuver detector, data pipelines, tests, charts. Test-first where a test is possible; every claim ships with the number that proves it. When work is done, state plainly what was verified and what was not.$commonRules"
    mark  = "You are Mark, the marketer of Zayah's space startup: outreach, social, and income. You draft emails, find real human contacts, keep the outreach ledger honest, and think about who pays and why. You NEVER send anything - drafts only; Zayah sends. Write like one specific human to another; if it smells like spam, rewrite it.$commonRules"
    randy = "You are Randy, the researcher / brainstormer of Zayah's space startup. You dig into papers, competitors, orbital mechanics, and generate ideas. Separate VERIFIED (with source) from SPECULATION (labeled) in everything you produce. Wild ideas welcome, mislabeled facts are not.$commonRules"
    video = "You are the video editor / content producer for Zayah's channel 'Zayah in Orbit' - a 19-year-old building a space startup from his bedroom, documented as it actually happens. You turn the day's REAL events into episodes: outlines, titles, hooks, shot lists, shorts scripts, thumbnails ideas. Never invent or exaggerate events - the detector catching a real maneuver IS the drama. OPSEC duty: before anything is marked ready to publish, flag any frame or text that exposes real people's emails/contact info, auth files, or credentials - blur or cut, no exceptions.$commonRules"
}
foreach ($name in $personas.Keys) {
    Set-Content -Path (Join-Path $personaDir "$name.md") -Value $personas[$name] -Encoding UTF8
}

# --- Console look: per-title registry settings (conhost picks these up because the
# --- window is created with this exact title via `start "<title>"`).
foreach ($win in $layout) {
    $key = "HKCU:\Console\$($win.Title)"
    if (-not (Test-Path $key)) { New-Item -Path $key | Out-Null }
    Set-ItemProperty $key -Name FaceName     -Value 'Consolas' -Type String
    Set-ItemProperty $key -Name FontFamily   -Value 0x36       -Type DWord   # TrueType
    Set-ItemProperty $key -Name FontSize     -Value 0x120000   -Type DWord   # 18 pt
    Set-ItemProperty $key -Name FontWeight   -Value 400        -Type DWord
    Set-ItemProperty $key -Name ColorTable08 -Value $darkGrey   -Type DWord
    Set-ItemProperty $key -Name ScreenColors -Value $win.Colors -Type DWord
    Set-ItemProperty $key -Name QuickEdit    -Value 1          -Type DWord
    Set-ItemProperty $key -Name InsertMode   -Value 1          -Type DWord
}

# --- Per-window-slot session IDs, keyed to this folder, so `t` resumes where you were.
$munged   = ($Path -replace '[^A-Za-z0-9]', '-')
$sessDir  = Join-Path $env:USERPROFILE '.claude\t-sessions'
$sessFile = Join-Path $sessDir "$munged.json"

if (-not (Test-Path $sessDir)) { New-Item -ItemType Directory -Path $sessDir | Out-Null }
$sessions = @{}
if ((Test-Path $sessFile) -and -not $Fresh) {
    $obj = Get-Content $sessFile -Raw | ConvertFrom-Json
    foreach ($p in $obj.PSObject.Properties) { $sessions[$p.Name] = $p.Value }
}
foreach ($win in $layout) {
    if (-not $sessions[$win.Title]) { $sessions[$win.Title] = [guid]::NewGuid().ToString() }
}
$sessions | ConvertTo-Json | Set-Content -Path $sessFile -Encoding UTF8

# --- Worktrees: give each branch-bound window its own checkout.
$wtRoot = Join-Path $env:USERPROFILE '.claude\worktrees'
if (-not (Test-Path $wtRoot)) { New-Item -ItemType Directory -Path $wtRoot | Out-Null }
git -C $Path worktree prune 2>$null

function Ensure-Worktree($branch) {
    $null = git -C $Path rev-parse --verify --quiet $branch
    if ($LASTEXITCODE -ne 0) { return $null }   # branch doesn't exist here; caller falls back
    $wtPath = Join-Path $wtRoot "$munged-$branch"
    if (-not (Test-Path $wtPath)) {
        git -C $Path worktree add $wtPath $branch
        if (-not (Test-Path $wtPath)) { return $null }   # e.g. branch checked out elsewhere
        # Seed the gitignored things the code actually needs to run:
        foreach ($f in 'spacetrack_auth.json', 'gmail_auth.json') {
            $src = Join-Path $Path "06 Code\$f"
            if (Test-Path $src) { Copy-Item $src (Join-Path $wtPath "06 Code\$f") }
        }
        # One real SupGP archive, junction-linked everywhere (it's ~2 MB/day, forever).
        $arch = Join-Path $Path '06 Code\supgp_archive'
        if ((Test-Path $arch) -and -not (Test-Path (Join-Path $wtPath '06 Code\supgp_archive'))) {
            New-Item -ItemType Junction -Path (Join-Path $wtPath '06 Code\supgp_archive') -Target $arch | Out-Null
        }
    }
    return $wtPath
}

# --- Launch + snap into quadrants.
foreach ($win in $layout) {
    $launchDir = $Path
    if ($win.Branch) {
        $wt = Ensure-Worktree $win.Branch
        if ($wt) { $launchDir = $wt }
    }

    # Resume if this slot's session already has a transcript on disk; otherwise create it.
    # (Claude keys transcripts by the launch folder, so check against $launchDir.)
    $id = $sessions[$win.Title]
    $launchMunged = ($launchDir -replace '[^A-Za-z0-9]', '-')
    $personaFile = Join-Path $personaDir "$($win.Persona).md"
    $opts = "--model $($win.Model) --effort $($win.Effort) --append-system-prompt-file $personaFile"
    if (Test-Path (Join-Path $env:USERPROFILE ".claude\projects\$launchMunged\$id.jsonl")) {
        $inner = "claude --resume $id $opts"
    } else {
        $inner = "claude --session-id $id $opts"
    }
    Start-Process cmd -WorkingDirectory $launchDir -ArgumentList "/c start `"$($win.Title)`" cmd /k `"$inner`""

    # `start` returns immediately; cmd appends the running command to the title
    # ("Claude 1 - PLAN - HIGH - claude ..."), so find the newest cmd window whose
    # title STARTS with ours, then position it.
    $hwnd = [IntPtr]::Zero
    $deadline = (Get-Date).AddSeconds(8)
    while ($hwnd -eq [IntPtr]::Zero -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 150
        $proc = Get-Process cmd -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowTitle -like "$($win.Title)*" } |
            Sort-Object StartTime -Descending | Select-Object -First 1
        if ($proc) { $hwnd = $proc.MainWindowHandle }
    }
    if ($hwnd -ne [IntPtr]::Zero) {
        if ($win.Center) {
            $x = $wa.X + [math]::Floor(($wa.Width - $w) / 2)
            $y = $wa.Y + [math]::Floor(($wa.Height - $h) / 2)
        } else {
            $x = $wa.X + ($win.Col * $w)
            $y = $wa.Y + ($win.Row * $h)
        }
        [Win32.Native]::MoveWindow($hwnd, $x, $y, $w, $h, $true) | Out-Null
    }
}
