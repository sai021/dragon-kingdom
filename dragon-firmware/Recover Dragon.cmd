@echo off
title Dragon Kingdom - USB recovery
cd /d "%~dp0"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\recovery_gui.py
) else (
  python tools\recovery_gui.py
)
if errorlevel 1 pause
