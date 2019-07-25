from .salience_builder import main
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Updates Saliences'

    def handle(self, *args, **options):
        main()

        self.stdout.write(self.style.SUCCESS('Done!'))



