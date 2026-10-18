@echo off
title Dragon Kingdom - automatic S3 / C3 flasher
cd /d "%~dp0"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\batch_flash.py
  if errorlevel 1 pause
  exit /b
)
python tools\batch_flash.py
if errorlevel 1 pause
