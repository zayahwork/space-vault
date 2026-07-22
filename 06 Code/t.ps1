# t.ps1 - launch 4 Claude Code cmd windows in a 2x2 grid, one per work stream.
#
#   t                 4 windows on the space project (see layout below)
#   t C:\SomeRepo     same grid in another folder (windows whose branch doesn't
#                     exist there just open in the folder itself)
#   t -Fresh          start all 4 with blank conversations instead of resuming
#
# Layout - each window is its own work stream on its own branch, in its own
# git worktree, so nothing collides:
#   Top-left     PLAN     high effort    master    the vault, planning, merges
#   Top-right    DETECTOR high effort    detector  maneuver detection builds
#   Bottom-left  OUTREACH medium effort  outreach  emails, contact checking
#   Bottom-right ROOM     low effort     room      crew tooling, quick questions
#
# Each window slot owns a permanent session ID, so closing the grid and typing `t`
# again resumes each window exactly where it left off. Use -Fresh to wipe that and
# start over (old sessions stay on disk; `claude --resume` can still find them).
#
# Worktrees live in ~\.claude\worktrees\. On creation, gitignored essentials are
# seeded in: auth files are copied, and the SupGP archive is junction-linked (one
# real archive on disk, visible from every stream).
param(
    [string]$Path = "C:\Space",
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

# ScreenColors: low nibble = text, high nibble = background.
# Palette slot 8 is repainted to a proper dark grey below (Windows' stock slot 8 is a
# washed-out #808080), so 0x8F = bright white text on dark grey.
$darkGrey = 0x2B2B2B   # conhost stores colours as 0x00BBGGRR - grey reads the same either way
$layout = @(
    @{ Effort = 'high';   Col = 0; Row = 0; Title = 'Claude 1 - PLAN - HIGH';       Branch = $null;       Colors = 0x0F },
    @{ Effort = 'high';   Col = 1; Row = 0; Title = 'Claude 2 - DETECTOR - HIGH';   Branch = 'detector';  Colors = 0x0F },
    @{ Effort = 'medium'; Col = 0; Row = 1; Title = 'Claude 3 - OUTREACH - MEDIUM'; Branch = 'outreach';  Colors = 0x0F },
    @{ Effort = 'low';    Col = 1; Row = 1; Title = 'Claude 4 - ROOM - LOW';        Branch = 'room';      Colors = 0x0F }
)

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
    if (Test-Path (Join-Path $env:USERPROFILE ".claude\projects\$launchMunged\$id.jsonl")) {
        $inner = "claude --resume $id --effort $($win.Effort)"
    } else {
        $inner = "claude --session-id $id --effort $($win.Effort)"
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
        $x = $wa.X + ($win.Col * $w)
        $y = $wa.Y + ($win.Row * $h)
        [Win32.Native]::MoveWindow($hwnd, $x, $y, $w, $h, $true) | Out-Null
    }
}
