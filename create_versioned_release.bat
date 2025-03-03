@echo off
setlocal EnableDelayedExpansion

echo ================================================
echo DEPLOYMENT ANALYZER VERSIONED RELEASE CREATOR
echo ================================================
echo Running at: %date% %time%

REM Extract version from version.py using Python
for /f "tokens=*" %%a in ('python -c "import version; print(version.VERSION)"') do (
    set VERSION=%%a
)

REM Extract version date from version.py
for /f "tokens=*" %%a in ('python -c "import version; print(version.VERSION_DATE)"') do (
    set VERSION_DATE=%%a
)

echo Detected version: !VERSION! (Date: !VERSION_DATE!)

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

set RELEASE_DIR=dist\DeploymentAnalyzer-!VERSION!-Release

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
echo Target directory: !RELEASE_DIR!

echo.
echo Step 1: Creating target directory structure...
if exist !RELEASE_DIR! rmdir /s /q !RELEASE_DIR!
mkdir !RELEASE_DIR!
mkdir "!RELEASE_DIR!\.app"
mkdir "!RELEASE_DIR!\.app\lib"
mkdir "!RELEASE_DIR!\.app\support"
mkdir "!RELEASE_DIR!\.app\support\data"
mkdir "!RELEASE_DIR!\.app\support\logs"
mkdir "!RELEASE_DIR!\.app\support\output"

echo.
echo Step 2: Copying lib directory...
if exist "%SOURCE_DIR%\_internal" (
    mkdir "!RELEASE_DIR!\.app\lib\_internal"
    xcopy /E /I /Y "%SOURCE_DIR%\_internal\*" "!RELEASE_DIR!\.app\lib\_internal\" > nul
)

if exist "%SOURCE_DIR%\DeploymentAnalyzer.exe" (
    xcopy /Y "%SOURCE_DIR%\DeploymentAnalyzer.exe" "!RELEASE_DIR!\.app\lib\" > nul
)

echo.
echo Step 3: Copying README.txt...
if exist "%SOURCE_DIR%\README.txt" (
    copy "%SOURCE_DIR%\README.txt" "!RELEASE_DIR!\README.txt" > nul
) else (
    echo DeploymentAnalyzer v!VERSION! > "!RELEASE_DIR!\README.txt"
    echo ======================= >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo Welcome to the Deployment Analyzer application! >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo OVERVIEW: >> "!RELEASE_DIR!\README.txt"
    echo This application allows you to analyze deployment data with powerful visualization >> "!RELEASE_DIR!\README.txt"
    echo capabilities. It provides both command-line and graphical interfaces for data analysis. >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo STARTING THE APPLICATION: >> "!RELEASE_DIR!\README.txt"
    echo Simply double-click DeploymentAnalyzer.exe to run the application in GUI mode. >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo DISK SPACE: >> "!RELEASE_DIR!\README.txt"
    echo This optimized distribution requires approximately 350 MB of disk space. >> "!RELEASE_DIR!\README.txt"
    echo Large sample data files and test directories have been excluded to minimize size. >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo FILE STRUCTURE: >> "!RELEASE_DIR!\README.txt"
    echo - The .app folder contains all application files (hidden for cleaner appearance) >> "!RELEASE_DIR!\README.txt"
    echo - User data is stored in .app\support\data >> "!RELEASE_DIR!\README.txt"
    echo - Log files are written to .app\support\logs >> "!RELEASE_DIR!\README.txt"
    echo - Output files are saved to .app\support\output >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo TROUBLESHOOTING: >> "!RELEASE_DIR!\README.txt"
    echo - If the application fails to start, ensure you have extracted the entire zip file. >> "!RELEASE_DIR!\README.txt"
    echo - The .app folder must exist alongside the executable. >> "!RELEASE_DIR!\README.txt"
    echo - Check log files in .app\support\logs for error details. >> "!RELEASE_DIR!\README.txt"
    echo - On first run, necessary directories will be created automatically. >> "!RELEASE_DIR!\README.txt"
    echo. >> "!RELEASE_DIR!\README.txt"
    echo SUPPORT: >> "!RELEASE_DIR!\README.txt"
    echo For support, please contact the application developer. >> "!RELEASE_DIR!\README.txt"
)

