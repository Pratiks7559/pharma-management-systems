#!/usr/bin/env python3
"""
Setup PostgreSQL Database
Migrate from SQLite to PostgreSQL for 600K records
"""

import os
import django
from django.core.management import execute_from_command_line
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')

def setup_postgresql():
    """Setup PostgreSQL database and run migrations"""
    
    print("Setting up PostgreSQL database...")
    
    try:
        # Test PostgreSQL connection
        django.setup()
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"PostgreSQL connected: {version}")
        
        # Run migrations
        print("\nRunning database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create superuser if needed
        print("\nCreating superuser (if needed)...")
        try:
            execute_from_command_line(['manage.py', 'createsuperuser', '--noinput', '--username=admin', '--email=admin@pharmacy.com'])
        except:
            print("Superuser already exists or creation skipped")
        
        # Collect static files
        print("\nCollecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("\n✅ PostgreSQL setup completed!")
        print("📊 Database ready for 600K records")
        print("🚀 All new data will be stored in PostgreSQL")
        
    except Exception as e:
        print(f"❌ PostgreSQL setup error: {e}")
        print("\n🔧 Please ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database 'pharma_db' exists")
        print("3. User 'postgres' has access")
        print("4. psycopg2 is installed: pip install psycopg2-binary")

if __name__ == "__main__":
    setup_postgresql()