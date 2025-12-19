@echo off
echo ========================================
echo Complete Pharmacy System Load Test
echo ========================================
echo.
echo This will test ALL routes:
echo - Dashboard
echo - Products and Inventory
echo - Suppliers and Customers
echo - Purchase and Sales Invoices
echo - Challans and Returns
echo - Reports and Ledgers
echo - Payments and Receipts
echo - Stock Issues and Contra
echo - User Management and Backups
echo.
echo ========================================
echo.

venv\Scripts\python.exe -m pip install locust >nul 2>&1

echo Starting Locust...
echo Open browser: http://localhost:8089
echo.
echo Recommended Settings:
echo - Host: http://127.0.0.1:8000
echo - Users: 100-200
echo - Spawn rate: 10
echo.

venv\Scripts\locust -f complete_locustfile.py
