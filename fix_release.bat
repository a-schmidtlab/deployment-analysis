@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FIXED RELEASE CREATOR
echo ================================================
echo Running at: %date% %time%

echo Retrieving version information...
for /f "tokens=*" %%a in ('python -c "from version import VERSION; print(VERSION)"') do set APP_VERSION=%%a
echo Building version: %APP_VERSION%

echo Creating release directory structure...
set RELEASE_DIR=dist\DeploymentAnalyzer-%APP_VERSION%-Release
mkdir %RELEASE_DIR% 2>nul
mkdir %RELEASE_DIR%\.app 2>nul
mkdir %RELEASE_DIR%\.app\lib 2>nul
mkdir %RELEASE_DIR%\.app\support 2>nul
mkdir %RELEASE_DIR%\.app\support\logs 2>nul
mkdir %RELEASE_DIR%\.app\support\data 2>nul
mkdir %RELEASE_DIR%\.app\support\output 2>nul

echo Copying DeploymentAnalyzer.exe and dependencies...
copy "dist\DeploymentAnalyzer\DeploymentAnalyzer.exe" "%RELEASE_DIR%\.app\lib\" >nul
copy "dist\DeploymentAnalyzer\*.dll" "%RELEASE_DIR%\.app\lib\" >nul

echo Copying _internal directory with Python modules...
xcopy /E /I /H /Y "dist\DeploymentAnalyzer\_internal" "%RELEASE_DIR%\.app\lib\_internal" >nul

echo Creating app_config.ini...
echo [Application]> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo Name=Deployment Analyzer>> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo Version=%APP_VERSION%>> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo [Paths]>> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo DataDir=.app\support\data>> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo LogsDir=.app\support\logs>> "%RELEASE_DIR%\.app\lib\app_config.ini"
echo OutputDir=.app\support\output>> "%RELEASE_DIR%\.app\lib\app_config.ini"

echo Creating launcher.bat...
echo @echo off > "%RELEASE_DIR%\.app\launcher.bat"
echo cd /d "%%~dp0" >> "%RELEASE_DIR%\.app\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "%RELEASE_DIR%\.app\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "%RELEASE_DIR%\.app\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "%RELEASE_DIR%\.app\launcher.bat"

echo Creating VBS launcher...
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

echo Copying README.txt...
copy "dist\DeploymentAnalyzer\README.txt" "%RELEASE_DIR%\" >nul

echo Creating a dummy EXE launcher that just calls the VBS script...
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
echo echo             startInfo.FileName = "cscript.exe"; >> TempCompiler.cs
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
echo csc /target:winexe /out:"%RELEASE_DIR%\DeploymentAnalyzer.exe" /reference:System.Windows.Forms.dll TempCompiler.cs >> temp_compile.bat
call temp_compile.bat
del TempCompiler.cs
del temp_compile.bat

REM Check if the executable was created successfully
if not exist "%RELEASE_DIR%\DeploymentAnalyzer.exe" (
    echo C# compiler not found. Trying alternative methods...
    
    REM Try using the PowerShell script if it exists
    if exist "create_exe.ps1" (
        echo Running PowerShell script to create executable...
        powershell -ExecutionPolicy Bypass -File create_exe.ps1
    ) else (
        echo PowerShell script not found. Creating simple executable...
        copy "%RELEASE_DIR%\DeploymentAnalyzer.vbs" "%RELEASE_DIR%\DeploymentAnalyzer.exe" >nul
        echo Simple executable created as fallback.
    )
)

echo Updating README.txt...
copy "%RELEASE_DIR%\README.txt" "%RELEASE_DIR%\README.txt.bak" >nul
echo ============================================= > "%RELEASE_DIR%\README.txt"
echo Deployment Analyzer v%APP_VERSION% >> "%RELEASE_DIR%\README.txt"
echo ============================================= >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo (c) 2025 by Axel Schmidt >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo SCHNELLSTART >> "%RELEASE_DIR%\README.txt"
echo Simply double-click on DeploymentAnalyzer.exe to start the application. >> "%RELEASE_DIR%\README.txt"
echo A warning may appear first. Click on "More Info" and then on "Run anyway". >> "%RELEASE_DIR%\README.txt"
echo Next, a console window will open to set up the software environment. This can take up to one minute. >> "%RELEASE_DIR%\README.txt"
echo In our app, click "Import" to upload your .csv data. >> "%RELEASE_DIR%\README.txt"
echo The app needs all files in the folder. Therefore, always move the entire folder. >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo USER GUIDE: >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo This version features a clean user interface with only the executable visible in the main folder. >> "%RELEASE_DIR%\README.txt"
echo All supporting files are hidden in the .app directory for your convenience. >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo TROUBLESHOOTING: >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo If you're having trouble running the application: >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo 1. Check the .app\support\logs directory for log files >> "%RELEASE_DIR%\README.txt"
echo 2. Make sure all required directories exist: >> "%RELEASE_DIR%\README.txt"
echo    - .app\support\data >> "%RELEASE_DIR%\README.txt"
echo    - .app\support\logs >> "%RELEASE_DIR%\README.txt"
echo    - .app\support\output >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo 3. If you see "Missing DLL" errors: >> "%RELEASE_DIR%\README.txt"
echo    - Install Microsoft Visual C++ Redistributable 2019 (or later) >> "%RELEASE_DIR%\README.txt"
echo    - Available at: https://aka.ms/vs/17/release/vc_redist.x64.exe >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo 4. Common issues: >> "%RELEASE_DIR%\README.txt"
echo    - If the application fails to start, ensure you have extracted the entire zip file. >> "%RELEASE_DIR%\README.txt"
echo    - The .app folder must exist alongside the executable. >> "%RELEASE_DIR%\README.txt"
echo    - On first run, necessary directories will be created automatically. >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo SUPPORT: >> "%RELEASE_DIR%\README.txt"
echo If you continue to have issues, please contact technical support with the contents of the logs directory. >> "%RELEASE_DIR%\README.txt"
echo - User data is stored in .app\support\data >> "%RELEASE_DIR%\README.txt"
echo - Log files are written to .app\support\logs >> "%RELEASE_DIR%\README.txt"
echo - Output files are saved to .app\support\output >> "%RELEASE_DIR%\README.txt"

echo Removing backup README file...
del "%RELEASE_DIR%\README.txt.bak" >nul

echo.
echo Hiding the .app directory...
attrib +h "%RELEASE_DIR%\.app" >nul

echo.
echo Distribution created successfully at:
echo %RELEASE_DIR%
echo.
echo Contents (visible files only):
echo DeploymentAnalyzer.exe
echo README.txt
echo.
echo Done!
pause 