@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title JARVIS Local Model Setup

echo.
echo ==============================================
echo  JARVIS Local Model Setup
echo ==============================================
echo.
echo This will prepare local model answers for JARVIS.
echo It checks Ollama and downloads model: llama3.2:1b
echo Internet is required for install/download.
echo.
echo Local Windows commands work even without this setup.
echo.
pause

call :find_ollama
if defined OLLAMA_EXE goto start_server

echo.
echo Ollama not found.
if exist "%~dp0tools\ollama\OllamaSetup.exe" goto bundled_installer

echo.
echo [1/3] Trying to install Ollama with winget...
where winget >nul 2>nul
if errorlevel 1 goto no_winget

winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements

echo.
echo Re-checking Ollama...
call :find_ollama
if defined OLLAMA_EXE goto start_server

echo.
echo Ollama may be installed, but Windows PATH is not updated yet.
echo Try closing this window, restart Windows or log out/in, then run this BAT again.
echo If it still fails, install Ollama from the official site and run this BAT again.
pause
exit /b 1

:bundled_installer
echo.
echo [1/3] Running bundled Ollama installer...
start /wait "" "%~dp0tools\ollama\OllamaSetup.exe"
call :find_ollama
if defined OLLAMA_EXE goto start_server
echo Installer finished, but ollama is not visible yet.
echo Restart Windows or log out/in, then run this BAT again.
pause
exit /b 1

:no_winget
echo.
echo winget not found. Opening official Ollama download page...
start "" "https://ollama.com/download/windows"
echo Install Ollama, then run this BAT again.
pause
exit /b 1

:start_server
echo.
echo Found Ollama: %OLLAMA_EXE%
echo [2/3] Starting Ollama service if needed...
start "" /min "%OLLAMA_EXE%" serve >nul 2>nul
timeout /t 3 /nobreak >nul 2>nul

echo.
echo [3/3] Pulling llama3.2:1b model...
"%OLLAMA_EXE%" pull llama3.2:1b
if errorlevel 1 (
  echo.
  echo Model download failed. Check internet and free disk space.
  pause
  exit /b 1
)

echo.
echo Checking installed models...
"%OLLAMA_EXE%" list

echo.
echo ==============================================
echo  DONE. Restart JARVIS now.
echo ==============================================
echo.
pause
exit /b 0

:find_ollama
set "OLLAMA_EXE="
for %%I in (ollama.exe) do if not "%%~$PATH:I"=="" set "OLLAMA_EXE=%%~$PATH:I"
if defined OLLAMA_EXE exit /b 0
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if defined OLLAMA_EXE exit /b 0
if exist "%LOCALAPPDATA%\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Ollama\ollama.exe"
if defined OLLAMA_EXE exit /b 0
if exist "%ProgramFiles%\Ollama\ollama.exe" set "OLLAMA_EXE=%ProgramFiles%\Ollama\ollama.exe"
if defined OLLAMA_EXE exit /b 0
if exist "%ProgramFiles(x86)%\Ollama\ollama.exe" set "OLLAMA_EXE=%ProgramFiles(x86)%\Ollama\ollama.exe"
exit /b 0
