@echo off
echo ===============================================
echo ULTIMATE DEPLOYMENT ANALYZER BUILD SCRIPT
echo ===============================================
echo Running at: %date% %time%
echo.

:: Set paths
set TEMP_BUILD_DIR=C:\temp\deploy_build
set WORK_PATH=%TEMP_BUILD_DIR%\build
set DIST_PATH=%TEMP_BUILD_DIR%\dist
set LOG_FILE=build_log.txt

echo Build started > %LOG_FILE%
echo Date: %date% Time: %time% >> %LOG_FILE%
echo Python information: >> %LOG_FILE%

:: Get Python information
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%i
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.prefix)"') do set PYTHON_PREFIX=%%i
for /f "tokens=*" %%i in ('python -c "import sys; import platform; print(sys.version.split()[0] + ' ' + platform.architecture()[0])"') do set PYTHON_INFO=%%i

echo Python executable: %PYTHON_EXE% >> %LOG_FILE%
echo Python prefix: %PYTHON_PREFIX% >> %LOG_FILE%
echo Python version: %PYTHON_INFO% >> %LOG_FILE%

echo Python executable: %PYTHON_EXE%
echo Python prefix: %PYTHON_PREFIX%
echo Python version: %PYTHON_INFO%

:: Clean previous builds
echo.
echo Cleaning previous builds...
rmdir /s /q "%WORK_PATH%" 2>nul
rmdir /s /q "%DIST_PATH%" 2>nul
mkdir "%WORK_PATH%" 2>nul
mkdir "%DIST_PATH%" 2>nul

echo Cleaned previous builds >> %LOG_FILE%

:: Verify Python modules
echo.
echo Verifying required Python modules...
python -c "import pandas, numpy, matplotlib, seaborn, tkinter, PIL; print('All modules imported successfully!')" >> %LOG_FILE% 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Missing required Python modules!
    echo ERROR: Missing required Python modules! >> %LOG_FILE%
    echo Check build_log.txt for details.
    exit /b 1
)
echo Required modules verified >> %LOG_FILE%

:: Generate a directory manifest list for verification
echo.
echo Generating DLL manifest of Python directory...
dir /s /b "%PYTHON_PREFIX%\*.dll" > python_dlls.txt
echo Number of Python DLLs found: >> %LOG_FILE%
find /c "dll" python_dlls.txt >> %LOG_FILE%

