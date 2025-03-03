@echo off 
cd /d "%~dp0" 
set PATH=%~dp0lib;%PATH% 
if not exist "%~dp0support\logs" mkdir "%~dp0support\logs" 
if not exist "%~dp0support\data" mkdir "%~dp0support\data" 
if not exist "%~dp0support\output" mkdir "%~dp0support\output" 
start "" "%~dp0lib\DeploymentAnalyzer.exe" --gui 
