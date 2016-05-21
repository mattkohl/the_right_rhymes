from ._xml_handler import main
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Ingests tRR_v4.xml'

    def add_arguments(self, parser):
        parser.add_argument('--directory',
            action='store_true',
            default='../tRR/XML/tRR_Django',
            help='path to XML')

    def handle(self, *args, **options):
        if 'directory' in options:
            d = options['directory']
        else:
            d = '../tRR/XML/tRR_Django'

        main(d)

        self.stdout.write(self.style.SUCCESS('Done!'))



