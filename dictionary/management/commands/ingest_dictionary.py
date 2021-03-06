from .xml_handler import main
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Ingests tRR_v4.xml'

    def add_arguments(self, parser):
        parser.add_argument('--directory',
                            action='store_true',
                            default='../django-xml',
                            help='path to XML')

    def handle(self, *args, **options):
        d = os.getenv("SOURCE_XML_PATH")
        print(d)
        main(d)

        self.stdout.write(self.style.SUCCESS('Done!'))



