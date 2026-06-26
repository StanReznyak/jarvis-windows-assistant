@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PY_EXE="
set "PY_LAUNCHER="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if "%PY_EXE%"=="" if exist "venv\Scripts\python.exe" set "PY_EXE=venv\Scripts\python.exe"

if "%PY_EXE%"=="" (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.12 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY_LAUNCHER=py -3.12"
    if "%PY_LAUNCHER%"=="" py -3.11 -c "import sys" >nul 2>nul
    if "%PY_LAUNCHER%"=="" if not errorlevel 1 set "PY_LAUNCHER=py -3.11"
    if "%PY_LAUNCHER%"=="" py -3 -c "import sys" >nul 2>nul
    if "%PY_LAUNCHER%"=="" if not errorlevel 1 set "PY_LAUNCHER=py -3"
  )
)
if "%PY_EXE%"=="" if "%PY_LAUNCHER%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PY_LAUNCHER=python"
)

if "%PY_EXE%"=="" (
  if "%PY_LAUNCHER%"=="" goto python_error
  echo Creating virtual environment with %PY_LAUNCHER% ...
  %PY_LAUNCHER% -m venv .venv
  if errorlevel 1 goto venv_error
  set "PY_EXE=.venv\Scripts\python.exe"
)

echo Updating pip...
"%PY_EXE%" -m pip install --upgrade pip
if errorlevel 1 goto pip_error

echo Installing requirements...
"%PY_EXE%" -m pip install -r requirements.txt
if errorlevel 1 goto pip_error

echo Dependencies installed.
if not "%JARVIS_REQ_NOPAUSE%"=="1" pause
exit /b 0

:python_error
echo ERROR: Python not found.
echo Install Python 3.11 or 3.12 and enable Add python.exe to PATH.
if not "%JARVIS_REQ_NOPAUSE%"=="1" pause
exit /b 1

:venv_error
echo ERROR: Cannot create virtual environment.
echo Try running this manually: py -3.12 -m venv .venv
if not "%JARVIS_REQ_NOPAUSE%"=="1" pause
exit /b 2

:pip_error
echo ERROR: Cannot install dependencies.
echo Check internet connection and Python version.
if not "%JARVIS_REQ_NOPAUSE%"=="1" pause
exit /b 3
