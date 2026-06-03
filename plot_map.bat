@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\plot_route.py --open %*
