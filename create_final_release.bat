@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FINAL RELEASE CREATOR
echo ================================================
echo Running at: %date% %time%

REM Check available source directories in priority order
set SOURCE_FOUND=0
set SOURCE_DIR=

REM Try to find a suitable source directory
echo Checking for available distributions...
if exist dist\DeploymentAnalyzer-Final (
    set SOURCE_DIR=dist\DeploymentAnalyzer-Final
    set SOURCE_FOUND=1
    echo Found DeploymentAnalyzer-Final
) else if exist dist\DeploymentAnalyzer-Perfect (
    set SOURCE_DIR=dist\DeploymentAnalyzer-Perfect
    set SOURCE_FOUND=1
    echo Found DeploymentAnalyzer-Perfect
) else if exist dist\DeploymentAnalyzer-Ultimate (
    set SOURCE_DIR=dist\DeploymentAnalyzer-Ultimate
    set SOURCE_FOUND=1
    echo Found DeploymentAnalyzer-Ultimate
) else if exist dist\DeploymentAnalyzer (
    set SOURCE_DIR=dist\DeploymentAnalyzer
    set SOURCE_FOUND=1
    echo Found DeploymentAnalyzer
)

set RELEASE_DIR=dist\DeploymentAnalyzer-Release

if %SOURCE_FOUND% EQU 0 (
    echo ERROR: No source distribution found!
    echo.
    echo Please build a distribution first using one of the following:
    echo - ultimate_build.bat
    echo - create_perfect_minimal.bat
    echo - create_ultimate_minimal.bat
    echo.
    pause
    exit /b 1
)

echo Source directory: %SOURCE_DIR%
echo Target directory: %RELEASE_DIR%

echo.
echo Step 1: Creating target directory structure...
if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
mkdir %RELEASE_DIR%
mkdir "%RELEASE_DIR%\.app"
mkdir "%RELEASE_DIR%\.app\lib"
mkdir "%RELEASE_DIR%\.app\support"
mkdir "%RELEASE_DIR%\.app\support\data"
mkdir "%RELEASE_DIR%\.app\support\logs"
mkdir "%RELEASE_DIR%\.app\support\output"

echo.
echo Step 2: Copying lib directory...
if exist "%SOURCE_DIR%\.app\lib" (
    xcopy /E /I /Y "%SOURCE_DIR%\.app\lib\*" "%RELEASE_DIR%\.app\lib\" > nul
) else if exist "%SOURCE_DIR%\DeploymentAnalyzer.exe" (
    xcopy /Y "%SOURCE_DIR%\DeploymentAnalyzer.exe" "%RELEASE_DIR%\.app\lib\" > nul
    if exist "%SOURCE_DIR%\*.dll" xcopy /Y "%SOURCE_DIR%\*.dll" "%RELEASE_DIR%\.app\lib\" > nul
    if exist "%SOURCE_DIR%\*.pyd" xcopy /Y "%SOURCE_DIR%\*.pyd" "%RELEASE_DIR%\.app\lib\" > nul
)

echo.
echo Step 3: Copying README.txt...
if exist "%SOURCE_DIR%\README.txt" (
    copy "%SOURCE_DIR%\README.txt" "%RELEASE_DIR%\README.txt" > nul
) else (
    echo DeploymentAnalyzer > "%RELEASE_DIR%\README.txt"
    echo ================== >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo Welcome to the Deployment Analyzer application! >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo OVERVIEW: >> "%RELEASE_DIR%\README.txt"
    echo This application allows you to analyze deployment data with powerful visualization >> "%RELEASE_DIR%\README.txt"
    echo capabilities. It provides both command-line and graphical interfaces for data analysis. >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo STARTING THE APPLICATION: >> "%RELEASE_DIR%\README.txt"
    echo Simply double-click DeploymentAnalyzer.exe to run the application in GUI mode. >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo DISK SPACE: >> "%RELEASE_DIR%\README.txt"
    echo This optimized distribution requires approximately 350 MB of disk space. >> "%RELEASE_DIR%\README.txt"
    echo Large sample data files and test directories have been excluded to minimize size. >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo FILE STRUCTURE: >> "%RELEASE_DIR%\README.txt"
    echo - The .app folder contains all application files (hidden for cleaner appearance) >> "%RELEASE_DIR%\README.txt"
    echo - User data is stored in .app\support\data >> "%RELEASE_DIR%\README.txt"
    echo - Log files are written to .app\support\logs >> "%RELEASE_DIR%\README.txt"
    echo - Output files are saved to .app\support\output >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo TROUBLESHOOTING: >> "%RELEASE_DIR%\README.txt"
    echo - If the application fails to start, ensure you have extracted the entire zip file. >> "%RELEASE_DIR%\README.txt"
    echo - The .app folder must exist alongside the executable. >> "%RELEASE_DIR%\README.txt"
    echo - Check log files in .app\support\logs for error details. >> "%RELEASE_DIR%\README.txt"
    echo - On first run, necessary directories will be created automatically. >> "%RELEASE_DIR%\README.txt"
    echo. >> "%RELEASE_DIR%\README.txt"
    echo SUPPORT: >> "%RELEASE_DIR%\README.txt"
    echo For support, please contact the application developer. >> "%RELEASE_DIR%\README.txt"
)

echo.
echo Step 4: Creating app_config.ini...
echo [Paths] > "%RELEASE_DIR%\.app\lib\app_config.ini"
echo DataDir=..\support\data >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo LogsDir=..\support\logs >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo OutputDir=..\support\output >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo InternalDir=. >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo. >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo [Options] >> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo DefaultGUIMode=True >> "%RELEASE_DIR%\.app\lib\app_config.ini"

echo.
echo Step 5: Creating hidden launcher batch...
echo @echo off > "%RELEASE_DIR%\.app\launcher.bat"
echo cd /d "%%~dp0" >> "%RELEASE_DIR%\.app\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%RELEASE_DIR%\.app\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%RELEASE_DIR%\.app\launcher.bat"

echo.
echo Step 6: Creating VBS launcher...
echo Set WshShell = CreateObject("WScript.Shell") > "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo BatchFile = AppDir ^& ".app\launcher.bat" >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo     WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo Else >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo     MsgBox "Error: Required files not found." ^& vbCrLf ^& vbCrLf ^& _ >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo     "The .app folder must exist in the same location as this executable." ^& vbCrLf ^& _ >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo     "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo End If >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "%RELEASE_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 7: Creating temporary batch launcher...
echo @if (1==1) echo off > "%RELEASE_DIR%\DeploymentAnalyzer.bat"
echo cscript //nologo "%%~dp0DeploymentAnalyzer.vbs" >> "%RELEASE_DIR%\DeploymentAnalyzer.bat"
echo exit >> "%RELEASE_DIR%\DeploymentAnalyzer.bat"

echo.
echo Step 8: Hiding auxiliary files...
attrib +h "%RELEASE_DIR%\.app"
attrib +h "%RELEASE_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Step 9: Creating executable launcher...
choice /C YN /M "Would you like to create an EXE launcher instead of a BAT file"
if %ERRORLEVEL% EQU 1 (
    echo Creating EXE launcher...
    powershell -ExecutionPolicy Bypass -File create_exe_launcher.ps1
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Failed to create EXE launcher. Keeping BAT file instead.
    )
) else (
    echo Keeping BAT file launcher.
)

echo.
echo Distribution created successfully at:
echo %RELEASE_DIR%
echo.
echo Contents (visible files only):
dir "%RELEASE_DIR%" /a:-h /b

echo.
echo Done!
pause 