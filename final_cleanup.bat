@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FINAL CLEANUP
echo ================================================
echo Running at: %date% %time%

set DIST_DIR=dist\DeploymentAnalyzer
echo Distribution directory: %DIST_DIR%

if not exist %DIST_DIR% (
    echo ERROR: Distribution directory not found!
    pause
    exit /b 1
)

echo.
echo Moving additional files to lib directory...
if exist "%DIST_DIR%\app_config.ini" move "%DIST_DIR%\app_config.ini" "%DIST_DIR%\lib\" > nul 2>&1
if exist "%DIST_DIR%\debug_launcher.bat" move "%DIST_DIR%\debug_launcher.bat" "%DIST_DIR%\lib\" > nul 2>&1
if exist "%DIST_DIR%\verify.bat" move "%DIST_DIR%\verify.bat" "%DIST_DIR%\lib\" > nul 2>&1
if exist "%DIST_DIR%\verify_results.txt" move "%DIST_DIR%\verify_results.txt" "%DIST_DIR%\lib\" > nul 2>&1
if exist "%DIST_DIR%\Deployment Analyzer.bat" del "%DIST_DIR%\Deployment Analyzer.bat" > nul 2>&1

echo.
echo Checking final contents...
dir "%DIST_DIR%" /b

echo.
echo Final organization complete!
echo.
echo The distribution folder now contains only:
echo - DeploymentAnalyzer.bat (launcher)
echo - README.txt (documentation)
echo - debug.bat (for troubleshooting)
echo - lib\ (all application files)
echo - support\ (user data)
echo.
echo Done.
pause 