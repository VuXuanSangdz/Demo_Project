@echo off
setlocal
cd /d "%~dp0"
echo === Demo Project: Smart Delivery Routing ===
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt
echo.
echo [OK] Cai dat xong. Tiep theo (PowerShell dung .\ truoc ten file):
echo   .venv\Scripts\python.exe scripts\download_graph.py
echo   .venv\Scripts\python.exe scripts\train_clusters.py
echo   .\run.bat
echo.
echo Hoac chay 1 lenh: .\install.ps1
pause
