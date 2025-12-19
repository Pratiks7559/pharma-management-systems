import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import ProductInventoryCache, BatchInventoryCache

print("⚡ Simple Solution - Skip Cache, Use Direct Calculation")
print("=" * 60)

# Just clear cache - inventory view will work without it
print("🗑️  Clearing cache tables...")
ProductInventoryCache.objects.all().delete()
BatchInventoryCache.objects.all().delete()

print("✅ Done! Now use the OLD inventory view instead.")
print("\nChange urls.py:")
print("  FROM: path('inventory/', inventory_list_cached, name='inventory_list')")
print("  TO:   path('inventory/', views.inventory_list, name='inventory_list')")
print("\nOr just visit inventory page - it will calculate on-the-fly")
