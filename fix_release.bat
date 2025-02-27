@echo off
echo ================================================
echo DEPLOYMENT ANALYZER FIXED RELEASE CREATOR
echo ================================================
echo Running at: %date% %time%

echo Creating release directory structure...
mkdir dist\DeploymentAnalyzer-Release 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app\lib 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app\support 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app\support\logs 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app\support\data 2>nul
mkdir dist\DeploymentAnalyzer-Release\.app\support\output 2>nul

echo Copying DeploymentAnalyzer.exe and dependencies...
copy "dist\DeploymentAnalyzer\DeploymentAnalyzer.exe" "dist\DeploymentAnalyzer-Release\.app\lib\" >nul
copy "dist\DeploymentAnalyzer\*.dll" "dist\DeploymentAnalyzer-Release\.app\lib\" >nul

echo Copying _internal directory with Python modules...
xcopy /E /I /H /Y "dist\DeploymentAnalyzer\_internal" "dist\DeploymentAnalyzer-Release\.app\lib\_internal" >nul

echo Creating app_config.ini...
echo [Application]> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo Name=Deployment Analyzer>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo Version=1.1>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo [Paths]>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo DataDir=.app\support\data>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo LogsDir=.app\support\logs>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"
echo OutputDir=.app\support\output>> "dist\DeploymentAnalyzer-Release\.app\lib\app_config.ini"

echo Creating launcher.bat...
echo @echo off > "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo cd /d "%%~dp0" >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo set PATH=%%~dp0lib;%%PATH%% >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"
echo start "" "%%~dp0lib\DeploymentAnalyzer.exe" --gui >> "dist\DeploymentAnalyzer-Release\.app\launcher.bat"

echo Creating VBS launcher...
echo Set WshShell = CreateObject("WScript.Shell") > "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo AppPath = WScript.ScriptFullName >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo AppDir = Left(AppPath, InStrRev(AppPath, "\")) >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo BatchFile = AppDir ^& ".app\launcher.bat" >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo     WshShell.Run Chr(34) ^& BatchFile ^& Chr(34), 0, False >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo Else >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo     MsgBox "Error: Required files not found." ^& vbCrLf ^& vbCrLf ^& _ >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo     "The .app folder must exist in the same location as this executable." ^& vbCrLf ^& _ >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo     "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo End If >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"
echo Set WshShell = Nothing >> "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs"

echo Copying README.txt...
copy "dist\DeploymentAnalyzer\README.txt" "dist\DeploymentAnalyzer-Release\" >nul

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
echo csc /target:winexe /out:"dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.exe" /reference:System.Windows.Forms.dll TempCompiler.cs >> temp_compile.bat
call temp_compile.bat
del TempCompiler.cs
del temp_compile.bat

echo Updating README.txt...
copy "dist\DeploymentAnalyzer-Release\README.txt" "dist\DeploymentAnalyzer-Release\README.txt.bak" >nul
echo ============================================= > "dist\DeploymentAnalyzer-Release\README.txt"
echo Deployment Analyzer >> "dist\DeploymentAnalyzer-Release\README.txt"
echo ============================================= >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo USER GUIDE: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo To start the application: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - Simply double-click "DeploymentAnalyzer.exe" in this folder >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo This version features a clean user interface with only the executable visible in the main folder. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo All supporting files are hidden in the .app directory for your convenience. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo TROUBLESHOOTING GUIDE: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo If you're having trouble running the application: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo 1. Check the .app\support\logs directory for log files >> "dist\DeploymentAnalyzer-Release\README.txt"
echo 2. Make sure all required directories exist: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo    - .app\support\data >> "dist\DeploymentAnalyzer-Release\README.txt"
echo    - .app\support\logs >> "dist\DeploymentAnalyzer-Release\README.txt"
echo    - .app\support\output >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo 3. If you see "Missing DLL" errors: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo    - Install Microsoft Visual C++ Redistributable 2019 (or later) >> "dist\DeploymentAnalyzer-Release\README.txt"
echo    - Available at: https://aka.ms/vs/17/release/vc_redist.x64.exe >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo Technical Support: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo If you continue to have issues, please contact technical support >> "dist\DeploymentAnalyzer-Release\README.txt"
echo with the contents of the logs directory. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - User data is stored in .app\support\data >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - Log files are written to .app\support\logs >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - Output files are saved to .app\support\output >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo TROUBLESHOOTING: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - If the application fails to start, ensure you have extracted the entire zip file. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - The .app folder must exist alongside the executable. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - Check log files in .app\support\logs for error details. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo - On first run, necessary directories will be created automatically. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo. >> "dist\DeploymentAnalyzer-Release\README.txt"
echo SUPPORT: >> "dist\DeploymentAnalyzer-Release\README.txt"
echo For support, please contact the application developer. >> "dist\DeploymentAnalyzer-Release\README.txt"

echo.
echo Hiding the .app directory...
attrib +h "dist\DeploymentAnalyzer-Release\.app" >nul

echo.
echo Distribution created successfully at:
echo dist\DeploymentAnalyzer-Release
echo.
echo Contents (visible files only):
echo DeploymentAnalyzer.exe
echo README.txt
echo.
echo Done!
pause 