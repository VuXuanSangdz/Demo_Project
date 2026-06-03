@echo off
setlocal
cd /d "%~dp0"
echo === Demo Project: Smart Delivery Routing ===
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt
echo.
echo [OK] Cai dat xong. Tiep theo:
echo   python scripts\download_graph.py
echo   python scripts\train_clusters.py
echo   python main.py
pause
