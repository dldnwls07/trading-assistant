
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get current path (Safe encoding free)
CurrentPath = FSO.GetParentFolderName(WScript.ScriptFullName)

' Use ASCII name to prevent encoding errors
BatPath = CurrentPath & "\run.bat"

' Execute with hidden window (0)
WshShell.Run chr(34) & BatPath & chr(34), 0
Set WshShell = Nothing
