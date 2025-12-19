@echo off
echo Starting Production Server...
echo.
echo Configuration:
echo - Threads: 8 (handles 8 concurrent requests)
echo - Channel timeout: 120 seconds
echo.
venv\Scripts\python.exe -m pip install waitress >nul 2>&1
venv\Scripts\waitress-serve --threads=8 --channel-timeout=120 --host=127.0.0.1 --port=8000 pharmamgmt.wsgi:application
