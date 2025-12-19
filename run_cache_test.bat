@echo off
cd /d "c:\pharmaproject pratk\WebsiteHostingService\WebsiteHostingService\WebsiteHostingService\pharmamgmt"
echo Running cache test...
echo.
python manage.py shell < test_cache_logic.py
echo.
echo Test completed!
pause
