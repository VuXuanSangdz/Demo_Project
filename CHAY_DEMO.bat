@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo Chua cai dat. Dang chay CAI_DAT.bat...
  call "%~dp0CAI_DAT.bat"
  if errorlevel 1 exit /b 1
)

if not exist data\graph\*.pkl (
  echo Chua co ban do OSM. Dang tai...
  set PYTHONIOENCODING=utf-8
  .venv\Scripts\python.exe scripts\download_graph.py
  .venv\Scripts\python.exe scripts\train_clusters.py
)

set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe main.py
pause
