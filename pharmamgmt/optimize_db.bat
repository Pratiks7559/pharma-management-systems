@echo off
echo ========================================
echo Database Optimization
echo ========================================
echo.
echo Adding indexes for faster queries...
echo.

venv\Scripts\python.exe optimize_database.py

echo.
echo ========================================
echo Done! Restart server now
echo ========================================
pause
