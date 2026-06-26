@echo off
setlocal EnableExtensions
title JARVIS Local Model Check

echo ==============================================
echo  JARVIS Local Model Check
echo ==============================================
echo.
call :find_ollama
if not defined OLLAMA_EXE (
  echo Ollama not found.
  echo Run SETUP_LOCAL_MODEL_WINDOWS.bat first.
  pause
  exit /b 1
)
echo Found Ollama: %OLLAMA_EXE%
echo.
echo Starting Ollama service if needed...
start "" /min "%OLLAMA_EXE%" serve >nul 2>nul
timeout /t 3 /nobreak >nul 2>nul

echo.
echo Installed models:
"%OLLAMA_EXE%" list

echo.
echo Testing model llama3.2:1b...
"%OLLAMA_EXE%" run llama3.2:1b "Say OK in one short Russian sentence."
if errorlevel 1 (
  echo.
  echo Model test failed. Run SETUP_LOCAL_MODEL_WINDOWS.bat again.
  pause
  exit /b 1
)

echo.
echo DONE. If JARVIS was open, restart it.
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
