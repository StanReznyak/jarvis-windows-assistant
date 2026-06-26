@echo off
cd /d "%~dp0"
if not exist data mkdir data
if not exist data\config.json copy /Y config.example.json data\config.json >nul
echo Config prepared.
pause
