@echo off
echo ================================================
echo DEPLOYMENT ANALYZER ULTIMATE MINIMAL DISTRIBUTION
echo ================================================
echo Running at: %date% %time%

set SOURCE_DIR=dist\DeploymentAnalyzer-Minimal
set ULTIMATE_DIR=dist\DeploymentAnalyzer-Ultimate
echo Source directory: %SOURCE_DIR%
echo Target directory: %ULTIMATE_DIR%

if not exist %SOURCE_DIR% (
    echo ERROR: Source distribution directory not found!
    pause
    exit /b 1
)

echo.
echo Step 1: Creating target directory structure...
if exist %ULTIMATE_DIR% rmdir /s /q %ULTIMATE_DIR%
mkdir %ULTIMATE_DIR%
mkdir "%ULTIMATE_DIR%\resources"
mkdir "%ULTIMATE_DIR%\resources\support"
mkdir "%ULTIMATE_DIR%\resources\support\data"
mkdir "%ULTIMATE_DIR%\resources\support\logs"
mkdir "%ULTIMATE_DIR%\resources\support\output"

echo.
echo Step 2: Copying application files...
xcopy /E /I /Y "%SOURCE_DIR%\lib" "%ULTIMATE_DIR%\resources\lib" > nul
xcopy /E /I /Y "%SOURCE_DIR%\support" "%ULTIMATE_DIR%\resources\support" > nul

echo.
echo Step 3: Creating comprehensive README.txt...
echo ================================================= > "%ULTIMATE_DIR%\README.txt"
echo DEPLOYMENT ANALYZER >> "%ULTIMATE_DIR%\README.txt"
echo ================================================= >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo QUICK START >> "%ULTIMATE_DIR%\README.txt"
echo ----------- >> "%ULTIMATE_DIR%\README.txt"
echo Simply double-click DeploymentAnalyzer.exe to start the application. >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo INSTALLATION >> "%ULTIMATE_DIR%\README.txt"
echo ------------ >> "%ULTIMATE_DIR%\README.txt"
echo This application is portable and requires no installation. >> "%ULTIMATE_DIR%\README.txt"
echo Simply copy the entire folder to your desired location. >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo SYSTEM REQUIREMENTS >> "%ULTIMATE_DIR%\README.txt"
echo ------------------ >> "%ULTIMATE_DIR%\README.txt"
echo Windows 10 or later >> "%ULTIMATE_DIR%\README.txt"
echo Microsoft Visual C++ Redistributable 2019 or later >> "%ULTIMATE_DIR%\README.txt"
echo (available at: https://aka.ms/vs/17/release/vc_redist.x64.exe) >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo FOLDER STRUCTURE >> "%ULTIMATE_DIR%\README.txt"
echo --------------- >> "%ULTIMATE_DIR%\README.txt"
echo The 'resources' folder contains all application files and should not be modified. >> "%ULTIMATE_DIR%\README.txt"
echo User data is stored in: >> "%ULTIMATE_DIR%\README.txt"
echo - resources\support\data (source data files) >> "%ULTIMATE_DIR%\README.txt"
echo - resources\support\logs (application logs) >> "%ULTIMATE_DIR%\README.txt"
echo - resources\support\output (generated output) >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo TROUBLESHOOTING >> "%ULTIMATE_DIR%\README.txt"
echo -------------- >> "%ULTIMATE_DIR%\README.txt"
echo If the application doesn't start: >> "%ULTIMATE_DIR%\README.txt"
echo 1. Check the resources\support\logs directory for log files >> "%ULTIMATE_DIR%\README.txt"
echo 2. Ensure you have the Microsoft Visual C++ Redistributable installed >> "%ULTIMATE_DIR%\README.txt"
echo 3. Try running the application from a command prompt for error messages >> "%ULTIMATE_DIR%\README.txt"
echo. >> "%ULTIMATE_DIR%\README.txt"
echo SUPPORT >> "%ULTIMATE_DIR%\README.txt"
echo ------- >> "%ULTIMATE_DIR%\README.txt"
echo For technical support, please contact the application developer. >> "%ULTIMATE_DIR%\README.txt"

echo.
echo Step 4: Creating self-launching executable...
echo @echo off > "%ULTIMATE_DIR%\resources\launcher.bat"
echo cd /d "%%~dp0" >> "%ULTIMATE_DIR%\resources\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%ULTIMATE_DIR%\resources\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%ULTIMATE_DIR%\resources\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%ULTIMATE_DIR%\resources\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%ULTIMATE_DIR%\resources\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%ULTIMATE_DIR%\resources\launcher.bat"

echo.
echo Step 5: Creating VBS launcher for the exe...
echo Set WshShell = CreateObject("WScript.Shell") > "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo ResourcesDir = AppDir ^& "resources\" >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo BatchFile = ResourcesDir ^& "launcher.bat" >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "%ULTIMATE_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 6: Creating app_config.ini...
echo [Paths] > "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo DataDir=..\support\data >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo OutputDir=..\support\output >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo InternalDir=. >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo. >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo [Options] >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"
echo DefaultGUIMode=True >> "%ULTIMATE_DIR%\resources\lib\app_config.ini"

echo.
echo Step 7: Renaming VBS to EXE...
copy /b "%SOURCE_DIR%\DeploymentAnalyzer.exe" "%ULTIMATE_DIR%\DeploymentAnalyzer.exe" > nul

echo.
echo Ultimate minimal distribution created successfully at:
echo %ULTIMATE_DIR%
echo.
echo Contents:
dir "%ULTIMATE_DIR%" /b

echo.
echo Done!
pause 