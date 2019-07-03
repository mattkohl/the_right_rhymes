from collections import OrderedDict
from typing import Dict, List, Iterator, Tuple

from django.core.exceptions import ObjectDoesNotExist

from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.ingestion.song_parser import SongParser
from dictionary.ingestion.xref_parser import XrefParser
from dictionary.management.commands.xml_handler import clean_up_date
from dictionary.models import ExampleParsed, Example, Song, ExampleRelations, SongParsed, Artist, ArtistParsed, \
    SongRelations, Xref, XrefRelations
from dictionary.utils import slugify


class ExampleParser:

    @staticmethod
    def parse(d: Dict) -> ExampleParsed:
        try:
            primary_artists = [d['artist']['#text'] if isinstance(d['artist'], OrderedDict) else d['artist']]
            from pprint import pprint
            nt = ExampleParsed(
                primary_artists=primary_artists,
                song_title=d['songTitle'],
                featured_artists=d['feat'] if 'feat' in d else [],
                release_date=clean_up_date(d['date']),
                release_date_string=d['date'],
                album=d['album'],
                lyric_text=d['lyric']['text'],
                xml_id=d["@id"],
                rhymes=d["rhyme"] if "rhyme" in d else [],
                rfs=d["rf"] if "rf" in d else [],
                xrefs=d["xref"] if "xref" in d else [],
                entities=d["entity"] if "entity" in d else []
            )
        except Exception as e:
            raise KeyError(f"Example parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: ExampleParsed) -> Tuple[Example, ExampleRelations]:
        artist_name = nt.primary_artists[0]
        artist_slug = slugify(artist_name)
        try:
            example = Example.objects.get(song_title=nt.song_title,
                                          artist_name=artist_name,
                                          artist_slug=artist_slug,
                                          release_date=nt.release_date,
                                          release_date_string=nt.release_date_string,
                                          album=nt.album,
                                          lyric_text=nt.lyric_text)

        except ObjectDoesNotExist:
            example = Example.objects.create(song_title=nt.song_title,
                                             artist_name=artist_name,
                                             artist_slug=artist_slug,
                                             release_date=nt.release_date,
                                             release_date_string=nt.release_date_string,
                                             album=nt.album,
                                             lyric_text=nt.lyric_text)
        return ExampleParser.update_relations(example, nt)

    @staticmethod
    def update_relations(example: Example, nt: ExampleParsed) -> Tuple[Example, ExampleRelations]:
        purged = ExampleParser.purge_relations(example)
        primary_artists = ExampleParser.process_primary_artists(nt, purged)
        featured_artists = ExampleParser.process_featured_artists(nt, purged)
        relations = ExampleRelations(
            artist=primary_artists,
            from_song=ExampleParser.process_songs(nt, example, primary_artists, featured_artists),
            feat_artist=featured_artists,
            example_rhymes=ExampleParser.extract_rhymes(nt),
            illustrates_senses=[],
            features_entities=ExampleParser.extract_entities(nt),
            lyric_links=[]
        )
        return purged, relations

    @staticmethod
    def purge_relations(example: Example) -> Example:
        example.artist.clear()
        example.from_song.clear()
        example.feat_artist.clear(),
        example.example_rhymes.clear(),
        example.illustrates_senses.clear(),
        example.features_entities.clear(),
        example.lyric_links.clear()
        return example

    @staticmethod
    def extract_songs(nt: ExampleParsed) -> Iterator[SongParsed]:
        yield SongParser.parse(nt)

    @staticmethod
    def process_songs(nt: ExampleParsed, example: Example, primary_artists: List[Artist],
                      featured_artists: List[Artist]):
        def process_song(song: Song, relations: SongRelations) -> Tuple[Song, SongRelations]:
            example.from_song.add(song)
            return song, relations

        return [process_song(*SongParser.persist(d, primary_artists, featured_artists)) for d in
                ExampleParser.extract_songs(nt)]

    @staticmethod
    def extract_featured_artists(nt: ExampleParsed) -> List[ArtistParsed]:
        return [ArtistParser.parse(a) for a in nt.featured_artists]

    @staticmethod
    def extract_primary_artists(nt: ExampleParsed) -> List[ArtistParsed]:
        return [ArtistParser.parse(a) for a in nt.primary_artists]

    @staticmethod
    def process_primary_artists(nt: ExampleParsed, example: Example) -> List[Artist]:
        def process_primary_artist(artist: Artist) -> Artist:
            example.artist.add(artist)
            return artist

        return [process_primary_artist(ArtistParser.persist(a)) for a in ExampleParser.extract_primary_artists(nt)]

    @staticmethod
    def process_featured_artists(nt: ExampleParsed, example: Example) -> List[Artist]:
        def process_featured_artist(artist: Artist) -> Artist:
            example.feat_artist.add(artist)
            return artist

        return [process_featured_artist(ArtistParser.persist(a)) for a in ExampleParser.extract_featured_artists(nt)]

    @staticmethod
    def extract_entities(nt: ExampleParsed) -> List:
        return list()

    @staticmethod
    def extract_rhymes(nt: ExampleParsed) -> List:
        return list()

    @staticmethod
    def extract_rf(nt: ExampleParsed) -> List:
        return list()

    @staticmethod
    def extract_xrefs(nt: ExampleParsed) -> List:
        return [XrefParser.parse(a) for a in nt.xrefs]

    @staticmethod
    def process_xrefs(nt: ExampleParsed, example: Example):
        def process_xref(xref: Xref) -> Xref:
            return xref
        return [process_xref(XrefParser.persist(d, example)) for d in ExampleParser.extract_xrefs(nt)]
