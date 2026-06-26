@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title JARVIS start

echo ========================================
echo JARVIS v8.4 start
echo ========================================
echo Folder: %CD%
echo.

if not exist "main.py" (
  echo ERROR: main.py not found.
  echo Run this file from the extracted JARVIS folder, not from ZIP preview.
  echo.
  pause
  exit /b 1
)

set "PY_EXE="
set "PY_LAUNCHER="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if "%PY_EXE%"=="" if exist "venv\Scripts\python.exe" set "PY_EXE=venv\Scripts\python.exe"

if "%PY_EXE%"=="" (
  echo Preparing Python environment. First start can take a few minutes...
  echo.
  set "JARVIS_REQ_NOPAUSE=1"
  call install_requirements.bat
  set "JARVIS_REQ_NOPAUSE="
  if errorlevel 1 (
    echo.
    echo ERROR: dependency setup failed.
    echo Try installing Python 3.11 or 3.12 and run this file again.
    echo.
    pause
    exit /b 2
  )
  set "PY_EXE=.venv\Scripts\python.exe"
)

if not exist "%PY_EXE%" (
  echo ERROR: Python executable not found: %PY_EXE%
  echo.
  pause
  exit /b 3
)

echo Starting JARVIS...
echo Python: %PY_EXE%
echo.
"%PY_EXE%" main.py
set "JARVIS_EXIT_CODE=%ERRORLEVEL%"

echo.
echo JARVIS closed. Exit code: %JARVIS_EXIT_CODE%
echo.
pause
exit /b %JARVIS_EXIT_CODE%
