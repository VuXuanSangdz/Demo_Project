@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo Chua cai dat. Chay setup.bat truoc.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python main.py
