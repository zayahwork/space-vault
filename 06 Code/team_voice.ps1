# team_voice.ps1 - give the standup team speaking voices.
#
# Windows ships two TTS voices (David, Zira). We get five distinguishable
# speakers out of them by shifting pitch and rate per persona via SSML.
# No installs, no API keys, no network - this runs entirely offline.
#
# Talking BACK to them needs no software either: press Win+H anywhere and
# Windows dictates your speech straight into the terminal.
#
# Usage:
#   .\team_voice.ps1 -List
#   .\team_voice.ps1 -Persona Rook -Text 'the pipeline falls over at scale'
#   .\team_voice.ps1 -File .\standup.txt
#   .\team_voice.ps1 -Persona Nova -Text 'hi' -ToWav out.wav   (silent test)
#
# ASCII only on purpose: this file gets round-tripped through PowerShell,
# which mangles non-ASCII punctuation into mojibake.

[CmdletBinding()]
param(
    [string]$Persona = 'CTO',
    [string]$Text,
    [string]$File,
    [string]$ToWav,
    [switch]$List
)

Add-Type -AssemblyName System.Speech

# Pitch and rate are the only knobs SAPI gives us - tune to taste.
$Cast = @{
    'CTO'   = @{ Voice = 'Microsoft David Desktop'; Pitch = '+0%';  Rate = 0;  Role = 'CTO' }
    'Rook'  = @{ Voice = 'Microsoft David Desktop'; Pitch = '-15%'; Rate = 1;  Role = 'Software Engineer' }
    'Fitz'  = @{ Voice = 'Microsoft David Desktop'; Pitch = '+18%'; Rate = 2;  Role = 'Debugger' }
    'Vega'  = @{ Voice = 'Microsoft Zira Desktop';  Pitch = '+12%'; Rate = 2;  Role = 'Marketing' }
    'Sable' = @{ Voice = 'Microsoft Zira Desktop';  Pitch = '-12%'; Rate = 0;  Role = 'ML Engineer' }
    'Nova'  = @{ Voice = 'Microsoft Zira Desktop';  Pitch = '+0%';  Rate = -2; Role = 'Explainer' }
}

function Invoke-Line {
    param([string]$Who, [string]$Line, [string]$WavPath)

    if (-not $Cast.ContainsKey($Who)) {
        Write-Warning ('unknown persona ' + $Who + ' - using CTO')
        $Who = 'CTO'
    }
    $part = $Cast[$Who]

    # SSML must be XML-clean or SAPI throws rather than degrading.
    $safe = $Line -replace '&', ' and ' -replace '<', '' -replace '>', ''

    # Rate goes through the native SAPI property (-10..10, well defined).
    # SSML's rate attribute is ambiguous across engines - it read '0' as
    # near-silent-slow and '2' as double speed, which is not what we meant.
    # Pitch has no native property, so that stays in SSML.
    $q = [char]34
    $ssml = '<speak version=' + $q + '1.0' + $q +
            ' xmlns=' + $q + 'http://www.w3.org/2001/10/synthesis' + $q +
            ' xml:lang=' + $q + 'en-US' + $q + '>' +
            '<voice name=' + $q + $part.Voice + $q + '>' +
            '<prosody pitch=' + $q + $part.Pitch + $q + '>' +
            $safe +
            '</prosody></voice></speak>'

    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try {
        if ($WavPath) { $synth.SetOutputToWaveFile($WavPath) }
        $synth.Rate = $part.Rate
        Write-Host ($Who.PadRight(6) + ' [' + $part.Role + ']') -ForegroundColor Cyan
        $synth.SpeakSsml($ssml)
    }
    finally {
        $synth.Dispose()
    }
}

if ($List) {
    Write-Host 'Cast:'
    foreach ($k in ($Cast.Keys | Sort-Object)) {
        Write-Host ('  ' + $k.PadRight(6) + ' [' + $Cast[$k].Role.PadRight(18) + '] ' + $Cast[$k].Voice)
    }
    Write-Host ''
    Write-Host 'Installed voices:'
    $probe = New-Object System.Speech.Synthesis.SpeechSynthesizer
    foreach ($v in $probe.GetInstalledVoices()) { Write-Host ('  ' + $v.VoiceInfo.Name) }
    $probe.Dispose()
    return
}

if ($File) {
    if (-not (Test-Path $File)) { throw ('no such file: ' + $File) }
    # Each line looks like:  Rook: what they said
    foreach ($raw in (Get-Content $File)) {
        if ([string]::IsNullOrWhiteSpace($raw)) { continue }
        if ($raw.TrimStart().StartsWith('#')) { continue }
        if ($raw -match '^\s*(\w+)\s*:\s*(.+)$') {
            Invoke-Line -Who $Matches[1] -Line $Matches[2]
        }
        else {
            Invoke-Line -Who 'Nova' -Line $raw
        }
    }
}
elseif ($Text) {
    Invoke-Line -Who $Persona -Line $Text -WavPath $ToWav
}
else {
    throw 'give me -Text or -File, or -List to see the cast'
}
