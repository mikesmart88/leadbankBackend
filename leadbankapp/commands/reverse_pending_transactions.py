from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Reverse pending transactions older than 24 hours"

    def handle(self, *args, **options):
        print("Cron is working!")