:: Generate spec file for PyInstaller
echo.
echo Generating spec file...
echo # -*- mode: python -*- > DeploymentAnalyzer_ultimate.spec
echo from PyInstaller.utils.hooks import collect_all >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo datas = [('data', 'data'), ('logs', 'logs'), ('output', 'output'), ('deployment-analyse.py', '.')] >> DeploymentAnalyzer_ultimate.spec
echo binaries = [] >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Explicitly add Python DLLs >> DeploymentAnalyzer_ultimate.spec
echo import os, glob >> DeploymentAnalyzer_ultimate.spec
echo python_dlls = glob.glob(os.path.join(r'%PYTHON_PREFIX%', '*.dll')) >> DeploymentAnalyzer_ultimate.spec
echo python_dlls += glob.glob(os.path.join(r'%PYTHON_PREFIX%', 'DLLs', '*.dll')) >> DeploymentAnalyzer_ultimate.spec
echo for dll in python_dlls: >> DeploymentAnalyzer_ultimate.spec
echo     binaries.append((dll, '.')) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # VC Runtime files >> DeploymentAnalyzer_ultimate.spec
echo vc_dlls = glob.glob(os.path.join(os.environ['WINDIR'], 'System32', 'msvcp*.dll')) >> DeploymentAnalyzer_ultimate.spec
echo vc_dlls += glob.glob(os.path.join(os.environ['WINDIR'], 'System32', 'vcruntime*.dll')) >> DeploymentAnalyzer_ultimate.spec
echo for dll in vc_dlls: >> DeploymentAnalyzer_ultimate.spec
echo     binaries.append((dll, '.')) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Add TK/TCL resources >> DeploymentAnalyzer_ultimate.spec
echo import site >> DeploymentAnalyzer_ultimate.spec
echo site_packages = site.getsitepackages()[0] >> DeploymentAnalyzer_ultimate.spec
echo tcl_dir = os.path.join(r'%PYTHON_PREFIX%', 'tcl') >> DeploymentAnalyzer_ultimate.spec
echo if os.path.exists(tcl_dir): >> DeploymentAnalyzer_ultimate.spec
echo     for root, dirs, files in os.walk(tcl_dir): >> DeploymentAnalyzer_ultimate.spec
echo         for file in files: >> DeploymentAnalyzer_ultimate.spec
echo             full_path = os.path.join(root, file) >> DeploymentAnalyzer_ultimate.spec
echo             rel_path = os.path.relpath(full_path, r'%PYTHON_PREFIX%') >> DeploymentAnalyzer_ultimate.spec
echo             target_dir = os.path.dirname(rel_path) >> DeploymentAnalyzer_ultimate.spec
echo             datas.append((full_path, target_dir)) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Add package dependencies >> DeploymentAnalyzer_ultimate.spec
echo hiddenimports = ['pandas', 'numpy', 'matplotlib', 'matplotlib.backends.backend_tkagg', >> DeploymentAnalyzer_ultimate.spec
echo                  'seaborn', 'configparser', 'tkinter', 'PIL', 'csv', 'openpyxl', >> DeploymentAnalyzer_ultimate.spec
echo                  'logging', 'logging.handlers', 'datetime', 'argparse', 'threading'] >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Collect all dependencies >> DeploymentAnalyzer_ultimate.spec
echo packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'PIL', 'openpyxl'] >> DeploymentAnalyzer_ultimate.spec
echo for package in packages: >> DeploymentAnalyzer_ultimate.spec
echo     tmp_ret = collect_all(package) >> DeploymentAnalyzer_ultimate.spec
echo     datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2] >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Create the Analysis object >> DeploymentAnalyzer_ultimate.spec
echo a = Analysis( >> DeploymentAnalyzer_ultimate.spec
echo     ['standalone.py'], >> DeploymentAnalyzer_ultimate.spec
echo     pathex=[], >> DeploymentAnalyzer_ultimate.spec
echo     binaries=binaries, >> DeploymentAnalyzer_ultimate.spec
echo     datas=datas, >> DeploymentAnalyzer_ultimate.spec
echo     hiddenimports=hiddenimports, >> DeploymentAnalyzer_ultimate.spec
echo     hookspath=[], >> DeploymentAnalyzer_ultimate.spec
echo     hooksconfig={}, >> DeploymentAnalyzer_ultimate.spec
echo     runtime_hooks=[], >> DeploymentAnalyzer_ultimate.spec
echo     excludes=[], >> DeploymentAnalyzer_ultimate.spec
echo     noarchive=False, >> DeploymentAnalyzer_ultimate.spec
echo     optimize=0, >> DeploymentAnalyzer_ultimate.spec
echo ) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Add the pyz >> DeploymentAnalyzer_ultimate.spec
echo pyz = PYZ(a.pure) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Create the exe >> DeploymentAnalyzer_ultimate.spec
echo exe = EXE( >> DeploymentAnalyzer_ultimate.spec
echo     pyz, >> DeploymentAnalyzer_ultimate.spec
echo     a.scripts, >> DeploymentAnalyzer_ultimate.spec
echo     [], >> DeploymentAnalyzer_ultimate.spec
echo     exclude_binaries=True, >> DeploymentAnalyzer_ultimate.spec
echo     name='DeploymentAnalyzer', >> DeploymentAnalyzer_ultimate.spec
echo     debug=False, >> DeploymentAnalyzer_ultimate.spec
echo     bootloader_ignore_signals=False, >> DeploymentAnalyzer_ultimate.spec
echo     strip=False, >> DeploymentAnalyzer_ultimate.spec
echo     upx=True, >> DeploymentAnalyzer_ultimate.spec
echo     console=True, # Set to True for debugging >> DeploymentAnalyzer_ultimate.spec
echo     disable_windowed_traceback=False, >> DeploymentAnalyzer_ultimate.spec
echo     argv_emulation=False, >> DeploymentAnalyzer_ultimate.spec
echo     target_arch=None, >> DeploymentAnalyzer_ultimate.spec
echo     codesign_identity=None, >> DeploymentAnalyzer_ultimate.spec
echo     entitlements_file=None, >> DeploymentAnalyzer_ultimate.spec
echo ) >> DeploymentAnalyzer_ultimate.spec
echo. >> DeploymentAnalyzer_ultimate.spec
echo # Create the collection >> DeploymentAnalyzer_ultimate.spec
echo coll = COLLECT( >> DeploymentAnalyzer_ultimate.spec
echo     exe, >> DeploymentAnalyzer_ultimate.spec
echo     a.binaries, >> DeploymentAnalyzer_ultimate.spec
echo     a.datas, >> DeploymentAnalyzer_ultimate.spec
echo     strip=False, >> DeploymentAnalyzer_ultimate.spec
echo     upx=True, >> DeploymentAnalyzer_ultimate.spec
echo     upx_exclude=[], >> DeploymentAnalyzer_ultimate.spec
echo     name='DeploymentAnalyzer', >> DeploymentAnalyzer_ultimate.spec
echo ) >> DeploymentAnalyzer_ultimate.spec

