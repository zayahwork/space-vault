# drip.ps1 - send a couple of outreach emails, then stop.
#
# Called on a schedule (see "Outreach Drip" in Task Scheduler). Each run sends at
# most a couple. outreach.py enforces the real ceiling itself - DAILY_CAP, counted
# from the audit log - so running this more often cannot exceed 25 in a day. That
# means the schedule is a suggestion and the cap is the law, which is the right
# way round: a scheduler misfire cannot turn into a mail blast.
#
# Business hours only, on purpose. Mail that lands at 3am is buried under
# whatever arrives at 9am, and nobody is awake to notice if this misbehaves.
#
# JITTER - why this script sleeps before it sends:
# The scheduler can only fire on an exact interval. Mail that leaves at 08:00:04,
# 09:00:04, 10:00:04 every single day, two at a time, twenty seconds apart, reads
# as a machine to anyone who looks at headers - and Gmail looks. A human writing
# to eight strangers does it in an uneven scatter: three before lunch, none for
# two hours, one at 4pm. So each run rolls dice:
#   - a random wait of 0..MaxJitterMin minutes before anything is sent
#   - a random SkipChance percent of runs send nothing at all
#   - a random 1-2 emails per run instead of always 2
#   - a random 35-95s gap between the sends inside a run
# The cap and the business-hours guard still hold; only the shape is random.
#
#   powershell -File drip.ps1                 # jittered, up to 2
#   powershell -File drip.ps1 -N 1            # slower
#   powershell -File drip.ps1 -NoJitter       # fire immediately (manual runs)
#   powershell -File drip.ps1 -DryRun         # show what would go, send nothing
param(
    [int]$N = 0,                  # 0 = roll for it (1 or 2)
    [int]$MaxJitterMin = 25,      # upper bound on the pre-send wait
    [int]$SkipChance = 20,        # percent of runs that send nothing
    [int]$OpenHour = 8,           # no sends before this hour, local
    [int]$CloseHour = 19,         # or after it
    [switch]$Weekends,            # allow Sat/Sun (off: nobody cold-mails Sunday)
    [switch]$NoJitter,            # skip the dice entirely - manual runs
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py   = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
$log  = Join-Path $here "drip.log"

function Say($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg"
    Write-Output $line
    $line | Out-File -FilePath $log -Append -Encoding utf8
}

Set-Location $here
Say "=== run start (N=$N, jitter<=${MaxJitterMin}m, skip=${SkipChance}%, dryrun=$DryRun)"

if (-not $NoJitter) {
    # Weekend and after-hours guards come BEFORE the sleep - no point waiting
    # twenty minutes to discover it's Sunday.
    $now = Get-Date
    if ((-not $Weekends) -and (@('Saturday','Sunday') -contains $now.DayOfWeek.ToString())) {
        Say "skip: $($now.DayOfWeek). Cold mail on a weekend gets read Monday at best."
        exit 0
    }

    if ((Get-Random -Minimum 0 -Maximum 100) -lt $SkipChance) {
        Say "skip: rolled a quiet hour ($SkipChance% chance). Nothing sent."
        exit 0
    }

    $wait = Get-Random -Minimum 0 -Maximum ($MaxJitterMin * 60 + 1)
    $land = (Get-Date).AddSeconds($wait)
    # The wait must not push the send past closing time, or out of the hour the
    # scheduler intended. Landing at 19:04 because the dice said so is exactly
    # the machine-shaped behaviour this is meant to avoid.
    if ($land.Hour -lt $OpenHour -or $land.Hour -ge $CloseHour) {
        Say ("skip: jitter would land at {0:HH:mm}, outside {1:00}:00-{2:00}:00." -f $land, $OpenHour, $CloseHour)
        exit 0
    }
    Say ("waiting {0}m{1:00}s - sending around {2:HH:mm}" -f [int]($wait / 60), ($wait % 60), $land)
    Start-Sleep -Seconds $wait
}

if ($N -le 0) {
    # Mostly one, sometimes two. Averages a bit over one an hour, which across a
    # jittered eleven-hour window lands comfortably under the 25/day cap and
    # looks like someone working through a list, not a mail merge.
    $N = Get-Random -InputObject @(1, 1, 1, 2, 2)
}
$gap = Get-Random -Minimum 35 -Maximum 95

$sendArgs = @("outreach.py", "--send", "-n", "$N", "--gap", "$gap")
if (-not $DryRun) { $sendArgs += "--live" }

Say "sending up to $N, ${gap}s apart"

# Tee-Object -Append writes UTF-16 by default in PS 5.1, which turns a log the
# rest of this script writes as UTF-8 into interleaved mojibake. Write both
# streams by hand instead.
function Run($tool, $arguments) {
    $out = & $tool @arguments 2>&1 | Out-String
    Write-Output $out
    $out | Out-File -FilePath $log -Append -Encoding utf8
}

Run $py $sendArgs

# Bounces are the whole point of tracking. A 5xx at send time is caught inline by
# outreach.py; the ones that arrive later, as mail, need this.
Run $py @("outreach.py", "--check-bounces")
