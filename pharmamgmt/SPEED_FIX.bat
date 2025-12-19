@echo off
echo ========================================
echo Speed Optimization Script
echo ========================================
echo.

echo Step 1: Adding database indexes...
python optimize_database.py
echo.

echo Step 2: Clearing cache...
python manage.py clear_cache 2>nul
echo.

echo ========================================
echo Optimization Complete!
echo Now restart your server with:
echo python manage.py runserver
echo ========================================
pause
