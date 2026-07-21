# The room, with faces. Opens a browser; talk out loud.
#   .\jarvis.ps1                 local + free (llama3)
#   .\jarvis.ps1 --brain claude  sharper (needs ANTHROPIC_API_KEY)
#   .\jarvis.ps1 --no-mic        type only
#   .\jarvis.ps1 --list-mics
& "$PSScriptRoot\.venv-meeting\Scripts\python.exe" "$PSScriptRoot\roomserver.py" @args
