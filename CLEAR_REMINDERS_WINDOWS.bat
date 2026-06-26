@echo off
setlocal
title JARVIS - Clear Reminders
echo JARVIS: clearing local reminders...
set "HERE=%~dp0"
if not exist "%HERE%data" mkdir "%HERE%data"
> "%HERE%data\reminders.json" echo []
if not exist "%APPDATA%\JARVIS\data" mkdir "%APPDATA%\JARVIS\data"
> "%APPDATA%\JARVIS\data\reminders.json" echo []
echo Done. Reminders cleared in portable and installed data folders.
echo Restart JARVIS if it is already open.
pause
