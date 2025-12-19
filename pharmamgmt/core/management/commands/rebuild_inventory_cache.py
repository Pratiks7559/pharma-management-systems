"""
Management command to rebuild inventory cache
Usage: python manage.py rebuild_inventory_cache
"""
from django.core.management.base import BaseCommand
from core.inventory_cache import rebuild_all_cache


class Command(BaseCommand):
    help = 'Rebuild inventory cache for all products'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting inventory cache rebuild...'))
        
        result = rebuild_all_cache()
        
        if result:
            self.stdout.write(self.style.SUCCESS('Cache rebuild completed successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Cache rebuild failed!'))
