@echo off
echo Fixing DeploymentAnalyzer.exe file...

cd dist\DeploymentAnalyzer-Final

echo @echo off > DeploymentAnalyzer.exe
echo cscript //nologo "%%~dp0DeploymentAnalyzer.vbs" >> DeploymentAnalyzer.exe
echo exit >> DeploymentAnalyzer.exe

echo Done!
cd ..\..
pause 