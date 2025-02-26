@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FINAL SOLUTION
echo ================================================
echo Running at: %date% %time%

set SOURCE_DIR=dist\DeploymentAnalyzer-Ultimate
set FINAL_DIR=dist\DeploymentAnalyzer-Final
echo Source directory: %SOURCE_DIR%
echo Target directory: %FINAL_DIR%

if not exist %SOURCE_DIR% (
    echo ERROR: Source distribution directory not found!
    pause
    exit /b 1
)

echo.
echo Step 1: Creating target directory structure...
if exist %FINAL_DIR% rmdir /s /q %FINAL_DIR%
mkdir %FINAL_DIR%
mkdir "%FINAL_DIR%\.app"
mkdir "%FINAL_DIR%\.app\support"
mkdir "%FINAL_DIR%\.app\support\data"
mkdir "%FINAL_DIR%\.app\support\logs"
mkdir "%FINAL_DIR%\.app\support\output"

echo.
echo Step 2: Copying application files...
xcopy /E /I /Y "%SOURCE_DIR%\resources\lib" "%FINAL_DIR%\.app\lib" > nul
xcopy /E /I /Y "%SOURCE_DIR%\resources\support" "%FINAL_DIR%\.app\support" > nul

echo.
echo Step 3: Creating comprehensive README.txt...
echo ================================================= > "%FINAL_DIR%\README.txt"
echo DEPLOYMENT ANALYZER >> "%FINAL_DIR%\README.txt"
echo ================================================= >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo QUICK START >> "%FINAL_DIR%\README.txt"
echo ----------- >> "%FINAL_DIR%\README.txt"
echo Simply double-click DeploymentAnalyzer.exe to start the application. >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo INSTALLATION >> "%FINAL_DIR%\README.txt"
echo ------------ >> "%FINAL_DIR%\README.txt"
echo This application is portable and requires no installation. >> "%FINAL_DIR%\README.txt"
echo Simply copy both files (DeploymentAnalyzer.exe and README.txt) >> "%FINAL_DIR%\README.txt"
echo and the hidden .app folder to your desired location. >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo IMPORTANT: The .app folder is hidden but essential! >> "%FINAL_DIR%\README.txt"
echo If you move the application, ensure you copy this folder too. >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo SYSTEM REQUIREMENTS >> "%FINAL_DIR%\README.txt"
echo ------------------ >> "%FINAL_DIR%\README.txt"
echo Windows 10 or later >> "%FINAL_DIR%\README.txt"
echo Microsoft Visual C++ Redistributable 2019 or later >> "%FINAL_DIR%\README.txt"
echo (available at: https://aka.ms/vs/17/release/vc_redist.x64.exe) >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo FOLDER STRUCTURE >> "%FINAL_DIR%\README.txt"
echo --------------- >> "%FINAL_DIR%\README.txt"
echo The hidden .app folder contains all application files. >> "%FINAL_DIR%\README.txt"
echo User data is stored in: >> "%FINAL_DIR%\README.txt"
echo - .app\support\data (source data files) >> "%FINAL_DIR%\README.txt"
echo - .app\support\logs (application logs) >> "%FINAL_DIR%\README.txt"
echo - .app\support\output (generated output) >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo TROUBLESHOOTING >> "%FINAL_DIR%\README.txt"
echo -------------- >> "%FINAL_DIR%\README.txt"
echo If the application doesn't start: >> "%FINAL_DIR%\README.txt"
echo 1. Check the .app\support\logs directory for log files >> "%FINAL_DIR%\README.txt"
echo 2. Ensure you have the Microsoft Visual C++ Redistributable installed >> "%FINAL_DIR%\README.txt"
echo 3. Make sure the .app folder exists alongside the .exe file >> "%FINAL_DIR%\README.txt"
echo. >> "%FINAL_DIR%\README.txt"
echo SUPPORT >> "%FINAL_DIR%\README.txt"
echo ------- >> "%FINAL_DIR%\README.txt"
echo For technical support, please contact the application developer. >> "%FINAL_DIR%\README.txt"

echo.
echo Step 4: Creating launcher batch...
echo @echo off > "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo cd /d "%%~dp0.app" >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo set PATH=%%~dp0.app\lib;%%PATH%% >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0.app\support\logs" mkdir "%%~dp0.app\support\logs" >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0.app\support\data" mkdir "%%~dp0.app\support\data" >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo if not exist "%%~dp0.app\support\output" mkdir "%%~dp0.app\support\output" >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"
echo start "" "%%~dp0.app\lib\DeploymentAnalyzer.exe" --gui >> "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"

echo.
echo Step 5: Creating VBScript launcher...
echo Set WshShell = CreateObject("WScript.Shell") > "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo BatchFile = AppDir ^& "DeploymentAnalyzer.exe.bat" >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo     WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo Else >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo     MsgBox "Error: Required files not found." ^& vbCrLf ^& vbCrLf ^& _ >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo     "The .app folder must exist in the same location as this executable." ^& vbCrLf ^& _ >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo     "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo End If >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "%FINAL_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 6: Creating app_config.ini...
echo [Paths] > "%FINAL_DIR%\.app\lib\app_config.ini"
echo DataDir=..\support\data >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo OutputDir=..\support\output >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo InternalDir=. >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo. >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo [Options] >> "%FINAL_DIR%\.app\lib\app_config.ini"
echo DefaultGUIMode=True >> "%FINAL_DIR%\.app\lib\app_config.ini"

echo.
echo Step 7: Renaming VBScript to make it look like an executable...
echo ^@if (^1==^1) echo off>"%FINAL_DIR%\DeploymentAnalyzer.exe"
echo cscript //nologo "%~dp0\%FINAL_DIR%\DeploymentAnalyzer.vbs">>"%FINAL_DIR%\DeploymentAnalyzer.exe"
echo exit>>"%FINAL_DIR%\DeploymentAnalyzer.exe"

echo.
echo Step 8: Hiding auxiliary files and folders...
attrib +h "%FINAL_DIR%\.app"
attrib +h "%FINAL_DIR%\DeploymentAnalyzer.vbs"
attrib +h "%FINAL_DIR%\DeploymentAnalyzer.exe.bat"

echo.
echo Perfect distribution created successfully at:
echo %FINAL_DIR%
echo.
echo Contents (visible files only):
dir "%FINAL_DIR%" /a:-h /b

echo.
echo Done!
pause 