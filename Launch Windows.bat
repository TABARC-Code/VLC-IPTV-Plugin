@echo off
cd /d "%~dp0"
py -3 iptv.py
if errorlevel 1 pause
