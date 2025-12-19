@echo off
echo ========================================
echo Creating 100,000 Test Entries
echo ========================================
echo.
echo This will create:
echo - 25,000 Purchase Invoices
echo - 25,000 Sales Invoices
echo - 15,000 Supplier Challans
echo - 15,000 Customer Challans
echo - 10,000 Purchase Returns
echo - 10,000 Sales Returns
echo.
echo TOTAL: 100,000 entries
echo WARNING: This will take 10-15 minutes!
echo ========================================
echo.
pause

venv\Scripts\python.exe create_test_data.py

echo.
echo ========================================
echo Done! Now test with Locust
echo ========================================
pause
