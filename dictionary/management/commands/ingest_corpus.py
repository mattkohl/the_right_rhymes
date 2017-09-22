from .corpus_handler import main
from django.core.management.base import BaseCommand
import django.conf.global_settings as settings


class Command(BaseCommand):
    help = 'Ingests HH.db'

    def add_arguments(self, parser):
        parser.add_argument('--directory',
                            action='store_true',
                            default='../corpus/dbs/HH.db',
                            help='path to sqlite3 db')

    def handle(self, *args, **options):
        if 'directory' in options:
            d = options['directory']
        else:
            d = settings.SOURCE_CORPUS_PATH

        main(d)

        self.stdout.write(self.style.SUCCESS('Done!'))