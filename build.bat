@echo off
echo Building DeploymentAnalyzer...

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
    --add-data "data;data" ^
    --add-data "logs;logs" ^
    --add-data "output;output" ^
    --add-data "deployment-analyse.py;." ^
    --name "DeploymentAnalyzer" ^
    standalone.py

if %ERRORLEVEL% NEQ 0 (
    echo Build failed with error code %ERRORLEVEL%
) else (
    echo Build completed successfully!
    echo Executable is located at: %DIST_PATH%\DeploymentAnalyzer\DeploymentAnalyzer.exe
    
    echo Copying executable to project directory...
    mkdir dist 2>nul
    xcopy /E /I /Y "%DIST_PATH%\DeploymentAnalyzer" "dist\DeploymentAnalyzer"
)

echo Done.
pause 