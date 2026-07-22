# The room, with faces. Opens a browser; talk out loud.
#
#   .\jarvis.ps1                     free + sharp. Claude Code headless, no API key.
#   .\jarvis.ps1 --auto              claimed jobs run without asking you first
#   .\jarvis.ps1 --no-work           talking only; jobs are logged, never run
#   .\jarvis.ps1 --no-mic            type only
#   .\jarvis.ps1 --brain ollama      fully offline, and it invents details
#   .\jarvis.ps1 --list-mics
#
# The default brain rides the Claude Code subscription already signed in here.
# No ANTHROPIC_API_KEY, no separate bill - but it does draw on your plan usage.
# When someone claims a job it goes to a real Claude Code session with tools,
# running as that person, and nothing touches the vault until you press Do it.
& "$PSScriptRoot\.venv-meeting\Scripts\python.exe" "$PSScriptRoot\roomserver.py" @args
