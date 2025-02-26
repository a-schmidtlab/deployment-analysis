@echo off
echo ===================================
echo Updating Release with EXE Launcher
echo ===================================
echo.

set RELEASE_DIR=dist\DeploymentAnalyzer-Release

REM Check if release directory exists
if not exist %RELEASE_DIR% (
    echo Error: Release directory not found at %RELEASE_DIR%
    echo Please run create_final_release.bat first to create a release.
    echo.
    pause
    exit /b 1
)

echo Release directory found at: %RELEASE_DIR%
echo.

REM Run PowerShell script to create the EXE launcher
echo Creating EXE launcher...
PowerShell -ExecutionPolicy Bypass -File create_exe_launcher.ps1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to create EXE launcher.
    echo.
    pause
    exit /b 1
)

echo.
echo Verifying files in release directory...
dir /b %RELEASE_DIR%
echo.
echo Update completed successfully!
echo Your release now has a proper EXE file as the launcher.
echo.
pause 