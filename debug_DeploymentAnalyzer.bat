@echo off
echo ================================================
echo Deployment Analyzer Debug Launcher
echo ================================================
echo Running at: %DATE% %TIME%
echo Current directory: %CD%

echo.
echo Creating logs directory if not exists...
if not exist logs mkdir logs

echo.
echo Checking for the executable...
if exist dist\DeploymentAnalyzer\DeploymentAnalyzer.exe (
    echo Found DeploymentAnalyzer.exe in dist\DeploymentAnalyzer
) else (
    echo ERROR: DeploymentAnalyzer.exe not found in dist\DeploymentAnalyzer
    echo Please make sure the application has been built correctly.
    goto :error
)

echo.
echo Creating required directories...
if not exist dist\DeploymentAnalyzer\logs mkdir dist\DeploymentAnalyzer\logs
if not exist dist\DeploymentAnalyzer\data mkdir dist\DeploymentAnalyzer\data
if not exist dist\DeploymentAnalyzer\output mkdir dist\DeploymentAnalyzer\output

echo.
echo Running DeploymentAnalyzer with console output...
cd dist\DeploymentAnalyzer
echo New working directory: %CD%

echo.
echo Launching application and capturing output...
DeploymentAnalyzer.exe > ..\..\logs\debug_output.log 2>&1
set EXIT_CODE=%ERRORLEVEL%
cd ..\..

echo.
echo Application exited with code: %EXIT_CODE%
echo Check logs\debug_output.log for details.

if %EXIT_CODE% NEQ 0 goto :error

echo.
echo Application started successfully.
goto :end

:error
echo.
echo There was an error running the application!
echo Please check the logs for more information.

:end
echo.
echo Press any key to exit...
pause > nul 