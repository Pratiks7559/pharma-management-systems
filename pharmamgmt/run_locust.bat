@echo off
echo Installing Locust...
venv\Scripts\python.exe -m pip install locust >nul 2>&1

echo.
echo Starting Locust Web UI...
echo.
echo Open browser: http://localhost:8089
echo.
echo Configuration:
echo - Host: http://127.0.0.1:8000
echo - Users: Start with 50, then increase
echo - Spawn rate: 10 users/second
echo.

venv\Scripts\locust -f locustfile.py
