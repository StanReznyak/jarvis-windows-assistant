@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo JARVIS v8.4 installer build
echo ========================================
echo.

call build_exe.bat --no-pause
if errorlevel 1 (
  echo.
  echo ERROR: EXE build failed. Installer build stopped.
  pause
  exit /b 20
)

if not exist dist\JARVIS\JARVIS.exe (
  echo ERROR: EXE not found: dist\JARVIS\JARVIS.exe
  echo Build failed or PyInstaller did not create the expected dist\JARVIS folder.
  pause
  exit /b 1
)

if exist dist\JARVIS.exe (
  echo WARNING: old wrong file dist\JARVIS.exe found. Removing it...
  del /f /q dist\JARVIS.exe >nul 2>nul
)

if not exist dist\JARVIS\model\am (
  echo WARNING: Vosk model was not copied into dist\JARVIS\model.
  echo Installer will still be built, but voice via Vosk will show a clear error until model is placed near JARVIS.exe.
  echo To bundle Vosk: put the unpacked model into project root "model" and rebuild.
)

set "ISCC_EXE="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if "%ISCC_EXE%"=="" if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
if "%ISCC_EXE%"=="" for %%I in (ISCC.exe) do if not "%%~$PATH:I"=="" set "ISCC_EXE=%%~$PATH:I"
if "%ISCC_EXE%"=="" (
  echo ERROR: Inno Setup 6 not found.
  echo Install Inno Setup 6 or add ISCC.exe to PATH.
  pause
  exit /b 1
)

"%ISCC_EXE%" JARVIS_Setup.iss
if errorlevel 1 (
  echo ERROR: Inno Setup failed.
  pause
  exit /b 30
)

echo Done. Installer is in dist_setup.
pause
exit /b 0
