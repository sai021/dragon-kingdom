@echo off
title Dragon Kingdom - signed production recovery
cd /d "%~dp0"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\recovery_gui.py
  if errorlevel 1 pause
  exit /b
)
python tools\recovery_gui.py
if errorlevel 1 pause