echo Spec file generated >> %LOG_FILE%

:: Run PyInstaller with the spec file
echo.
echo Running PyInstaller with custom spec file...
pyinstaller --workpath="%WORK_PATH%" --distpath="%DIST_PATH%" --noconfirm DeploymentAnalyzer_ultimate.spec >> %LOG_FILE% 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller failed! Check build_log.txt for details.
    echo PyInstaller failed with code %ERRORLEVEL% >> %LOG_FILE%
    exit /b 1
)

echo PyInstaller completed successfully >> %LOG_FILE%

:: Copy distribution to the project directory
echo.
echo Copying distribution to project directory...
if exist dist\DeploymentAnalyzer rmdir /s /q dist\DeploymentAnalyzer
mkdir dist 2>nul
xcopy /E /I /Y "%DIST_PATH%\DeploymentAnalyzer" "dist\DeploymentAnalyzer" >> %LOG_FILE% 2>&1

echo Distribution copied >> %LOG_FILE%

:: Manually copy critical DLLs
echo.
echo Manually copying critical DLLs and dependencies...
mkdir "dist\DeploymentAnalyzer\support" 2>nul
mkdir "dist\DeploymentAnalyzer\support\data" 2>nul
mkdir "dist\DeploymentAnalyzer\support\logs" 2>nul
mkdir "dist\DeploymentAnalyzer\support\output" 2>nul

echo Copying Python DLLs from: %PYTHON_PREFIX%
copy "%PYTHON_PREFIX%\python*.dll" "dist\DeploymentAnalyzer\" >> %LOG_FILE% 2>&1
copy "%PYTHON_PREFIX%\DLLs\*.dll" "dist\DeploymentAnalyzer\" >> %LOG_FILE% 2>&1

echo Copying VC Runtime files
copy "%WINDIR%\System32\msvcp140.dll" "dist\DeploymentAnalyzer\" >> %LOG_FILE% 2>&1
copy "%WINDIR%\System32\vcruntime140.dll" "dist\DeploymentAnalyzer\" >> %LOG_FILE% 2>&1
copy "%WINDIR%\System32\vcruntime140_1.dll" "dist\DeploymentAnalyzer\" >> %LOG_FILE% 2>&1

echo Manual copies completed >> %LOG_FILE%

:: Create configuration file
echo.
echo Creating configuration file and launchers...
echo [Paths] > "dist\DeploymentAnalyzer\app_config.ini"
echo DataDir=support\data >> "dist\DeploymentAnalyzer\app_config.ini"
echo LogsDir=support\logs >> "dist\DeploymentAnalyzer\app_config.ini"
echo OutputDir=support\output >> "dist\DeploymentAnalyzer\app_config.ini"
echo InternalDir=. >> "dist\DeploymentAnalyzer\app_config.ini"
echo. >> "dist\DeploymentAnalyzer\app_config.ini"
echo [Options] >> "dist\DeploymentAnalyzer\app_config.ini"
echo DefaultGUIMode=True >> "dist\DeploymentAnalyzer\app_config.ini"

:: Create batch launcher
echo @echo off > "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo echo Starting Deployment Analyzer... >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo echo Log will be created in support\logs directory >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo REM Launch with output redirection >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo start /wait cmd /c "%%~dp0DeploymentAnalyzer.exe --gui > %%~dp0support\logs\app.log 2>&1" >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo if ERRORLEVEL 1 ( >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     echo Application terminated with an error. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     echo Check %%~dp0support\logs\app.log for details. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     type %%~dp0support\logs\app.log >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     echo. >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo     pause >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"
echo ) >> "dist\DeploymentAnalyzer\Deployment Analyzer.bat"

:: Create verbose debug batch file
echo @echo off > "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo ====================================================== >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo DEPLOYMENT ANALYZER - VERBOSE DEBUG MODE >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo ====================================================== >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Running at: %%date%% %%time%% >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Current directory: %%CD%% >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Creating required directories if they don't exist... >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo if not exist "%%~dp0support\logs" mkdir "%%~dp0support\logs" >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo if not exist "%%~dp0support\data" mkdir "%%~dp0support\data" >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo if not exist "%%~dp0support\output" mkdir "%%~dp0support\output" >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo System environment: >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo OS: %%OS%% >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo PROCESSOR_ARCHITECTURE: %%PROCESSOR_ARCHITECTURE%% >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Directory contents: >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo dir >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Available DLLs: >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo dir *.dll >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Starting DeploymentAnalyzer in debug mode... >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo All output will appear below: >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo ====================================================== >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo DeploymentAnalyzer.exe --gui >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo ====================================================== >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo Application exited with error level: %%ERRORLEVEL%% >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo echo. >> "dist\DeploymentAnalyzer\debug_launcher.bat"
echo pause >> "dist\DeploymentAnalyzer\debug_launcher.bat"

