from collections import OrderedDict
from typing import Dict, List, Iterator

from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.ingestion.song_parser import SongParser
from dictionary.management.commands.xml_handler import clean_up_date
from dictionary.models import ExampleParsed, Example, Song, ExampleRelations, SongParsed, Artist, ArtistParsed
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
                xml_id=d["@id"]
            )
        except Exception as e:
            raise KeyError(f"Example parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: ExampleParsed):
        artist_name = nt.primary_artists[0]
        example, _ = Example.objects.get_or_create(song_title=nt.song_title,
                                                   artist_name=artist_name,
                                                   release_date=nt.release_date,
                                                   release_date_string=nt.release_date_string,
                                                   album=nt.album,
                                                   lyric_text=nt.lyric_text)
        example.artist_slug = slugify(artist_name)
        example.save()
        return example

    @staticmethod
    def update_relations(example: Example, nt: ExampleParsed) -> (Example, ExampleRelations):
        _ = ExampleParser.purge_relations(example)
        relations = ExampleRelations(
            artist=ExampleParser.process_primary_artists(nt, example),
            from_song=ExampleParser.process_songs(nt, example),
            feat_artist=ExampleParser.process_featured_artists(nt, example),
            example_rhymes=[],
            illustrates_senses=[],
            features_entities=[],
            lyric_links=[]
        )
        return example, relations

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
    def process_songs(nt: ExampleParsed, example: Example) -> List[Song]:
        def process_song(song: Song) -> Song:
            example.from_song.add(song)
            return song
        return [process_song(SongParser.persist(d)) for d in ExampleParser.extract_songs(nt)]

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

