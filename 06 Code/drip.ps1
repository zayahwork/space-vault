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
    [int]$N = 0,                  # 0 = let the pacer decide
    [int]$DailyTarget = 8,        # emails a day. The cap (25) is still the law.
                                  # 8, not 12, because that is what the queue can
                                  # actually feed - see Volume Pass - What the Drip
                                  # Can Actually Reach. Raise it when inventory allows.
    [int]$MaxJitterMin = 25,      # upper bound on the pre-send wait
    [int]$SkipChance = 15,        # percent of runs that send nothing even when behind
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
Say "=== run start (target=$DailyTarget/day, jitter<=${MaxJitterMin}m, skip=${SkipChance}%, dryrun=$DryRun)"

# PREFLIGHT. Both of these fail in ways that look like "a quiet day": missing
# credentials means every send dies inside Python, and an empty queue means the
# drip runs all day and mails nobody. Both must be loud in the log, not silent.
if (-not $DryRun -and -not (Test-Path (Join-Path $here "gmail_auth.json"))) {
    Say "STOP: no gmail_auth.json in $here - nothing can send from this tree."
    exit 1
}
try {
    $ready = [int](& $py "outreach.py" "--count-ready" | Select-Object -Last 1)
    if ($ready -lt 5) { Say "LOW QUEUE: only $ready sendable rows left - refill outreach_targets.csv." }
} catch { }

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
    # PACING. A fixed 1-2 per run either misses the daily number or overshoots it,
    # because runs get skipped, jitter drops some, and the sendable pool changes
    # under us. So each run asks a different question: given the time of day, how
    # far behind the daily target are we, and send that much.
    #
    # Behind pace -> catch up (bounded by MAX_PER_RUN inside outreach.py).
    # On pace     -> usually nothing, sometimes one, so the rhythm stays uneven.
    # The result is a day that reliably lands near the target without ever
    # looking like a scheduler: bursty early, quiet mid-afternoon, a straggler at 5.
    $already = 0
    try { $already = [int](& $py "outreach.py" "--count-today" | Select-Object -Last 1) } catch { }

    $now = Get-Date
    $windowHours = $CloseHour - $OpenHour
    $elapsed = [Math]::Max(0.0, [Math]::Min(1.0,
        (($now.Hour - $OpenHour) + ($now.Minute / 60.0)) / $windowHours))
    # +1 so the first run of the day isn't told it's already on pace at zero sent.
    $expected = [Math]::Ceiling($DailyTarget * $elapsed) + 1
    $deficit  = [int]$expected - $already

    if ($deficit -ge 1) {
        $N = [Math]::Min($deficit, 3)          # never more than 3 in one burst
    } else {
        $N = Get-Random -InputObject @(0, 0, 1)
    }
    Say ("pace: $already sent, ~$expected expected by {0:HH:mm} -> N=$N" -f $now)
    if ($N -le 0) { Say "on pace - nothing this run."; exit 0 }
}
$gap = Get-Random -Minimum 35 -Maximum 95

# --mix rotates across segments so a day is never nine insurers in a row: a bad
# segment shows up the same day instead of burning the whole queue first.
$sendArgs = @("outreach.py", "--send", "--mix", "-n", "$N", "--gap", "$gap")
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
