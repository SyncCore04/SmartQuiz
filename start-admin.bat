@echo off
title SmartQuiz Admin Panel

rem Switch to the admin folder relative to this script
cd /d "%~dp0backend\admin"

echo ==================================================
echo    SmartQuiz - Admin Panel Launcher
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

echo [2/3] Starting admin panel ...
echo        URL   : http://127.0.0.1:5001
echo        Login : admin / admin123
echo        Press Ctrl+C to stop.
echo.

echo [3/3] Running admin ...
python admin.py

echo.
echo Admin panel stopped.
pause