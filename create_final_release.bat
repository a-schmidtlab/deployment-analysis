@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FINAL RELEASE CREATOR
echo ================================================
echo Running at: %date% %time%

set SOURCE_DIR=dist\DeploymentAnalyzer-Final
set RELEASE_DIR=dist\DeploymentAnalyzer-Release
echo Source directory: %SOURCE_DIR%
echo Target directory: %RELEASE_DIR%

if not exist %SOURCE_DIR% (
    echo ERROR: Source directory not found!
    pause
    exit /b 1
)

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
xcopy /E /I /Y "%SOURCE_DIR%\.app\lib\*" "%RELEASE_DIR%\.app\lib\" > nul

echo.
echo Step 3: Copying README.txt...
copy "%SOURCE_DIR%\README.txt" "%RELEASE_DIR%\README.txt" > nul

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
echo Step 7: Creating main launcher...
echo @echo off > "%RELEASE_DIR%\DeploymentAnalyzer.bat"
echo cscript //nologo "%%~dp0DeploymentAnalyzer.vbs" >> "%RELEASE_DIR%\DeploymentAnalyzer.bat"
echo exit >> "%RELEASE_DIR%\DeploymentAnalyzer.bat"

echo.
echo Step 8: Hiding auxiliary files...
attrib +h "%RELEASE_DIR%\.app"
attrib +h "%RELEASE_DIR%\DeploymentAnalyzer.vbs"

echo.
echo Distribution created successfully at:
echo %RELEASE_DIR%
echo.
echo Contents (visible files only):
dir "%RELEASE_DIR%" /a:-h /b

echo.
echo Done!
pause 