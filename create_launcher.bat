@echo off
echo Creating a shortcut with .exe extension...

echo Retrieving version information...
for /f "tokens=*" %%a in ('python -c "from version import VERSION; print(VERSION)"') do set APP_VERSION=%%a
echo Building version: %APP_VERSION%
set RELEASE_DIR=dist\DeploymentAnalyzer-%APP_VERSION%-Release

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%RELEASE_DIR%\DeploymentAnalyzer.exe.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "wscript.exe" >> CreateShortcut.vbs
echo oLink.Arguments = "//nologo " ^& Chr(34) ^& "%RELEASE_DIR%\DeploymentAnalyzer.vbs" ^& Chr(34) >> CreateShortcut.vbs
echo oLink.Description = "Deployment Analyzer v%APP_VERSION%" >> CreateShortcut.vbs
echo oLink.WindowStyle = 0 >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%RELEASE_DIR%" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,167" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Moving the .lnk file to replace .exe...
ren "%RELEASE_DIR%\DeploymentAnalyzer.exe.lnk" "DeploymentAnalyzer.exe"

echo Launcher created at:
echo %RELEASE_DIR%\DeploymentAnalyzer.exe
echo.
echo Done!
pause 