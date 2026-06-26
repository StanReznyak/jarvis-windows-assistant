@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "JARVIS_BUILD_NOPAUSE="
set "NO_PAUSE=0"
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ========================================
echo JARVIS v8.4 EXE build
echo ========================================
echo.

echo [1/7] Stopping old JARVIS.exe if it is running...
taskkill /F /IM JARVIS.exe >nul 2>nul
timeout /t 1 /nobreak >nul 2>nul

echo [2/7] Preparing Python environment...
set "PY_EXE="
set "PY_LAUNCHER="
if exist .venv\Scripts\python.exe set "PY_EXE=.venv\Scripts\python.exe"
if "%PY_EXE%"=="" if exist venv\Scripts\python.exe set "PY_EXE=venv\Scripts\python.exe"
if "%PY_EXE%"=="" (
  where py >nul 2>nul
  if not errorlevel 1 set "PY_LAUNCHER=py -3"
)
if "%PY_EXE%"=="" if "%PY_LAUNCHER%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PY_LAUNCHER=python"
)
if "%PY_EXE%"=="" (
  if "%PY_LAUNCHER%"=="" goto :python_error
  %PY_LAUNCHER% -m venv .venv
  if errorlevel 1 goto :venv_error
  set "PY_EXE=.venv\Scripts\python.exe"
)

%PY_EXE% -m pip install --upgrade pip
if errorlevel 1 goto :pip_error
if not exist .venv\.deps_installed (
  %PY_EXE% -m pip install -r requirements.txt
  if errorlevel 1 goto :pip_error
  echo ok>.venv\.deps_installed
)
%PY_EXE% -m pip install pyinstaller pyinstaller-hooks-contrib soundfile
if errorlevel 1 goto :pip_error

echo [3/7] Cleaning previous build folders...
if exist build rmdir /s /q build
if exist dist\JARVIS.exe del /f /q dist\JARVIS.exe >nul 2>nul
if exist dist rmdir /s /q dist
if exist dist (
  echo.
  echo ERROR: Cannot delete old dist folder.
  echo Close JARVIS, close tray icon, close Explorer windows opened inside dist,
  echo then run this file again. If needed, reboot Windows.
  if "%NO_PAUSE%"=="0" pause
  exit /b 5
)
for /d /r %%D in (__pycache__) do @if exist "%%D" rmdir /s /q "%%D"
del /s /q *.pyc >nul 2>nul

echo [4/7] Running build_check.py...
%PY_EXE% build_check.py
if errorlevel 1 (
  echo ERROR: build_check.py failed.
  if "%NO_PAUSE%"=="0" pause
  exit /b 6
)

echo [5/7] Building clean onedir EXE via PyInstaller...
%PY_EXE% -m PyInstaller jarvis_pyinstaller.spec --noconfirm --clean
if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller failed.
  echo Most common reason: old dist\JARVIS.exe was locked by a running JARVIS process or antivirus.
  echo Close JARVIS / tray icon, reboot if needed, and build again.
  if "%NO_PAUSE%"=="0" pause
  exit /b 10
)

if not exist dist\JARVIS\JARVIS.exe (
  echo.
  echo ERROR: Expected file was not created: dist\JARVIS\JARVIS.exe
  echo Build result is wrong. Check PyInstaller output above.
  if "%NO_PAUSE%"=="0" pause
  exit /b 11
)

echo [6/7] Copying default config if needed...
if exist dist\JARVIS\config.example.json if not exist dist\JARVIS\data mkdir dist\JARVIS\data >nul 2>nul
if exist dist\JARVIS\config.example.json copy /y dist\JARVIS\config.example.json dist\JARVIS\data\config.json >nul

echo [7/7] Copying Vosk model and helper files...
if exist model\am (
  echo Copying Vosk model into dist\JARVIS\model ...
  if exist dist\JARVIS\model rmdir /s /q dist\JARVIS\model
  xcopy model dist\JARVIS\model /E /I /Y >nul
) else (
  echo WARNING: real Vosk model not found in project root "model".
  echo Put the unpacked Vosk model into project root "model" before building setup,
  echo or place model near installed JARVIS.exe later.
)

for %%F in (SETUP_LOCAL_MODEL_WINDOWS.bat CHECK_LOCAL_MODEL_WINDOWS.bat SET_CLOUD_KEY_WINDOWS.bat REMOVE_CLOUD_KEY_WINDOWS.bat CLEAR_REMINDERS_WINDOWS.bat QUICK_START_RU.txt MODEL_SETUP_RU.txt README.md README_RU.txt ARCHITECTURE_RU.md CHANGELOG.txt) do (
  if exist "%%F" copy /y "%%F" "dist\JARVIS\%%F" >nul
)

echo Done.
echo EXE path: dist\JARVIS\JARVIS.exe
if "%NO_PAUSE%"=="0" pause
exit /b 0

:python_error
echo ERROR: Python launcher not found. Install Python 3 and enable "Add python.exe to PATH".
if "%NO_PAUSE%"=="0" pause
exit /b 1

:venv_error
echo ERROR: Cannot create Python virtual environment.
if "%NO_PAUSE%"=="0" pause
exit /b 2

:pip_error
echo ERROR: Cannot install Python dependencies.
if "%NO_PAUSE%"=="0" pause
exit /b 3
