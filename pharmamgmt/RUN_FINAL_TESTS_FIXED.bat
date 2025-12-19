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
    python test_existing_data.py quick
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
        echo.
        echo Starting full test...
        python test_existing_data.py
        goto end
    )
    
    if /i "%confirm%"=="N" (
        goto cancelled
    )
    
    echo Invalid input! Please enter Y or N.
    goto end
)

if "%choice%"=="3" (
    echo.
    echo ========================================
    echo Cleaning Test Data...
    echo ========================================
    set /p cleanconfirm="Delete all test records? (Y/N): "
    
    if /i "%cleanconfirm%"=="Y" (
        python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings'); django.setup(); from core.models import *; InvoiceMaster.objects.filter(invoice_no__startswith='TPI').delete(); SalesInvoiceMaster.objects.filter(sales_invoice_no__startswith='TSI').delete(); ReturnInvoiceMaster.objects.filter(returninvoiceid__startswith='TPR').delete(); ReturnSalesInvoiceMaster.objects.filter(return_sales_invoice_no__startswith='TSR').delete(); print('✓ Test data cleaned!')"
        goto end
    )
    
    echo Cleanup cancelled.
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Exiting...
    exit /b 0
)

echo.
echo ========================================
echo Invalid choice! Please select 1-4.
echo ========================================
goto end

:cancelled
echo.
echo ========================================
echo Test cancelled.
echo ========================================
goto end

:end
echo.
echo ========================================
echo Done!
echo ========================================
pause
