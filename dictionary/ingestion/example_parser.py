from collections import OrderedDict
from typing import Dict, List, Iterator

from dictionary.ingestion.song_parser import SongParser
from dictionary.management.commands.xml_handler import clean_up_date
from dictionary.models import ExampleParsed, Example, Song, ExampleRelations, SongParsed, Artist
from dictionary.utils import slugify


class ExampleParser:

    @staticmethod
    def parse(d: Dict) -> ExampleParsed:
        try:
            artist_name = d['artist']['#text'] if isinstance(d['artist'], OrderedDict) else d['artist']
            print(d['artist'])
            from pprint import pprint
            pprint(d)
            nt = ExampleParsed(
                artist_name=artist_name,
                artist_slug=slugify(artist_name),
                song_title=d['songTitle'],
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
        example, _ = Example.objects.get_or_create(song_title=nt.song_title,
                                                   artist_name=nt.artist_name,
                                                   release_date=nt.release_date,
                                                   release_date_string=nt.release_date_string,
                                                   album=nt.album,
                                                   lyric_text=nt.lyric_text)
        example.artist_slug = nt.artist_slug
        example.save()
        return example

    @staticmethod
    def update_relations(example: Example, nt: ExampleParsed) -> (Example, ExampleRelations):
        _ = ExampleParser.purge_relations(example)
        relations = ExampleRelations(
            artist=[],
            from_song=ExampleParser.process_songs(nt, example),
            feat_artist=[],
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
            return example.from_song.add(song)
        return [process_song(SongParser.persist(d)) for d in ExampleParser.extract_songs(nt)]

    @staticmethod
    def extract_artists(nt: ExampleParsed, artist_type: str) -> List[Artist]:
        pass

    @staticmethod
    def extract_featured_artists(nt: ExampleParsed) -> List[Artist]:
        pass

    @staticmethod
    def process_primary_artists(nt: ExampleParsed, example: Example) -> List[Artist]:
        def process_primary_artist(artist: Artist) -> Artist:
            return example.artist.add(artist)
        return [process_primary_artist(a) for a in ExampleParser.extract_primary_artists(nt)]

    @staticmethod
    def process_featured_artists(nt: ExampleParsed, example: Example) -> List[Artist]:
        def process_featured_artist(artist: Artist) -> Artist:
            return example.feat_artist.add(artist)
        return [process_featured_artist(a) for a in ExampleParser.extract_featured_artists(nt)]

