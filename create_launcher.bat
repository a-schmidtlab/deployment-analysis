@echo off
echo Creating a shortcut with .exe extension...

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.exe.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "wscript.exe" >> CreateShortcut.vbs
echo oLink.Arguments = "//nologo " ^& Chr(34) ^& "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.vbs" ^& Chr(34) >> CreateShortcut.vbs
echo oLink.Description = "Deployment Analyzer" >> CreateShortcut.vbs
echo oLink.WindowStyle = 0 >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "dist\DeploymentAnalyzer-Release" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,167" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Moving the .lnk file to replace .exe...
ren "dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.exe.lnk" "DeploymentAnalyzer.exe"

echo Launcher created at:
echo dist\DeploymentAnalyzer-Release\DeploymentAnalyzer.exe
echo.
echo Done!
pause 