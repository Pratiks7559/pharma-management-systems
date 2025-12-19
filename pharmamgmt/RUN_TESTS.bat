@echo off
cls
echo ========================================
echo PHARMA MANAGEMENT - 6 SECTION TEST
echo ========================================
echo.
echo Sections to Test:
echo 1. Purchases
echo 2. Sales
echo 3. Purchase Returns
echo 4. Sales Returns
echo 5. Supplier Challans
echo 6. Customer Challans
echo.
echo ========================================
echo.
echo Select Test Type:
echo.
echo 1. Quick Test (1,000 records each = 6,000 total)
echo 2. Full Test (25,000 records each = 150,000 total)
echo 3. Clean Test Data
echo 4. Exit
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo ========================================
    echo Running Quick Test...
    echo Expected Time: 2-5 minutes
    echo ========================================
    python test_6_sections.py quick
    goto end
)

if "%choice%"=="2" (
    echo.
    echo ========================================
    echo Running Full Test...
    echo Expected Time: 20-40 minutes
    echo ========================================
    echo.
    set /p confirm="This will create 150,000 records. Continue? (Y/N): "
    if /i "%confirm%"=="Y" (
        python test_6_sections.py
    ) else (
        echo Test cancelled.
    )
    goto end
)

if "%choice%"=="3" (
    echo.
    echo ========================================
    echo Cleaning Test Data...
    echo ========================================
    python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings'); django.setup(); from core.models import *; print('Deleting test data...'); InvoiceMaster.objects.filter(invoice_no__startswith='TPI').delete(); SalesInvoiceMaster.objects.filter(sales_invoice_no__startswith='TSI').delete(); ReturnInvoiceMaster.objects.filter(returninvoiceid__startswith='TPR').delete(); ReturnSalesInvoiceMaster.objects.filter(return_sales_invoice_no__startswith='TSR').delete(); Challan1.objects.filter(challan_no__startswith='TSC').delete(); CustomerChallan.objects.filter(customer_challan_no__startswith='TCC').delete(); SupplierMaster.objects.filter(supplier_name__startswith='TestSupp').delete(); CustomerMaster.objects.filter(customer_name__startswith='TestCust').delete(); ProductMaster.objects.filter(product_name__startswith='TestProd').delete(); print('✓ Test data cleaned!')"
    goto end
)

if "%choice%"=="4" (
    exit
)

echo Invalid choice!

:end
echo.
echo ========================================
echo Done!
echo ========================================
pause
