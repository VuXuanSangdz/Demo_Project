@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Chua cai dat. Double-click CAI_DAT.bat truoc.
  pause
  exit /b 1
)
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe main.py
