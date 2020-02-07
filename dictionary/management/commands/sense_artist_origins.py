from django.core.management.base import BaseCommand

from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.models import Sense
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
                response = requests.get(f"{url}/{artist.slug}").json()
                done = [ArtistParser.persist(ArtistParser.parse(d)) for d in response["artists"]]
                cache[artist.slug] = done
            self.stdout.write(self.style.SUCCESS('Done!'))



