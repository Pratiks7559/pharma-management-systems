@echo off
cls
echo ========================================
echo DELETE BULK TEST DATA
echo ========================================
echo.
echo This will delete ALL test records:
echo   - Test Suppliers
echo   - Test Customers
echo   - TPI-* Purchase Invoices
echo   - TSI-* Sales Invoices
echo   - TPR-* Purchase Returns
echo   - TSR-* Sales Returns
echo   - TSC-* Supplier Challans
echo   - TCC-* Customer Challans
echo.
echo ========================================
echo.
pause

python delete_bulk_test_data.py

echo.
echo ========================================
echo Done!
echo ========================================
pause
