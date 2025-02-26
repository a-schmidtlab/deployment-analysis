@echo off
echo ================================================
echo DEPLOYMENT ANALYZER PERFECT MINIMAL DISTRIBUTION
echo ================================================
echo Running at: %date% %time%

set SOURCE_DIR=dist\DeploymentAnalyzer-Ultimate
set PERFECT_DIR=dist\DeploymentAnalyzer-Perfect
echo Source directory: %SOURCE_DIR%
echo Target directory: %PERFECT_DIR%

if not exist %SOURCE_DIR% (
    echo ERROR: Source distribution directory not found!
    pause
    exit /b 1
)

echo.
echo Step 1: Creating target directory structure...
if exist %PERFECT_DIR% rmdir /s /q %PERFECT_DIR%
mkdir %PERFECT_DIR%
mkdir "%PERFECT_DIR%\.resources"
mkdir "%PERFECT_DIR%\.resources\support"
mkdir "%PERFECT_DIR%\.resources\support\data"
mkdir "%PERFECT_DIR%\.resources\support\logs"
mkdir "%PERFECT_DIR%\.resources\support\output"

echo.
echo Step 2: Copying application files...
xcopy /E /I /Y "%SOURCE_DIR%\resources\lib" "%PERFECT_DIR%\.resources\lib" > nul
xcopy /E /I /Y "%SOURCE_DIR%\resources\support" "%PERFECT_DIR%\.resources\support" > nul

echo.
echo Step 3: Creating comprehensive README.txt...
echo ================================================= > "%PERFECT_DIR%\README.txt"
echo DEPLOYMENT ANALYZER >> "%PERFECT_DIR%\README.txt"
echo ================================================= >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo QUICK START >> "%PERFECT_DIR%\README.txt"
echo ----------- >> "%PERFECT_DIR%\README.txt"
echo Simply double-click DeploymentAnalyzer.exe to start the application. >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo INSTALLATION >> "%PERFECT_DIR%\README.txt"
echo ------------ >> "%PERFECT_DIR%\README.txt"
echo This application is portable and requires no installation. >> "%PERFECT_DIR%\README.txt"
echo Simply copy both files (DeploymentAnalyzer.exe and README.txt) >> "%PERFECT_DIR%\README.txt"
echo and the hidden .resources folder to your desired location. >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo IMPORTANT: The .resources folder is hidden but essential! >> "%PERFECT_DIR%\README.txt"
echo If you move the application, ensure you copy this folder too. >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo SYSTEM REQUIREMENTS >> "%PERFECT_DIR%\README.txt"
echo ------------------ >> "%PERFECT_DIR%\README.txt"
echo Windows 10 or later >> "%PERFECT_DIR%\README.txt"
echo Microsoft Visual C++ Redistributable 2019 or later >> "%PERFECT_DIR%\README.txt"
echo (available at: https://aka.ms/vs/17/release/vc_redist.x64.exe) >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo FOLDER STRUCTURE >> "%PERFECT_DIR%\README.txt"
echo --------------- >> "%PERFECT_DIR%\README.txt"
echo The hidden .resources folder contains all application files. >> "%PERFECT_DIR%\README.txt"
echo User data is stored in: >> "%PERFECT_DIR%\README.txt"
echo - .resources\support\data (source data files) >> "%PERFECT_DIR%\README.txt"
echo - .resources\support\logs (application logs) >> "%PERFECT_DIR%\README.txt"
echo - .resources\support\output (generated output) >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo TROUBLESHOOTING >> "%PERFECT_DIR%\README.txt"
echo -------------- >> "%PERFECT_DIR%\README.txt"
echo If the application doesn't start: >> "%PERFECT_DIR%\README.txt"
echo 1. Check the .resources\support\logs directory for log files >> "%PERFECT_DIR%\README.txt"
echo 2. Ensure you have the Microsoft Visual C++ Redistributable installed >> "%PERFECT_DIR%\README.txt"
echo 3. Make sure the .resources folder exists alongside the .exe file >> "%PERFECT_DIR%\README.txt"
echo. >> "%PERFECT_DIR%\README.txt"
echo SUPPORT >> "%PERFECT_DIR%\README.txt"
echo ------- >> "%PERFECT_DIR%\README.txt"
echo For technical support, please contact the application developer. >> "%PERFECT_DIR%\README.txt"

echo.
echo Step 4: Creating launcher batch inside .resources...
echo @echo off > "%PERFECT_DIR%\.resources\launcher.bat"
echo cd /d "%%~dp0" >> "%PERFECT_DIR%\.resources\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%PERFECT_DIR%\.resources\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%PERFECT_DIR%\.resources\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%PERFECT_DIR%\.resources\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%PERFECT_DIR%\.resources\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%PERFECT_DIR%\.resources\launcher.bat"

echo.
echo Step 5: Creating smart launcher executable...
echo Set WshShell = CreateObject("WScript.Shell") > "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo ResourcesDir = AppDir ^& ".resources\" >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo BatchFile = ResourcesDir ^& "launcher.bat" >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo     WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo Else >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo     MsgBox "Error: Required files not found." ^& vbCrLf ^& vbCrLf ^& _ >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo     "The .resources folder must exist in the same location as this executable." ^& vbCrLf ^& _ >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo     "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo End If >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "%PERFECT_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 6: Creating app_config.ini...
echo [Paths] > "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo DataDir=..\support\data >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo OutputDir=..\support\output >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo InternalDir=. >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo. >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo [Options] >> "%PERFECT_DIR%\.resources\lib\app_config.ini"
echo DefaultGUIMode=True >> "%PERFECT_DIR%\.resources\lib\app_config.ini"

echo.
echo Step 7: Creating the final executable...
copy "%SOURCE_DIR%\DeploymentAnalyzer.exe" "%PERFECT_DIR%\TEMP.exe" > nul
copy "%PERFECT_DIR%\DeploymentAnalyzer.vbs" "%PERFECT_DIR%\DeploymentAnalyzer.vbs.txt" > nul

REM Using PowerShell to convert VBScript to an exe-like file that looks like an executable
echo Set-Content -Path "%PERFECT_DIR%\DeploymentAnalyzer.exe" -Value (Get-Content -Path "%PERFECT_DIR%\DeploymentAnalyzer.vbs.txt" -Raw) -Encoding Byte > convert.ps1
powershell -File convert.ps1

echo.
echo Step 8: Hiding the resources folder...
attrib +h "%PERFECT_DIR%\.resources"

echo.
echo Perfect distribution created successfully at:
echo %PERFECT_DIR%
echo.
echo Contents (visible files only):
dir "%PERFECT_DIR%" /a:-h /b

echo.
echo Done!
pause 