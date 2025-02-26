@echo off
echo ================================================
echo DEPLOYMENT ANALYZER DISTRIBUTION REORGANIZATION
echo ================================================
echo Running at: %date% %time%

set DIST_DIR=dist\DeploymentAnalyzer
echo Distribution directory: %DIST_DIR%

if not exist %DIST_DIR% (
    echo ERROR: Distribution directory not found!
    echo Please run the build script first.
    pause
    exit /b 1
)

echo.
echo Step 1: Creating folder structure...
if not exist "%DIST_DIR%\lib" mkdir "%DIST_DIR%\lib"
if not exist "%DIST_DIR%\support\data" mkdir "%DIST_DIR%\support\data"
if not exist "%DIST_DIR%\support\logs" mkdir "%DIST_DIR%\support\logs"
if not exist "%DIST_DIR%\support\output" mkdir "%DIST_DIR%\support\output"

echo.
echo Step 2: Moving DLL files to lib directory...
move "%DIST_DIR%\*.dll" "%DIST_DIR%\lib\" > nul 2>&1

echo.
echo Step 3: Moving Python files to lib directory...
move "%DIST_DIR%\*.pyd" "%DIST_DIR%\lib\" > nul 2>&1
move "%DIST_DIR%\*.py" "%DIST_DIR%\lib\" > nul 2>&1
move "%DIST_DIR%\*.pyc" "%DIST_DIR%\lib\" > nul 2>&1

echo.
echo Step 4: Moving other files to lib directory...
move "%DIST_DIR%\*.manifest" "%DIST_DIR%\lib\" > nul 2>&1
move "%DIST_DIR%\*.typelib" "%DIST_DIR%\lib\" > nul 2>&1
move "%DIST_DIR%\*.cat" "%DIST_DIR%\lib\" > nul 2>&1

echo.
echo Step 5: Moving folders to lib directory...
for /d %%i in ("%DIST_DIR%\*") do (
    if not "%%~nxi"=="support" (
        if not "%%~nxi"=="lib" (
            echo Moving folder: %%~nxi
            move "%%i" "%DIST_DIR%\lib\" > nul 2>&1
        )
    )
)

echo.
echo Step 6: Creating launcher batch file...
echo @echo off > "%DIST_DIR%\DeploymentAnalyzer.bat"
echo cd /d "%%~dp0" >> "%DIST_DIR%\DeploymentAnalyzer.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%DIST_DIR%\DeploymentAnalyzer.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%DIST_DIR%\DeploymentAnalyzer.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%DIST_DIR%\DeploymentAnalyzer.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%DIST_DIR%\DeploymentAnalyzer.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%DIST_DIR%\DeploymentAnalyzer.bat"

