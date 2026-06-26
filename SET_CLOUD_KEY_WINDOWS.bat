@echo off
chcp 65001 >nul
title JARVIS Cloud Key Setup
echo ==============================================
echo  JARVIS - cloud API key setup
echo ==============================================
echo.
echo Paste your cloud API key below.
echo It will be saved to Windows environment variables.
echo Your project ZIP will NOT contain this key.
echo.
set /p JARVIS_CLOUD_KEY=Cloud API key: 
if "%JARVIS_CLOUD_KEY%"=="" (
  echo No key entered. Nothing changed.
  pause
  exit /b 0
)

setx JARVIS_CLOUD_API_KEY "%JARVIS_CLOUD_KEY%"
setx JARVIS_MODEL_PROVIDER "cloud"

echo.
echo Done.
echo Fully close JARVIS and start it again.
pause
