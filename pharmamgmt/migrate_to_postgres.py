"""
SQLite to PostgreSQL Migration Script
Run this after setting up PostgreSQL database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.core.management import call_command

print("Starting migration from SQLite to PostgreSQL...")
print("\nStep 1: Dumping data from SQLite...")
call_command('dumpdata', '--natural-foreign', '--natural-primary', 
             '--exclude=contenttypes', '--exclude=auth.permission', 
             '--indent=2', output='datadump.json')
print("✓ Data exported to datadump.json")

print("\nNext steps:")
print("1. Update settings.py with PostgreSQL configuration")
print("2. Run: python manage.py migrate")
print("3. Run: python manage.py loaddata datadump.json")
