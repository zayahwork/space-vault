@echo off
rem Space Night Shift - fired by Task Scheduler every 2h. Budget-gated (10 iterations/day
rem shared) and honors the STOP_LOOPS kill switch, so firing often never overspends.
powershell -ExecutionPolicy Bypass -Command "& 'C:\Space\06 Code\loop.ps1' run -Iterations 1"
