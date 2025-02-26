@echo off
echo =====================================================
echo VERBOSE DEBUG - DeploymentAnalyzer
echo %date% %time%
echo Current Directory: %CD%
echo =====================================================
echo.

echo Creating required directories if they don't exist...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "output" mkdir output

echo Checking if executable exists...
if not exist "dist\DeploymentAnalyzer\DeploymentAnalyzer.exe" (
    echo ERROR: DeploymentAnalyzer.exe not found in dist\DeploymentAnalyzer
    exit /b 1
)

echo Launching executable with full console output...
echo Output and errors will be captured in logs\verbose_debug.log
echo.

cd dist\DeploymentAnalyzer
echo Now in directory: %CD%

echo Starting executable at %time%...
DeploymentAnalyzer.exe --gui > ..\..\logs\verbose_debug.log 2>&1

set EXIT_CODE=%ERRORLEVEL%
cd ..\..

echo.
echo Process finished with exit code: %EXIT_CODE%
echo.

if %EXIT_CODE% NEQ 0 (
    echo ERROR: Application terminated with errors.
    echo Check logs\verbose_debug.log for details.
) else (
    echo Application launched successfully.
    echo If you don't see the application window, check logs\verbose_debug.log
)

echo.
echo Debug log created at logs\verbose_debug.log
echo.

pause 