echo Configuration and launchers created >> %LOG_FILE%

:: Create a README file
echo ============================================= > "dist\DeploymentAnalyzer\README.txt"
echo Deployment Analyzer - Debug Version >> "dist\DeploymentAnalyzer\README.txt"
echo ============================================= >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo TROUBLESHOOTING GUIDE: >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo If you're having trouble running the application: >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo 1. Run debug_launcher.bat to see detailed error messages >> "dist\DeploymentAnalyzer\README.txt"
echo 2. Check the support\logs directory for log files >> "dist\DeploymentAnalyzer\README.txt"
echo 3. Make sure all required directories exist: >> "dist\DeploymentAnalyzer\README.txt"
echo    - support\data >> "dist\DeploymentAnalyzer\README.txt"
echo    - support\logs >> "dist\DeploymentAnalyzer\README.txt"
echo    - support\output >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo 4. If you see "Missing DLL" errors: >> "dist\DeploymentAnalyzer\README.txt"
echo    - Install Microsoft Visual C++ Redistributable 2019 (or later) >> "dist\DeploymentAnalyzer\README.txt"
echo    - Available at: https://aka.ms/vs/17/release/vc_redist.x64.exe >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo 5. To start the application in normal mode: >> "dist\DeploymentAnalyzer\README.txt"
echo    - Double-click "Deployment Analyzer.bat" >> "dist\DeploymentAnalyzer\README.txt"
echo. >> "dist\DeploymentAnalyzer\README.txt"
echo Technical Support: >> "dist\DeploymentAnalyzer\README.txt"
echo If you continue to have issues, please contact technical support >> "dist\DeploymentAnalyzer\README.txt"
echo with the contents of the logs directory. >> "dist\DeploymentAnalyzer\README.txt"

echo README created >> %LOG_FILE%

:: Create a simple launcher for verification
echo @echo off > "dist\DeploymentAnalyzer\verify.bat"
echo echo Simple verification test... >> "dist\DeploymentAnalyzer\verify.bat"
echo cd /d "%%~dp0" >> "dist\DeploymentAnalyzer\verify.bat"
echo echo Current directory: %%CD%% >> "dist\DeploymentAnalyzer\verify.bat"
echo echo. >> "dist\DeploymentAnalyzer\verify.bat"
echo echo Available Python DLLs: >> "dist\DeploymentAnalyzer\verify.bat"
echo dir python*.dll >> "dist\DeploymentAnalyzer\verify.bat"
echo echo. >> "dist\DeploymentAnalyzer\verify.bat"
echo echo Available VC Runtime DLLs: >> "dist\DeploymentAnalyzer\verify.bat"
echo dir msvcp*.dll vcruntime*.dll >> "dist\DeploymentAnalyzer\verify.bat"
echo echo. >> "dist\DeploymentAnalyzer\verify.bat"
echo echo Testing DeploymentAnalyzer.exe... >> "dist\DeploymentAnalyzer\verify.bat"
echo DeploymentAnalyzer.exe --help >> "dist\DeploymentAnalyzer\verify.bat"
echo echo. >> "dist\DeploymentAnalyzer\verify.bat"
echo if ERRORLEVEL 1 ( >> "dist\DeploymentAnalyzer\verify.bat"
echo     echo Verification FAILED with error code %%ERRORLEVEL%% >> "dist\DeploymentAnalyzer\verify.bat"
echo ) else ( >> "dist\DeploymentAnalyzer\verify.bat"
echo     echo Verification SUCCESSFUL >> "dist\DeploymentAnalyzer\verify.bat"
echo ) >> "dist\DeploymentAnalyzer\verify.bat"
echo echo. >> "dist\DeploymentAnalyzer\verify.bat"
echo pause >> "dist\DeploymentAnalyzer\verify.bat"

echo Verification script created >> %LOG_FILE%

:: Run verification test
echo.
echo Running verification test...
cd /d "%CD%\dist\DeploymentAnalyzer"
call verify.bat > verify_results.txt 2>&1
cd /d "%CD%"

copy "dist\DeploymentAnalyzer\verify_results.txt" "verify_results.txt" > nul

:: Summarize
echo.
echo ===============================================
echo BUILD SUMMARY
echo ===============================================
echo Build log: %LOG_FILE%
echo Verification results: verify_results.txt
echo.
echo Distribution directory: dist\DeploymentAnalyzer
echo.
echo TO TEST THE APPLICATION:
echo 1. Navigate to dist\DeploymentAnalyzer
echo 2. Run debug_launcher.bat to see detailed output
echo 3. Check verify_results.txt for initial test results
echo.
echo Complete! Press any key to exit...
pause > nul 