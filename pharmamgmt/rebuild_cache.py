import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.inventory_cache import rebuild_all_cache

print("🔄 Rebuilding inventory cache...")
rebuild_all_cache()
print("✅ Cache rebuild complete!")
