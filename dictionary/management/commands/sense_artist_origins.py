from django.core.management.base import BaseCommand
from dictionary.models import Sense, Artist, Place
import requests


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('sense_id', nargs='+', type=str)

    def handle(self, *args, **options):
        url = "https://therightrhymes.com/data/artists"
        for _id in options['sense_id']:
            sense = Sense.objects.filter(xml_id=_id).first()
            artists = sense.cites_artists.all()
            cache = dict()
            for artist in artists:
                cache[artist.slug] = requests.get(f"{url}/{artist.slug}").json()
            from pprint import pprint
            pprint(cache)
            self.stdout.write(self.style.SUCCESS('Done!'))