echo.
echo Step 4: Creating app_config.ini...
echo [Paths] > "!RELEASE_DIR!\.app\lib\app_config.ini"
echo DataDir=..\support\data >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo LogsDir=..\support\logs >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo OutputDir=..\support\output >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo InternalDir=. >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo. >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo [Options] >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo DefaultGUIMode=True >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo. >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo [Application] >> "!RELEASE_DIR!\.app\lib\app_config.ini"
echo Version=!VERSION! >> "!RELEASE_DIR!\.app\lib\app_config.ini"

echo.
echo Step 5: Creating hidden launcher batch...
echo @echo off > "!RELEASE_DIR!\.app\launcher.bat"
echo cd /d "%%~dp0" >> "!RELEASE_DIR!\.app\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "!RELEASE_DIR!\.app\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "!RELEASE_DIR!\.app\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "!RELEASE_DIR!\.app\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "!RELEASE_DIR!\.app\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "!RELEASE_DIR!\.app\launcher.bat"

echo.
echo Step 6: Creating VBS launcher...
echo Set WshShell = CreateObject("WScript.Shell") > "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo BatchFile = AppDir ^& ".app\launcher.bat" >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo     WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo Else >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo     MsgBox "Error: Required files not found." ^& vbCrLf ^& vbCrLf ^& _ >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo     "The .app folder must exist in the same location as this executable." ^& vbCrLf ^& _ >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo     "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo End If >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "!RELEASE_DIR!\DeploymentAnalyzer.vbs"

echo.
echo Step 7: Cleaning up and hiding auxiliary files...
attrib +h "!RELEASE_DIR!\.app"

echo. 
echo Step 8: Creating updated README.txt...
echo --------------------------------------------------------- > "!RELEASE_DIR!\README.txt" 
echo DeploymentAnalyzer v!VERSION! >> "!RELEASE_DIR!\README.txt"
echo --------------------------------------------------------- >> "!RELEASE_DIR!\README.txt"
echo. >> "!RELEASE_DIR!\README.txt"
echo GETTING STARTED: >> "!RELEASE_DIR!\README.txt"
echo Double-click DeploymentAnalyzer.exe to start the application. >> "!RELEASE_DIR!\README.txt"
echo. >> "!RELEASE_DIR!\README.txt"
echo IMPORTANT: >> "!RELEASE_DIR!\README.txt"
echo * Do not move or rename the DeploymentAnalyzer.exe file >> "!RELEASE_DIR!\README.txt"
echo * Do not delete or modify the .app folder (hidden folder) >> "!RELEASE_DIR!\README.txt"
echo * All application files are contained in the .app folder >> "!RELEASE_DIR!\README.txt"
echo. >> "!RELEASE_DIR!\README.txt"
echo FILE STRUCTURE: >> "!RELEASE_DIR!\README.txt"
echo - DeploymentAnalyzer.exe - Main launcher >> "!RELEASE_DIR!\README.txt"
echo - .app (hidden) - Contains all application files >> "!RELEASE_DIR!\README.txt"
echo   - lib - Main program files >> "!RELEASE_DIR!\README.txt"
echo   - support - Data, logs, and output directories >> "!RELEASE_DIR!\README.txt"
echo. >> "!RELEASE_DIR!\README.txt"
echo TROUBLESHOOTING: >> "!RELEASE_DIR!\README.txt"
echo - If the application fails to start, ensure you have extracted the entire zip file. >> "!RELEASE_DIR!\README.txt"
echo - The .app folder must exist alongside the launcher. >> "!RELEASE_DIR!\README.txt"
echo - Check log files in .app\support\logs for error details. >> "!RELEASE_DIR!\README.txt"
echo. >> "!RELEASE_DIR!\README.txt"
echo VERSION: !VERSION! (Released: !VERSION_DATE!) >> "!RELEASE_DIR!\README.txt"

echo.
echo Step 9: Creating proper EXE launcher...
echo Using multiple launcher creation methods for compatibility...

