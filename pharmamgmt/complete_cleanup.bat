@echo off
echo ========================================
echo    COMPLETE DATABASE CLEANUP
echo ========================================
echo.

cd /d "%~dp0"

echo This will:
echo 1. Delete bulk test data
echo 2. Optimize database
echo 3. Clear cache files
echo 4. Reset auto-increment counters
echo.

set /p confirm="Continue? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo 🗑️  Step 1: Deleting bulk data...
    python delete_bulk_entries.py
    
    echo.
    echo 🔧 Step 2: Optimizing database...
    python optimize_database_after_deletion.py
    
    echo.
    echo 🧹 Step 3: Clearing cache files...
    if exist "django.log" del "django.log"
    if exist "*.pyc" del /s "*.pyc"
    if exist "__pycache__" rmdir /s /q "__pycache__"
    
    echo.
    echo ✅ Complete cleanup finished!
    echo Your website should now load much faster.
    
) else (
    echo.
    echo ❌ Cleanup cancelled.
)

echo.
echo Press any key to exit...
pause >nul