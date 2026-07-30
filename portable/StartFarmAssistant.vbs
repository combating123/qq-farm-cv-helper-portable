Option Explicit

Dim shell, fso, appDir, launcherPath, commandLine
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

If WScript.Arguments.Count > 0 Then
    If LCase(WScript.Arguments.Item(0)) = "--check" Then
        WScript.Echo "one-click launcher parsed"
        WScript.Quit 0
    End If
End If

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcherPath = appDir & "\launcher.ps1"

If Not fso.FileExists(launcherPath) Then
    MsgBox "Launcher not found:" & vbCrLf & launcherPath & vbCrLf & vbCrLf & _
        "Please keep StartFarmAssistant.vbs and launcher.ps1 in the same folder.", _
        16, "QQFarm Assistant"
    WScript.Quit 1
End If

commandLine = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & launcherPath & """"
shell.Run commandLine, 0, False
shell.Popup "Launch request sent. If the assistant window is not visible after about 20 seconds, check:" & _
    vbCrLf & appDir & "\logs\watchdog.log", _
    4, "QQFarm Assistant", 64
