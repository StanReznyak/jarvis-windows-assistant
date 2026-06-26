@echo off
chcp 65001 >nul
title JARVIS Cloud Key Remove
echo ==============================================
echo  JARVIS - remove cloud API key helper
echo ==============================================
echo.
echo This clears the cloud key from Windows environment variables.
echo.

setx JARVIS_CLOUD_API_KEY ""
setx JARVIS_MODEL_PROVIDER ""

echo Done. Fully close JARVIS and start it again.
pause
