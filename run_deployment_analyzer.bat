@echo off
echo ====================================================
echo Deployment Analyzer Debug Launcher
echo ====================================================
echo Running at: %DATE% %TIME%
echo Current directory: %CD%

cd /d %~dp0
echo Batch file directory: %CD%

echo.
echo Directory contents:
dir /b

echo.
echo Checking for executable...
if exist dist\DeploymentAnalyzer\DeploymentAnalyzer.exe (
    echo Found executable at dist\DeploymentAnalyzer\DeploymentAnalyzer.exe

    echo.
    echo Creating required directories if missing...
    if not exist dist\DeploymentAnalyzer\data mkdir dist\DeploymentAnalyzer\data
    if not exist dist\DeploymentAnalyzer\logs mkdir dist\DeploymentAnalyzer\logs
    if not exist dist\DeploymentAnalyzer\output mkdir dist\DeploymentAnalyzer\output
    
    echo.
    echo Launching application with output logged to app_output.log...
    cd dist\DeploymentAnalyzer
    echo Changed directory to: %CD%
    
    start /b cmd /c "DeploymentAnalyzer.exe > ..\..\app_output.log 2>&1"
    echo Application started. Check app_output.log for details.
) else (
    echo ERROR: DeploymentAnalyzer.exe not found in the dist\DeploymentAnalyzer directory.
    echo.
    echo Current directory contents:
    dir /b
    echo.
    echo Dist directory contents:
    if exist dist (
        dir /b dist
        if exist dist\DeploymentAnalyzer (
            echo.
            echo DeploymentAnalyzer directory contents:
            dir /b dist\DeploymentAnalyzer
        )
    ) else (
        echo Dist directory not found.
    )
    echo.
    echo Please run PyInstaller to build the application first.
)

echo.
echo Press any key to exit...
pause > nul 