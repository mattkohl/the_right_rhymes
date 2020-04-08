import os
from .csv_parser import main
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        d = os.getenv("SOURCE_CSV_PATH")
        main(d)
        self.stdout.write(self.style.SUCCESS('Done!'))



