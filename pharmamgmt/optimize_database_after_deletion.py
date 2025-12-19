import os
import django
import sqlite3
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

def optimize_database():
    """Optimize database after bulk deletion"""
    
    print("🔧 Optimizing database after deletion...")
    
    try:
        # Get database path
        db_path = 'db.sqlite3'
        
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("1. Running VACUUM to reclaim space...")
        cursor.execute('VACUUM;')
        
        print("2. Analyzing database statistics...")
        cursor.execute('ANALYZE;')
        
        print("3. Rebuilding indexes...")
        cursor.execute('REINDEX;')
        
        conn.commit()
        conn.close()
        
        print("✅ Database optimization completed!")
        
        # Show database size
        import os
        size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"📊 Database size: {size:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error during optimization: {str(e)}")

if __name__ == "__main__":
    optimize_database()