@echo off
cls
echo ========================================
echo PHARMA MANAGEMENT TESTING SUITE
echo ========================================
echo.
echo Select Test:
echo.
echo 1. Quick Test (1,000 records each)
echo 2. Full Test (25,000 records each)
echo 3. Clean Test Data
echo 4. Exit
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running Quick Test...
    python test_complete.py quick
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running Full Test...
    echo This will take 15-30 minutes
    echo.
    python test_complete.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Cleaning test data...
    python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings'); django.setup(); from core.models import *; InvoiceMaster.objects.filter(invoice_no__startswith='TPI').delete(); SalesInvoiceMaster.objects.filter(sales_invoice_no__startswith='TSI').delete(); SupplierMaster.objects.filter(supplier_name__startswith='TestSupplier').delete(); CustomerMaster.objects.filter(customer_name__startswith='TestCustomer').delete(); ProductMaster.objects.filter(product_name__startswith='TestProduct').delete(); print('Test data cleaned!')"
    goto end
)

if "%choice%"=="4" (
    exit
)

:end
echo.
echo ========================================
echo Test Complete!
echo ========================================
pause
