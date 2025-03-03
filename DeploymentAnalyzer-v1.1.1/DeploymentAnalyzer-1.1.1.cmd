@echo off
echo Starting Deployment Analyzer v1.1.1...
cd /d "%~dp0"
start "" ".app\lib\DeploymentAnalyzer.exe" --gui
echo.
echo If the application doesn't start, please ensure the .app folder exists and has not been renamed or deleted.
pause 