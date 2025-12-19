@echo off
echo ========================================
echo    BULK DATA DELETION UTILITY
echo ========================================
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Choose deletion option:
echo 1. Delete bulk test data (recommended)
echo 2. Delete ALL data (⚠️  DANGEROUS)
echo 3. Cancel
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🗑️  Deleting bulk test data...
    echo.
    python delete_bulk_entries.py
    echo.
    echo ✅ Bulk deletion completed!
) else if "%choice%"=="2" (
    echo.
    echo ⚠️  WARNING: This will delete ALL data!
    echo.
    python delete_bulk_entries.py --all
    echo.
    echo ✅ Complete deletion finished!
) else if "%choice%"=="3" (
    echo.
    echo ❌ Operation cancelled.
) else (
    echo.
    echo ❌ Invalid choice. Please run again.
)

echo.
echo Press any key to exit...
pause >nul