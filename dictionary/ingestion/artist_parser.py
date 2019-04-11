from dictionary.models import ArtistParsed, Artist
from dictionary.utils import slugify


class ArtistParser:

    @staticmethod
    def parse(name: str) -> ArtistParsed:
        return ArtistParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: ArtistParsed):
        artist, _ = Artist.objects.get_or_create(slug=nt.slug)
        artist.name = nt.name
        artist.save()
        return artist
