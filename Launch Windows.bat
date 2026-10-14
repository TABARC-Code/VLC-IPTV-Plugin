@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 setup_app.py
    if errorlevel 1 pause
    exit /b
)
python --version >nul 2>nul
if not errorlevel 1 (
    python setup_app.py
    if errorlevel 1 pause
    exit /b
)
echo Python is not ready yet. Install Python 3.10 or newer from python.org.
echo In the installer, keep Tcl/Tk and the Python launcher selected.
echo Then close this window and double-click Launch Windows.bat again.
echo The full guide is in SETUP.md.
start "" "https://www.python.org/downloads/"
pause
