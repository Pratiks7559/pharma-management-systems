========================================
PHARMA MANAGEMENT - TESTING GUIDE
========================================

6 SECTIONS TESTED:
------------------
1. Purchases          - Purchase invoices
2. Sales              - Sales invoices
3. Purchase Returns   - Return to suppliers
4. Sales Returns      - Return from customers
5. Supplier Challans  - Supplier delivery notes
6. Customer Challans  - Customer delivery notes

FILES:
------
test_6_sections.py - Main test script
RUN_TESTS.bat      - Easy test runner

HOW TO RUN:
-----------

METHOD 1 (Easiest):
-------------------
Double-click: RUN_TESTS.bat
Select:
  1 = Quick Test (1,000 each = 6,000 total)
  2 = Full Test (25,000 each = 150,000 total)
  3 = Clean test data
  4 = Exit

METHOD 2 (Command Line):
------------------------
Quick Test:  python test_6_sections.py quick
Full Test:   python test_6_sections.py

EXPECTED TIME:
--------------
Quick Test: 2-5 minutes (6,000 records)
Full Test:  20-40 minutes (150,000 records)

WHAT HAPPENS:
-------------
1. Creates base data (50 suppliers, 100 customers, 200 products)
2. Tests each section with specified record count
3. Shows progress every 1,000 records
4. Displays summary with timing

TEST DATA PREFIX:
-----------------
All test data has "T" prefix:
- Invoices: TPI, TSI, TPR, TSR, TSC, TCC
- Names: TestSupp_, TestCust_, TestProd_

CLEAN TEST DATA:
----------------
Option 3 in RUN_TESTS.bat
Or manually delete records starting with "T"

NOTES:
------
✓ Real data is NOT affected
✓ Tests can be run multiple times
✓ Use Quick Test first to verify
✓ Full Test creates 150,000 records
✓ Requires PostgreSQL for best performance

TROUBLESHOOTING:
----------------
If error occurs:
1. Check database connection
2. Ensure PostgreSQL is running
3. Run: python optimize_database.py
4. Try Quick Test first

========================================
