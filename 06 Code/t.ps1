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
    [switch]$Fresh,
    [switch]$Diag      # print what this machine actually sees, then still launch
)

if (-not (Test-Path -LiteralPath $Path)) { Write-Error "No such folder: $Path"; exit 1 }
$Path = (Resolve-Path -LiteralPath $Path).Path

Add-Type -Namespace Win32 -Name Native -MemberDefinition @'
[DllImport("user32.dll")]
public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
[DllImport("user32.dll")]
public static extern bool BringWindowToTop(IntPtr hWnd);
[DllImport("user32.dll")]
public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")]
public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
public struct RECT { public int Left, Top, Right, Bottom; }
'@
# Laptops usually run display scaling (125-200%). Without this, Windows lies to us about
# the screen size and every window lands in the wrong place at the wrong size.
[Win32.Native]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Windows.Forms

$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$w  = [math]::Floor($wa.Width / 2)
$h  = [math]::Floor($wa.Height / 2)

# Font must fit the quadrant, not the other way round: an 18pt console cannot shrink into
# a small laptop quadrant, so Windows refuses to move it and the grid "scatters".
$fontPt = if ($w -ge 900 -and $h -ge 480) { 18 } elseif ($w -ge 700 -and $h -ge 380) { 14 } else { 11 }
$charW  = [math]::Max(6, [math]::Round($fontPt * (96/72) * 0.55))
$charH  = [math]::Max(10, [math]::Round($fontPt * (96/72) * 1.17))
$cols   = [math]::Max(40, [math]::Floor(($w - 24) / $charW))
$rows   = [math]::Max(12, [math]::Floor(($h - 48) / $charH))
$fontVal   = $fontPt -shl 16                    # FontSize: height<<16 (width 0 = auto)
$winSize   = ($rows -shl 16) -bor $cols         # WindowSize: rows<<16 | cols
$buffSize  = (9999 -shl 16) -bor $cols          # big scrollback, same width

if ($Diag) {
    Write-Host "=== t diagnostics ===" -ForegroundColor Cyan
    Write-Host "vault      : $Path"
    Write-Host "screen     : $($wa.Width) x $($wa.Height) (DPI-aware)"
    Write-Host "quadrant   : $w x $h"
    Write-Host "font       : ${fontPt}pt -> console $cols x $rows"
    $cl = (Get-Command claude -ErrorAction SilentlyContinue)
    Write-Host "claude     : $(if ($cl) { $cl.Source } else { 'NOT FOUND on PATH' })"
    Write-Host "version    : $(try { (claude --version 2>&1 | Select-Object -First 1) } catch { 'n/a' })"
    Write-Host "git head   : $(git -C $Path log --oneline -1 2>&1)"
    Write-Host "====================" -ForegroundColor Cyan
}

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
    Set-ItemProperty $key -Name FaceName         -Value 'Consolas' -Type String
    Set-ItemProperty $key -Name FontFamily       -Value 0x36       -Type DWord   # TrueType
    Set-ItemProperty $key -Name FontSize         -Value $fontVal   -Type DWord   # sized to fit the quadrant
    Set-ItemProperty $key -Name FontWeight       -Value 400        -Type DWord
    Set-ItemProperty $key -Name WindowSize       -Value $winSize   -Type DWord
    Set-ItemProperty $key -Name ScreenBufferSize -Value $buffSize  -Type DWord
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

# --- Phase 1: launch ALL windows at once (no waiting between them).
foreach ($win in $layout) {
    $launchDir = $Path
    if ($win.Branch) {
        $wt = Ensure-Worktree $win.Branch
        if ($wt) { $launchDir = $wt }
    }

    # Resume if this slot's session already has a transcript on disk; otherwise create it.
    # (Claude keys transcripts by the launch folder, so check against $launchDir.)
    $id = $sessions[$win.Title]
    $win.Sid = $id
    $launchMunged = ($launchDir -replace '[^A-Za-z0-9]', '-')
    $personaFile = Join-Path $personaDir "$($win.Persona).md"
    $opts = "--model $($win.Model) --effort $($win.Effort) --append-system-prompt-file $personaFile"
    # Clear inherited child-session markers first (if t was started from inside a Claude
    # session, they'd silently turn transcript saving OFF and kill session resume).
    $clean = "set CLAUDE_CODE_CHILD_SESSION=&set CLAUDECODE=&"
    if (Test-Path (Join-Path $env:USERPROFILE ".claude\projects\$launchMunged\$id.jsonl")) {
        $inner = "$clean claude --resume $id $opts"
    } else {
        $inner = "$clean claude --session-id $id $opts"
    }
    Start-Process cmd -WindowStyle Hidden -WorkingDirectory $launchDir `
        -ArgumentList "/c start `"$($win.Title)`" cmd /k `"$inner`""
}

# --- Phase 2: snap each window into place. Claude retitles windows seconds after boot,
# --- so titles are useless - instead each window's command line contains its unique
# --- session ID, which is how we tell them apart no matter what they call themselves.
$pending  = [System.Collections.ArrayList]@($layout)
$deadline = (Get-Date).AddSeconds(25)
while ($pending.Count -gt 0 -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 200
    $cmds = Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" -ErrorAction SilentlyContinue
    foreach ($win in @($pending)) {
        $owner = $cmds | Where-Object { $_.CommandLine -like "*$($win.Sid)*" } | Select-Object -First 1
        if (-not $owner) { continue }
        $gp = Get-Process -Id $owner.ProcessId -ErrorAction SilentlyContinue
        if (-not $gp -or $gp.MainWindowHandle -eq 0) { continue }
        if ($win.Center) {
            $x = $wa.X + [math]::Floor(($wa.Width - $w) / 2)
            $y = $wa.Y + [math]::Floor(($wa.Height - $h) / 2)
        } else {
            $x = $wa.X + ($win.Col * $w)
            $y = $wa.Y + ($win.Row * $h)
        }
        [Win32.Native]::MoveWindow($gp.MainWindowHandle, $x, $y, $w, $h, $true) | Out-Null
        $win.Hwnd = $gp.MainWindowHandle
        $pending.Remove($win)
    }
}
if ($pending.Count -gt 0) {
    Write-Warning "Could not position: $(($pending | ForEach-Object Title) -join ', ')"
}
if ($Diag) {
    foreach ($win in $layout) {
        if (-not $win.Hwnd) { Write-Host "$($win.Title): NO WINDOW"; continue }
        $r = New-Object Win32.Native+RECT
        [Win32.Native]::GetWindowRect($win.Hwnd, [ref]$r) | Out-Null
        $wantX = if ($win.Center) { $wa.X + [math]::Floor(($wa.Width - $w)/2) } else { $wa.X + ($win.Col * $w) }
        $wantY = if ($win.Center) { $wa.Y + [math]::Floor(($wa.Height - $h)/2) } else { $wa.Y + ($win.Row * $h) }
        $got = "$($r.Left),$($r.Top) $($r.Right - $r.Left)x$($r.Bottom - $r.Top)"
        $ok  = if ([math]::Abs($r.Left - $wantX) -le 8 -and [math]::Abs($r.Top - $wantY) -le 8) { 'OK  ' } else { 'OFF ' }
        Write-Host "$ok $($win.Title): wanted $wantX,$wantY ${w}x${h} | got $got"
    }
}
# The centered window (VIDEO) belongs on top of the grid regardless of launch order.
foreach ($win in $layout) {
    if ($win.Center -and $win.Hwnd) { [Win32.Native]::BringWindowToTop($win.Hwnd) | Out-Null }
}
