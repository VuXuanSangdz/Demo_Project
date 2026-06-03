@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   CAI DAT DAY DU - Demo Project
echo   (venv + osmnx + ban do OSM + shipper)
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [LOI] Chua cai Python. Tai tu https://www.python.org/downloads/
  pause
  exit /b 1
)

echo [1/4] Tao virtual environment...
python -m venv .venv

echo [2/4] Cai thu vien (osmnx, folium, ...)...
.venv\Scripts\python.exe -m pip install --upgrade pip -q
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo [LOI] Cai thu vien that bai.
  pause
  exit /b 1
)

echo [3/4] Tai ban do OSM (Quan Dong Da, Ha Noi)...
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe scripts\download_graph.py
if errorlevel 1 (
  echo [LOI] Tai ban do that bai. Kiem tra ket noi mang.
  pause
  exit /b 1
)

echo [4/4] Huan luyen 5 shipper...
.venv\Scripts\python.exe scripts\train_clusters.py
if errorlevel 1 (
  echo [LOI] Train clusters that bai.
  pause
  exit /b 1
)

echo.
echo ========================================
echo   XONG! Double-click CHAY_DEMO.bat de chay
echo ========================================
pause
