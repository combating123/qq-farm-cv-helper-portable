Option Explicit

Dim shell, fso, appDir, launcherPath, commandLine
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

If WScript.Arguments.Count > 0 Then
    If LCase(WScript.Arguments.Item(0)) = "--check" Then
        WScript.Echo "start-repair launcher parsed"
        WScript.Quit 0
    End If
End If

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcherPath = appDir & "\launcher.ps1"

If Not fso.FileExists(launcherPath) Then
    MsgBox "Launcher not found:" & vbCrLf & launcherPath & vbCrLf & vbCrLf & _
        "Please keep RepairFarmAssistant.vbs and launcher.ps1 in the same folder.", _
        16, "QQFarm Assistant"
    WScript.Quit 1
End If

' This is the explicit repair route for an existing window whose Start button
' reports "task started" but does not enter a running cycle.  -Restart closes
' only QQFarmCVHelper and keeps all portable E: user data untouched.
commandLine = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & launcherPath & """ -Restart"
shell.Run commandLine, 0, False
shell.Popup "Restarting the assistant to repair an unresponsive Start button." & _
    vbCrLf & "Your settings and E: user data are kept." & _
    vbCrLf & "Wait for the new assistant window, then click Start once.", _
    6, "QQFarm Assistant", 64
