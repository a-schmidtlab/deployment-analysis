@echo off
echo Enhanced Building DeploymentAnalyzer...

set TEMP_BUILD_DIR=C:\temp\deploy_build
set WORK_PATH=%TEMP_BUILD_DIR%\build
set DIST_PATH=%TEMP_BUILD_DIR%\dist

echo Using build directories:
echo Working directory: %WORK_PATH%
echo Distribution directory: %DIST_PATH%

echo Cleaning previous builds...
rmdir /s /q "%WORK_PATH%" 2>nul
rmdir /s /q "%DIST_PATH%" 2>nul
mkdir "%WORK_PATH%" 2>nul
mkdir "%DIST_PATH%" 2>nul

echo Running PyInstaller with enhanced options...

:: Get Python information
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.prefix)"') do set PYTHON_PREFIX=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.version.split()[0])"') do set PYTHON_VER=%%i

echo Python executable: %PYTHON_EXE%
echo Python prefix: %PYTHON_PREFIX%
echo Python version: %PYTHON_VER%

:: Ensure we copy Python DLLs
set PYTHON_DLL_DIR=%PYTHON_PREFIX%

echo Running PyInstaller...
pyinstaller ^
    --workpath="%WORK_PATH%" ^
    --distpath="%DIST_PATH%" ^
    --clean ^
    --onedir ^
    --windowed ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=seaborn ^
    --hidden-import=configparser ^
    --hidden-import=tkinter ^
    --hidden-import=PIL ^
    --add-data "data;data" ^
    --add-data "logs;logs" ^
    --add-data "output;output" ^
    --add-data "deployment-analyse.py;." ^
    --add-binary "%PYTHON_PREFIX%\python*.dll;." ^
    --add-binary "%PYTHON_PREFIX%\DLLs\*.dll;." ^
    --collect-all pandas ^
    --collect-all numpy ^
    --collect-all matplotlib ^
    --collect-all seaborn ^
    --collect-all openpyxl ^
    --collect-all PIL ^
    --name "DeploymentAnalyzer" ^
    standalone.py

if %ERRORLEVEL% NEQ 0 (
    echo Build failed with error code %ERRORLEVEL%
) else (
    echo Build completed successfully!
    echo Executable is located at: %DIST_PATH%\DeploymentAnalyzer\DeploymentAnalyzer.exe
    
    echo Copying executable to project directory...
    mkdir dist 2>nul
    rmdir /s /q "dist\DeploymentAnalyzer" 2>nul
    xcopy /E /I /Y "%DIST_PATH%\DeploymentAnalyzer" "dist\DeploymentAnalyzer"
    
    echo Creating support directories...
    mkdir "dist\DeploymentAnalyzer\support" 2>nul
    mkdir "dist\DeploymentAnalyzer\support\data" 2>nul
    mkdir "dist\DeploymentAnalyzer\support\logs" 2>nul
    mkdir "dist\DeploymentAnalyzer\support\output" 2>nul
    
    echo Moving internal files to support directory...
    move "dist\DeploymentAnalyzer\_internal" "dist\DeploymentAnalyzer\support\" 2>nul
    
    echo Creating configuration file...
    echo [Paths] > "dist\DeploymentAnalyzer\app_config.ini"
    echo DataDir=support\data >> "dist\DeploymentAnalyzer\app_config.ini"
    echo LogsDir=support\logs >> "dist\DeploymentAnalyzer\app_config.ini"
    echo OutputDir=support\output >> "dist\DeploymentAnalyzer\app_config.ini"
    echo InternalDir=support\_internal >> "dist\DeploymentAnalyzer\app_config.ini"
    echo. >> "dist\DeploymentAnalyzer\app_config.ini"
    echo [Options] >> "dist\DeploymentAnalyzer\app_config.ini"
    echo DefaultGUIMode=True >> "dist\DeploymentAnalyzer\app_config.ini"
    
    echo Creating user-friendly launchers...
    echo @echo off > "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo echo Starting Deployment Analyzer... >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo REM Make sure required directories exist >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo REM Launch the application with the GUI flag >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo start "" "%%~dp0DeploymentAnalyzer.exe" --gui >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    echo echo If the application does not start, please check the support\logs directory for error information. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
    
    echo Option Explicit > "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo ' Deployment Analyzer Launcher Script >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo ' This script launches the DeploymentAnalyzer with GUI mode without showing a command prompt >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo Dim WshShell, strAppPath >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo Set WshShell = CreateObject("WScript.Shell") >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo ' Get the path of this script >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo strAppPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "") >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo ' Launch the application without showing a command window >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo WshShell.Run """" ^& strAppPath ^& "DeploymentAnalyzer.exe"" --gui", 0, False >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo. >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    echo Set WshShell = Nothing >> "dist\DeploymentAnalyzer\DeploymentAnalyzer.vbs"
    
    echo Creating README file...
    echo ============================================= > "dist\DeploymentAnalyzer\README.txt"
    echo Deployment Analyzer >> "dist\DeploymentAnalyzer\README.txt"
    echo ============================================= >> "dist\DeploymentAnalyzer\README.txt"
    echo. >> "dist\DeploymentAnalyzer\README.txt"
    echo Quick Start Guide: >> "dist\DeploymentAnalyzer\README.txt"
    echo. >> "dist\DeploymentAnalyzer\README.txt"
    echo 1. To start the application, double-click on one of these files: >> "dist\DeploymentAnalyzer\README.txt"
    echo    - DeploymentAnalyzer.exe (Main application) >> "dist\DeploymentAnalyzer\README.txt"
    echo    - DeploymentAnalyzer.vbs (Silent launcher - no command window) >> "dist\DeploymentAnalyzer\README.txt"
    echo    - "Deployment Analyzer.bat" (Batch launcher with console) >> "dist\DeploymentAnalyzer\README.txt"
    echo. >> "dist\DeploymentAnalyzer\README.txt"
    echo 2. All application data will be stored in the support folder: >> "dist\DeploymentAnalyzer\README.txt"
    echo    - support\data: Input data files >> "dist\DeploymentAnalyzer\README.txt"
    echo    - support\logs: Log files (check here if you have issues) >> "dist\DeploymentAnalyzer\README.txt"
    echo    - support\output: Generated output files >> "dist\DeploymentAnalyzer\README.txt"
    echo. >> "dist\DeploymentAnalyzer\README.txt"
    echo Technical Support: >> "dist\DeploymentAnalyzer\README.txt"
    echo If you encounter any issues, please check the log files in the support\logs folder >> "dist\DeploymentAnalyzer\README.txt"
    echo and contact technical support. >> "dist\DeploymentAnalyzer\README.txt"
    
    echo Copying VC runtime files...
    copy "%WINDIR%\System32\msvcp140.dll" "dist\DeploymentAnalyzer\" 2>nul
    copy "%WINDIR%\System32\vcruntime140.dll" "dist\DeploymentAnalyzer\" 2>nul
    copy "%WINDIR%\System32\vcruntime140_1.dll" "dist\DeploymentAnalyzer\" 2>nul
)

echo Done.
echo.
echo If the application doesn't start, check for errors and try to run enhanced_build.bat again.
pause 