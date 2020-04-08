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
            member_of=ArtistParser.process_memberships(nt, purged),
            also_known_as=ArtistParser.process_aliases(nt, purged)
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

    @staticmethod
    def extract_aliases(nt: ArtistParsed) -> Optional[PlaceParsed]:
        aliases = nt.xml_dict.get("also_known_as")
        return [ArtistParser.parse(alias) for alias in aliases] if aliases is not None else list()

    @staticmethod
    def process_aliases(nt: ArtistParsed, artist: Artist) -> List[ArtistParsed]:
        def process_alias(alias: Artist, artist_relations: ArtistRelations) -> Artist:
            artist.also_known_as.add(alias)
            return alias
        return [process_alias(*ArtistParser.persist(a)) for a in ArtistParser.extract_aliases(nt)]

    @staticmethod
    def extract_membership(nt: ArtistParsed) -> List[ArtistParsed]:
        member_of = nt.xml_dict.get("member_of")
        return [ArtistParser.parse(group) for group in member_of] if member_of is not None else list()

    @staticmethod
    def process_memberships(nt: ArtistParsed, artist: Artist) -> List[ArtistParsed]:
        def process_membership(group: Artist, artist_relations: ArtistRelations) -> Artist:
            artist.member_of.add(group)
            return group
        return [process_membership(*ArtistParser.persist(a)) for a in ArtistParser.extract_membership(nt)]

