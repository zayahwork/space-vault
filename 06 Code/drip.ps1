# drip.ps1 - send a couple of outreach emails, then stop.
#
# Called on a schedule (see "Outreach Drip" in Task Scheduler). Each run sends at
# most 2. outreach.py enforces the real ceiling itself - DAILY_CAP, counted from
# the audit log - so running this more often cannot exceed 25 in a day. That
# means the schedule is a suggestion and the cap is the law, which is the right
# way round: a scheduler misfire cannot turn into a mail blast.
#
# Business hours only, on purpose. Mail that lands at 3am is buried under
# whatever arrives at 9am, and nobody is awake to notice if this misbehaves.
#
#   powershell -File drip.ps1            # send up to 2
#   powershell -File drip.ps1 -N 1       # slower
#   powershell -File drip.ps1 -DryRun    # show what would go, send nothing
param(
    [int]$N = 2,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py   = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
$log  = Join-Path $here "drip.log"

$args = @("outreach.py", "--send", "-n", "$N", "--gap", "45")
if (-not $DryRun) { $args += "--live" }

Set-Location $here
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"=== $stamp  (n=$N, dryrun=$DryRun)" | Out-File -FilePath $log -Append -Encoding utf8
& $py @args 2>&1 | Tee-Object -FilePath $log -Append

# Bounces are the whole point of tracking. A 5xx at send time is caught inline by
# outreach.py; the ones that arrive later, as mail, need this.
& $py "outreach.py" "--check-bounces" 2>&1 | Tee-Object -FilePath $log -Append
