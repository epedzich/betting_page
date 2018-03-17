from django.core.management import BaseCommand

from events.models import Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        Event.update_status()
