@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 not found. Please install Python 3.10 or newer.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe python -m venv .venv
.venv\Scripts\python.exe -m pip install --quiet -e .
start http://127.0.0.1:8765
.venv\Scripts\python.exe main.py serve
