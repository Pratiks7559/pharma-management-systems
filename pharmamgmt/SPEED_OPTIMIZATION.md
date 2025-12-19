# Website Speed Optimization Guide

## Problem: Website slow with 1 lakh+ entries

## Quick Fixes (Apply These First)

### 1. Add Pagination to All List Views

Add this to settings.py:
```python
# Pagination
ITEMS_PER_PAGE = 50
```

### 2. Add Database Indexes

Run this command:
```bash
python manage.py sqlmigrate core 0001
```

### 3. Use select_related() and prefetch_related()

Example:
```python
# Before (Slow)
products = Product.objects.all()

# After (Fast)
products = Product.objects.select_related('supplier').prefetch_related('inventory_set')[:50]
```

### 4. Add Caching

Already configured in settings.py - just works!

### 5. Limit Dashboard Queries

Only show recent 100 records on dashboard.

## Apply These Changes:

Run these commands in order:
```bash
cd c:\pharmaproject pratk\WebsiteHostingService\WebsiteHostingService\WebsiteHostingService\pharmamgmt
python optimize_database.py
python manage.py migrate
python manage.py runserver
```
