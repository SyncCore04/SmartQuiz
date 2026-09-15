@echo off
title SmartQuiz Backend Launcher

rem Switch to backend folder relative to this script
cd /d "%~dp0backend"

echo ==================================================
echo    Online Quiz System - Flask Backend Launcher
echo ==================================================
echo.

rem Check python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] python not found in PATH. Please install Python 3.
    echo        Make sure to check "Add python.exe to PATH" during install.
    pause
    exit /b 1
)

rem Check Flask, install if missing
echo [1/3] Checking Flask dependency ...
python -m flask --version >nul 2>nul
if errorlevel 1 (
    echo [INFO] Flask not found, installing ...
    python -m pip install flask
)

echo [2/3] Starting backend service ...
echo        URL: http://127.0.0.1:5000
echo        Press Ctrl+C to stop.
echo.
echo [3/3] Running app ...
python app.py

echo.
echo Backend stopped.
pause