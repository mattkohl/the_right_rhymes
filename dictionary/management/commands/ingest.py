from .xml_parser import main
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--directory',
                            action='store_true',
                            default='/Users/mattkohl/django-xml',
                            help='path to XML')

    def handle(self, *args, **options):
        d = options['directory']
        main(d)
        self.stdout.write(self.style.SUCCESS('Done!'))



