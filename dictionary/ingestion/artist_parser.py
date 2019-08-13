from django.core.exceptions import ObjectDoesNotExist
from typing import Tuple, Dict

from dictionary.models import ArtistParsed, Artist, ArtistRelations
from dictionary.utils import slugify


class ArtistParser:

    @staticmethod
    def parse(d: Dict) -> ArtistParsed:
        try:
            name = d["name"]
            nt = ArtistParsed(
                name=name,
                slug=slugify(name),
                xml_dict=d
            )
        except Exception as e:
            raise KeyError(f"Sense parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: ArtistParsed) -> Artist:
        try:
            artist = Artist.objects.get(slug=nt.slug)
            artist.name = nt.name
            artist.save()
        except ObjectDoesNotExist:
            artist = Artist.objects.create(slug=nt.slug, name=nt.name)
        return artist

    @staticmethod
    def update_relations(artist: Artist, nt: ArtistParsed) -> Tuple[Artist, ArtistRelations]:
        pass

    @staticmethod
    def purge_relations(artist: Artist) -> Artist:
        return artist

    @staticmethod
    def extract_origin(nt: ArtistParsed):
        pass