echo.
echo Step 7: Creating comprehensive README.txt...
echo ================================================= > "%DIST_DIR%\README.txt"
echo DEPLOYMENT ANALYZER >> "%DIST_DIR%\README.txt"
echo ================================================= >> "%DIST_DIR%\README.txt"
echo. >> "%DIST_DIR%\README.txt"
echo INSTALLATION >> "%DIST_DIR%\README.txt"
echo ------------ >> "%DIST_DIR%\README.txt"
echo This application is portable and requires no installation. >> "%DIST_DIR%\README.txt"
echo Simply run the DeploymentAnalyzer.bat file to launch the application. >> "%DIST_DIR%\README.txt"
echo. >> "%DIST_DIR%\README.txt"
echo SYSTEM REQUIREMENTS >> "%DIST_DIR%\README.txt"
echo ------------------ >> "%DIST_DIR%\README.txt"
echo Windows 10 or later >> "%DIST_DIR%\README.txt"
echo Microsoft Visual C++ Redistributable 2019 or later >> "%DIST_DIR%\README.txt"
echo (available at: https://aka.ms/vs/17/release/vc_redist.x64.exe) >> "%DIST_DIR%\README.txt"
echo. >> "%DIST_DIR%\README.txt"
echo DIRECTORY STRUCTURE >> "%DIST_DIR%\README.txt"
echo ------------------ >> "%DIST_DIR%\README.txt"
echo DeploymentAnalyzer.bat - Starter script that launches the application >> "%DIST_DIR%\README.txt"
echo lib\               - Contains application executables and libraries >> "%DIST_DIR%\README.txt"
echo support\           - Contains user data and configuration files >> "%DIST_DIR%\README.txt"
echo support\data\      - Contains source data files >> "%DIST_DIR%\README.txt"
echo support\logs\      - Contains application logs >> "%DIST_DIR%\README.txt"
echo support\output\    - Contains generated output files >> "%DIST_DIR%\README.txt"
echo. >> "%DIST_DIR%\README.txt"
echo TROUBLESHOOTING >> "%DIST_DIR%\README.txt"
echo -------------- >> "%DIST_DIR%\README.txt"
echo If the application doesn't start: >> "%DIST_DIR%\README.txt"
echo 1. Check the support\logs directory for log files >> "%DIST_DIR%\README.txt"
echo 2. Ensure you have the Microsoft Visual C++ Redistributable installed >> "%DIST_DIR%\README.txt"
echo 3. Try running lib\DeploymentAnalyzer.exe directly to see any error messages >> "%DIST_DIR%\README.txt"
echo. >> "%DIST_DIR%\README.txt"
echo SUPPORT >> "%DIST_DIR%\README.txt"
echo ------- >> "%DIST_DIR%\README.txt"
echo For technical support, please contact the application developer. >> "%DIST_DIR%\README.txt"

echo.
echo Step 8: Moving executable to lib directory...
move "%DIST_DIR%\DeploymentAnalyzer.exe" "%DIST_DIR%\lib\" > nul 2>&1

echo.
echo Step 9: Creating app_config.ini...
echo [Paths] > "%DIST_DIR%\lib\app_config.ini"
echo DataDir=..\support\data >> "%DIST_DIR%\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%DIST_DIR%\lib\app_config.ini"
echo OutputDir=..\support\output >> "%DIST_DIR%\lib\app_config.ini"
echo InternalDir=. >> "%DIST_DIR%\lib\app_config.ini"
echo. >> "%DIST_DIR%\lib\app_config.ini"
echo [Options] >> "%DIST_DIR%\lib\app_config.ini"
echo DefaultGUIMode=True >> "%DIST_DIR%\lib\app_config.ini"

echo.
echo Step 10: Creating a debug launcher...
echo @echo off > "%DIST_DIR%\debug.bat"
echo cd /d "%%~dp0" >> "%DIST_DIR%\debug.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%DIST_DIR%\debug.bat"
echo echo ================================================ >> "%DIST_DIR%\debug.bat"
echo echo DEPLOYMENT ANALYZER - DEBUG MODE >> "%DIST_DIR%\debug.bat"
echo echo ================================================ >> "%DIST_DIR%\debug.bat"
echo echo Running at: %%date%% %%time%% >> "%DIST_DIR%\debug.bat"
echo echo Current directory: %%CD%% >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo echo PATH environment: >> "%DIST_DIR%\debug.bat"
echo echo %%PATH%% >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo echo Directory structure: >> "%DIST_DIR%\debug.bat"
echo dir >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo echo Lib directory contents: >> "%DIST_DIR%\debug.bat"
echo dir lib >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo echo Starting application with console output... >> "%DIST_DIR%\debug.bat"
echo cd lib >> "%DIST_DIR%\debug.bat"
echo DeploymentAnalyzer.exe --gui >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo cd .. >> "%DIST_DIR%\debug.bat"
echo echo Application exited with code %%ERRORLEVEL%% >> "%DIST_DIR%\debug.bat"
echo echo. >> "%DIST_DIR%\debug.bat"
echo pause >> "%DIST_DIR%\debug.bat"

echo.
echo Reorganization complete!
echo.
echo The distribution folder has been reorganized with:
echo - DeploymentAnalyzer.bat and README.txt in the root folder
echo - All application files in the lib subfolder
echo - All user data in the support subfolder
echo.
echo To launch the application, run DeploymentAnalyzer.bat
echo To troubleshoot, run debug.bat for more information.
echo.
echo Done.
pause 