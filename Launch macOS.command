#!/bin/sh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Install Python 3.10 or newer from python.org, then run this launcher again.'
    open 'https://www.python.org/downloads/macos/'
    read -r reply
    exit 1
fi
python3 setup_app.py
result=$?
if [ "$result" -ne 0 ]; then
    echo 'See SETUP.md for help. Press Return to close.'
    read -r reply
fi
exit "$result"
