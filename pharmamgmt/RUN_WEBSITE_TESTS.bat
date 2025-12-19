@echo off
cls
echo ========================================
echo WEBSITE PERFORMANCE TESTING
echo ========================================
echo.
echo This will test:
echo - Page Load Speed
echo - Database Query Performance
echo - Data Scalability
echo - Concurrent User Load
echo - Overall Reliability
echo.
echo ========================================
echo.
echo Make sure server is running!
echo Press Ctrl+C to cancel
echo.
pause

echo.
echo Starting tests...
echo.

python test_website_performance.py

echo.
echo ========================================
echo Testing Complete!
echo ========================================
pause
