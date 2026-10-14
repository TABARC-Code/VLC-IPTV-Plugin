#!/bin/sh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Install Python 3 and Tkinter using your distribution package manager. See SETUP.md.'
    exit 1
fi
exec python3 setup_app.py
