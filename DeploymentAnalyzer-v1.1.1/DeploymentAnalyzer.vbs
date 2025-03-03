Set WshShell = CreateObject("WScript.Shell") 
AppPath = WScript.ScriptFullName 
AppDir = Left(AppPath, InStrRev(AppPath, "\")) 
BatchFile = AppDir & ".app\launcher.bat" 
If CreateObject("Scripting.FileSystemObject").FileExists(BatchFile) Then 
    WshShell.Run Chr(34) & BatchFile & Chr(34), 0, False 
Else 
    MsgBox "Error: Required files not found." & vbCrLf & vbCrLf & _ 
    "The .app folder must exist in the same location as this executable." & vbCrLf & _ 
    "Please refer to the README.txt file for more information.", vbCritical, "Deployment Analyzer" 
End If 
Set WshShell = Nothing 
