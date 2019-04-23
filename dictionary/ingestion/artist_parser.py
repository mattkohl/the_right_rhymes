from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import ArtistParsed, Artist
from dictionary.utils import slugify


class ArtistParser:

    @staticmethod
    def parse(name: str) -> ArtistParsed:
        return ArtistParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: ArtistParsed) -> Artist:
        try:
            artist = Artist.objects.get(slug=nt.slug)
        except ObjectDoesNotExist:
            artist = Artist(slug=nt.slug, name=nt.name)
            artist.save()
            return artist
        else:
            artist.name = nt.name
            artist.save()
            return artist