REM First try the C# compiler method
echo Creating a dummy EXE launcher using C# compiler...
echo @echo off > temp_compile.bat
echo echo using System; > TempCompiler.cs
echo echo using System.Diagnostics; >> TempCompiler.cs
echo echo using System.IO; >> TempCompiler.cs
echo echo using System.Windows.Forms; >> TempCompiler.cs
echo echo. >> TempCompiler.cs
echo echo class Program >> TempCompiler.cs
echo echo { >> TempCompiler.cs
echo echo     static void Main() >> TempCompiler.cs
echo echo     { >> TempCompiler.cs
echo echo         try >> TempCompiler.cs
echo echo         { >> TempCompiler.cs
echo echo             string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location; >> TempCompiler.cs
echo echo             string directory = Path.GetDirectoryName(exePath); >> TempCompiler.cs
echo echo             string vbsPath = Path.Combine(directory, "DeploymentAnalyzer.vbs"); >> TempCompiler.cs
echo echo. >> TempCompiler.cs
echo echo             if (!File.Exists(vbsPath)) >> TempCompiler.cs
echo echo             { >> TempCompiler.cs
echo echo                 MessageBox.Show("Error: Required files not found.\n\n" + >> TempCompiler.cs
echo echo                     "The DeploymentAnalyzer.vbs script must exist in the same location as this executable.\n" + >> TempCompiler.cs
echo echo                     "Please refer to the README.txt file for more information.", >> TempCompiler.cs
echo echo                     "Deployment Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Error); >> TempCompiler.cs
echo echo                 return; >> TempCompiler.cs
echo echo             } >> TempCompiler.cs
echo echo. >> TempCompiler.cs
echo echo             ProcessStartInfo startInfo = new ProcessStartInfo(); >> TempCompiler.cs
echo echo             startInfo.FileName = "wscript.exe"; >> TempCompiler.cs
echo echo             startInfo.Arguments = "//nologo \"" + vbsPath + "\""; >> TempCompiler.cs
echo echo             startInfo.CreateNoWindow = true; >> TempCompiler.cs
echo echo             startInfo.UseShellExecute = false; >> TempCompiler.cs
echo echo. >> TempCompiler.cs
echo echo             Process.Start(startInfo); >> TempCompiler.cs
echo echo         } >> TempCompiler.cs
echo echo         catch (Exception ex) >> TempCompiler.cs
echo echo         { >> TempCompiler.cs
echo echo             MessageBox.Show("Error starting application: " + ex.Message, >> TempCompiler.cs
echo echo                 "Deployment Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Error); >> TempCompiler.cs
echo echo         } >> TempCompiler.cs
echo echo     } >> TempCompiler.cs
echo echo } >> TempCompiler.cs
echo. >> temp_compile.bat
echo csc /target:winexe /out:"!RELEASE_DIR!\DeploymentAnalyzer.exe" /reference:System.Windows.Forms.dll TempCompiler.cs >> temp_compile.bat

echo Attempting to create launcher with C# compiler...
call temp_compile.bat > nul 2>&1
set CSC_SUCCESS=!ERRORLEVEL!

if !CSC_SUCCESS! NEQ 0 (
    echo C# compiler not available, trying .NET Framework compiler...
    echo Attempting to locate .NET Framework...
    
    REM Try .NET Framework compiler directly
    if exist "%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
        echo Found .NET Framework 4 compiler...
        "%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:winexe /out:"!RELEASE_DIR!\DeploymentAnalyzer.exe" /reference:System.Windows.Forms.dll TempCompiler.cs > nul 2>&1
        set CSC_SUCCESS=!ERRORLEVEL!
    )
)

if !CSC_SUCCESS! NEQ 0 (
    echo Compiler methods failed, using alternative approach...
    echo Creating shortcut-based launcher...
    
    REM Fallback to VBS file as the launcher
    copy "!RELEASE_DIR!\DeploymentAnalyzer.vbs" "!RELEASE_DIR!\DeploymentAnalyzer.exe" > nul
    attrib +h "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
    echo NOTE: Created simple launcher. For a proper executable, install .NET Framework or Visual Studio.
) else (
    echo Successfully created executable launcher!
    attrib +h "!RELEASE_DIR!\DeploymentAnalyzer.vbs"
)

REM Clean up temporary files
del TempCompiler.cs > nul 2>&1
del temp_compile.bat > nul 2>&1

echo.
echo Distribution created successfully at:
echo !RELEASE_DIR!
echo.
echo Contents (visible files only):
dir "!RELEASE_DIR!" /a:-h /b

echo.
echo Done!
pause 