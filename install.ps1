# Cai dat day du: venv + thu vien + tai ban do OSM + train shipper
# Chay trong PowerShell:
#   cd duong_dan_Demo_Project
#   .\install.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Demo Project: Smart Delivery Routing ===" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Loi: chua cai Python. Tai tu https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] Tao virtual environment..." -ForegroundColor Yellow
python -m venv .venv

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $py -m pip install --upgrade pip -q
Write-Host "[2/4] Cai thu vien (osmnx, folium, ...)" -ForegroundColor Yellow
& $py -m pip install -r requirements.txt

Write-Host "[3/4] Tai ban do OSM (Quan Dong Da, Ha Noi)..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
& $py scripts\download_graph.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[4/4] Huấn luyện 5 shipper (K-means + snap OSM)..." -ForegroundColor Yellow
& $py scripts\train_clusters.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== XONG! Chay demo: ===" -ForegroundColor Green
Write-Host "  .\run.bat"
Write-Host "  hoac: .venv\Scripts\python.exe main.py"
Write-Host "  ban do: .\plot_map.bat"
