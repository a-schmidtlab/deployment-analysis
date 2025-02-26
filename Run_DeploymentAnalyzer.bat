@echo off
echo Starting Deployment Analyzer...
echo.

rem Create required directories if they don't exist
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "output" mkdir output

rem Run the application with the GUI flag
start "" "dist\DeploymentAnalyzer\DeploymentAnalyzer.exe" --gui

echo.
echo If the application doesn't start, please check the logs directory for error information.
echo. 