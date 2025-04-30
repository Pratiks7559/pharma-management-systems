from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone

class Command(BaseCommand):
    help = 'Clear expired sessions from the database'

    def handle(self, *args, **options):
        """
        Delete expired sessions from the database.
        This command should be run regularly using a cron job or similar.
        """
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared expired sessions')
        )