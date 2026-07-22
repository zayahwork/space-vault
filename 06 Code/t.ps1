# t.ps1 - launch 4 Claude Code windows in a 2x2 grid, like the Zen van Riel setup.
#
#   t                 4 windows in C:\Space  (top: HIGH+HIGH, bottom: MEDIUM+LOW)
#   t C:\SomeRepo     same grid, but in another folder
#
# Top-left / top-right  = high effort  -> big planning + feature work
# Bottom-left           = medium       -> normal tasks
# Bottom-right          = low          -> quick questions, cheap and fast
param([string]$Path = "C:\Space")

if (-not (Test-Path -LiteralPath $Path)) { Write-Error "No such folder: $Path"; exit 1 }

Add-Type -AssemblyName System.Windows.Forms
Add-Type -Namespace Win32 -Name Native -MemberDefinition @'
[DllImport("user32.dll")]
public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
'@

$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$w  = [math]::Floor($wa.Width / 2)
$h  = [math]::Floor($wa.Height / 2)

$layout = @(
    @{ Effort = 'high';   Col = 0; Row = 0; Title = 'Claude 1 - HIGH'   },
    @{ Effort = 'high';   Col = 1; Row = 0; Title = 'Claude 2 - HIGH'   },
    @{ Effort = 'medium'; Col = 0; Row = 1; Title = 'Claude 3 - MEDIUM' },
    @{ Effort = 'low';    Col = 1; Row = 1; Title = 'Claude 4 - LOW'    }
)

foreach ($win in $layout) {
    $cmd = "title $($win.Title) && claude --effort $($win.Effort)"
    $p = Start-Process cmd -WorkingDirectory $Path -ArgumentList '/k', $cmd -PassThru

    # Wait for the console window to exist, then snap it into its quadrant.
    $deadline = (Get-Date).AddSeconds(8)
    while ($p.MainWindowHandle -eq 0 -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 150
        $p.Refresh()
    }
    if ($p.MainWindowHandle -ne 0) {
        $x = $wa.X + ($win.Col * $w)
        $y = $wa.Y + ($win.Row * $h)
        [Win32.Native]::MoveWindow($p.MainWindowHandle, $x, $y, $w, $h, $true) | Out-Null
    }
}
