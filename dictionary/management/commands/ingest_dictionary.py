from .xml_handler import main
from django.core.management.base import BaseCommand
import django.conf.global_settings as settings


class Command(BaseCommand):
    help = 'Ingests tRR_v4.xml'

    def add_arguments(self, parser):
        parser.add_argument('--directory',
                            action='store_true',
                            default='../django-xml',
                            help='path to XML')

    def handle(self, *args, **options):
        if 'directory' in options:
            d = options['directory']
        else:
            d = settings.SOURCE_XML_PATH

        main(d)

        self.stdout.write(self.style.SUCCESS('Done!'))



