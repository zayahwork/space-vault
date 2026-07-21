@echo off
REM The room, with faces. Double-click this, or run  jarvis  from a terminal.
REM
REM This is a .cmd on purpose: PowerShell refuses to run unsigned .ps1 files
REM under the default Restricted policy, and changing that policy is a bigger
REM decision than opening a meeting should require.
REM
REM   jarvis                  local + free
REM   jarvis --brain claude   sharper, needs ANTHROPIC_API_KEY
REM   jarvis --no-mic         type only
REM   jarvis --auto           let the room run work without asking first
"%~dp0.venv-meeting\Scripts\python.exe" "%~dp0roomserver.py" %*
