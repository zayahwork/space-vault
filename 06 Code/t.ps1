# t.ps1 - launch 4 Claude Code cmd windows in a 2x2 grid, like the Zen van Riel setup.
#
#   t                 4 windows in C:\Space  (top: HIGH+HIGH, bottom: MEDIUM+LOW)
#   t C:\SomeRepo     same grid, but in another folder
#   t -Fresh          start all 4 with blank conversations instead of resuming
#
# Each window slot owns a permanent session ID, so closing the grid and typing `t`
# again resumes each window exactly where it left off. Use -Fresh to wipe that and
# start over (old sessions stay on disk; `claude --resume` can still find them).
#
# Top-left / top-right  = high effort  -> big planning + feature work
# Bottom-left           = medium       -> normal tasks
# Bottom-right          = low          -> quick questions, cheap and fast
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
# HIGH = bright white on black, MEDIUM = white on dark blue, LOW = white on dark green.
$layout = @(
    @{ Effort = 'high';   Col = 0; Row = 0; Title = 'Claude 1 - HIGH';   Colors = 0x0F },
    @{ Effort = 'high';   Col = 1; Row = 0; Title = 'Claude 2 - HIGH';   Colors = 0x0F },
    @{ Effort = 'medium'; Col = 0; Row = 1; Title = 'Claude 3 - MEDIUM'; Colors = 0x1F },
    @{ Effort = 'low';    Col = 1; Row = 1; Title = 'Claude 4 - LOW';    Colors = 0x2F }
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
    Set-ItemProperty $key -Name ScreenColors -Value $win.Colors -Type DWord
    Set-ItemProperty $key -Name QuickEdit    -Value 1          -Type DWord
    Set-ItemProperty $key -Name InsertMode   -Value 1          -Type DWord
}

# --- Per-window-slot session IDs, keyed to this folder, so `t` resumes where you were.
$munged   = ($Path -replace '[^A-Za-z0-9]', '-')
$sessDir  = Join-Path $env:USERPROFILE '.claude\t-sessions'
$sessFile = Join-Path $sessDir "$munged.json"
$projDir  = Join-Path $env:USERPROFILE ".claude\projects\$munged"

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

# --- Launch + snap into quadrants.
foreach ($win in $layout) {
    $id = $sessions[$win.Title]
    # Resume if this slot's session already has a transcript on disk; otherwise create it.
    if (Test-Path (Join-Path $projDir "$id.jsonl")) {
        $inner = "claude --resume $id --effort $($win.Effort)"
    } else {
        $inner = "claude --session-id $id --effort $($win.Effort)"
    }
    Start-Process cmd -WorkingDirectory $Path -ArgumentList "/c start `"$($win.Title)`" cmd /k `"$inner`""

    # `start` returns immediately; cmd appends the running command to the title
    # ("Claude 1 - HIGH - claude ..."), so find the newest cmd window whose title
    # STARTS with ours, then position it.
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
