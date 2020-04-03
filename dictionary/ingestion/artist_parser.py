from django.core.exceptions import ObjectDoesNotExist
from typing import Tuple, Dict, Optional, List

from dictionary.ingestion.place_parser import PlaceParser
from dictionary.models import ArtistParsed, Artist, ArtistRelations, Place, PlaceParsed
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
            raise KeyError(f"Artist parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: ArtistParsed) -> Tuple[Artist, ArtistRelations]:
        try:
            artist = Artist.objects.get(slug=nt.slug)
            artist.name = nt.name
            artist.save()
        except ObjectDoesNotExist:
            artist = Artist.objects.create(slug=nt.slug, name=nt.name)
        return ArtistParser.update_relations(artist, nt)

    @staticmethod
    def update_relations(artist: Artist, nt: ArtistParsed) -> Tuple[Artist, ArtistRelations]:
        purged = ArtistParser.purge_relations(artist)
        relations = ArtistRelations(
            origin=ArtistParser.process_origin(nt, purged),
            member_of=list(),
            also_known_as=list()
        )
        return purged, relations

    @staticmethod
    def purge_relations(artist: Artist) -> Artist:
        return artist

    @staticmethod
    def extract_origin(nt: ArtistParsed) -> Optional[PlaceParsed]:
        _origin = nt.xml_dict.get("origin")
        return PlaceParser.parse(_origin) if _origin else None

    @staticmethod
    def process_origin(nt: ArtistParsed, artist: Artist) -> Place:
        origin = ArtistParser.extract_origin(nt)
        if origin:
            persisted = PlaceParser.persist(origin)
            artist.origin.add(persisted)
        return origin

