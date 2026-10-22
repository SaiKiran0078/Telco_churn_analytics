@echo off
rem Sets the Power BI RepoRoot to this clone. Use "init.cmd reset" to restore the placeholder before committing.
if /I "%1"=="reset" (powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0init.ps1" -Reset) else (powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0init.ps1")
