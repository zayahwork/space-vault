# Open the room. Everything after this line is passed through, so:
#   .\room.ps1              the room, local + free
#   .\room.ps1 --hear       ears only, check the mic
#   .\room.ps1 --bench      measure the loop
#   .\room.ps1 --tts edge   real Irish + Australian accents
& "$PSScriptRoot\.venv-meeting\Scripts\python.exe" "$PSScriptRoot\room.py" @args
