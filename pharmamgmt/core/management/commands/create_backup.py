from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import shutil
from datetime import datetime

class Command(BaseCommand):
    help = 'Create database backup'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup SQLite
        source = 'db.sqlite3'
        destination = os.path.join(backup_dir, f'backup_{timestamp}.sqlite3')
        shutil.copy2(source, destination)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Backup created: {destination}'))
        return destination
