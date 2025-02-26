@echo off
echo ================================================
echo DEPLOYMENT ANALYZER MINIMAL DISTRIBUTION
echo ================================================
echo Running at: %date% %time%

set SOURCE_DIR=dist\DeploymentAnalyzer
set MINIMAL_DIR=dist\DeploymentAnalyzer-Minimal
echo Source directory: %SOURCE_DIR%
echo Target directory: %MINIMAL_DIR%

if not exist %SOURCE_DIR% (
    echo ERROR: Source distribution directory not found!
    pause
    exit /b 1
)

echo.
echo Step 1: Creating target directory structure...
if exist %MINIMAL_DIR% rmdir /s /q %MINIMAL_DIR%
mkdir %MINIMAL_DIR%
mkdir "%MINIMAL_DIR%\lib"
mkdir "%MINIMAL_DIR%\support"
mkdir "%MINIMAL_DIR%\support\data"
mkdir "%MINIMAL_DIR%\support\logs"
mkdir "%MINIMAL_DIR%\support\output"

echo.
echo Step 2: Copying lib directory...
xcopy /E /I /Y "%SOURCE_DIR%\lib" "%MINIMAL_DIR%\lib" > nul

echo.
echo Step 3: Creating README.txt file...
echo ================================================= > "%MINIMAL_DIR%\README.txt"
echo DEPLOYMENT ANALYZER >> "%MINIMAL_DIR%\README.txt"
echo ================================================= >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo QUICK START >> "%MINIMAL_DIR%\README.txt"
echo ----------- >> "%MINIMAL_DIR%\README.txt"
echo Simply double-click DeploymentAnalyzer.exe to start the application. >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo INSTALLATION >> "%MINIMAL_DIR%\README.txt"
echo ------------ >> "%MINIMAL_DIR%\README.txt"
echo This application is portable and requires no installation. >> "%MINIMAL_DIR%\README.txt"
echo Simply copy the entire folder to your desired location. >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo SYSTEM REQUIREMENTS >> "%MINIMAL_DIR%\README.txt"
echo ------------------ >> "%MINIMAL_DIR%\README.txt"
echo Windows 10 or later >> "%MINIMAL_DIR%\README.txt"
echo Microsoft Visual C++ Redistributable 2019 or later >> "%MINIMAL_DIR%\README.txt"
echo (available at: https://aka.ms/vs/17/release/vc_redist.x64.exe) >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo DIRECTORY STRUCTURE >> "%MINIMAL_DIR%\README.txt"
echo ------------------ >> "%MINIMAL_DIR%\README.txt"
echo DeploymentAnalyzer.exe - Application starter >> "%MINIMAL_DIR%\README.txt"
echo lib\               - Contains application files (do not modify) >> "%MINIMAL_DIR%\README.txt"
echo support\           - Contains user data and configuration files >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo TROUBLESHOOTING >> "%MINIMAL_DIR%\README.txt"
echo -------------- >> "%MINIMAL_DIR%\README.txt"
echo If the application doesn't start: >> "%MINIMAL_DIR%\README.txt"
echo 1. Check the support\logs directory for log files >> "%MINIMAL_DIR%\README.txt"
echo 2. Ensure you have the Microsoft Visual C++ Redistributable installed >> "%MINIMAL_DIR%\README.txt"
echo 3. Try running the application from a command prompt for error messages >> "%MINIMAL_DIR%\README.txt"
echo. >> "%MINIMAL_DIR%\README.txt"
echo SUPPORT >> "%MINIMAL_DIR%\README.txt"
echo ------- >> "%MINIMAL_DIR%\README.txt"
echo For technical support, please contact the application developer. >> "%MINIMAL_DIR%\README.txt"

echo.
echo Step 4: Creating minimal launcher...
echo @echo off > "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo cd /d "%%~dp0" >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%MINIMAL_DIR%\DeploymentAnalyzer.exe.bat"

echo.
echo Step 5: Creating app_config.ini...
echo [Paths] > "%MINIMAL_DIR%\lib\app_config.ini"
echo DataDir=..\support\data >> "%MINIMAL_DIR%\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%MINIMAL_DIR%\lib\app_config.ini"
echo OutputDir=..\support\output >> "%MINIMAL_DIR%\lib\app_config.ini"
echo InternalDir=. >> "%MINIMAL_DIR%\lib\app_config.ini"
echo. >> "%MINIMAL_DIR%\lib\app_config.ini"
echo [Options] >> "%MINIMAL_DIR%\lib\app_config.ini"
echo DefaultGUIMode=True >> "%MINIMAL_DIR%\lib\app_config.ini"

echo.
echo Step 6: Creating VBS launcher to hide command window...
echo Set WshShell = CreateObject("WScript.Shell") > "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"
echo BatchFile = AppDir ^& "DeploymentAnalyzer.exe.bat" >> "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"
echo WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "%MINIMAL_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 7: Creating final executable...
copy /b "%SOURCE_DIR%\lib\DeploymentAnalyzer.exe" "%MINIMAL_DIR%\DeploymentAnalyzer.exe" > nul

echo.
echo Minimal distribution created successfully at:
echo %MINIMAL_DIR%
echo.
echo Contents:
dir "%MINIMAL_DIR%" /b

echo.
echo Done!
pause 