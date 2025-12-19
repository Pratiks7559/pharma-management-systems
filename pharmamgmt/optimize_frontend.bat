@echo off
echo ========================================
echo Frontend Optimization
echo ========================================
echo.
echo Step 1: Collecting static files...
venv\Scripts\python.exe manage.py collectstatic --noinput

echo.
echo Step 2: Optimization complete!
echo.
echo Benefits:
echo - Static files cached
echo - Faster page loading
echo - Reduced server load
echo.
echo ========================================
echo Now restart server: .\start_server.bat
echo ========================================
pause
