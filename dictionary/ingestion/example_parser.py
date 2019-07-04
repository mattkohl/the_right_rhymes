from collections import OrderedDict
from typing import Dict, List, Iterator, Tuple

from django.core.exceptions import ObjectDoesNotExist

from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.ingestion.lyric_link_parser import LyricLinkParser
from dictionary.ingestion.named_entity_parser import NamedEntityParser
from dictionary.ingestion.song_parser import SongParser
from dictionary.management.commands.xml_handler import clean_up_date
from dictionary.models import ExampleParsed, Example, Song, ExampleRelations, SongParsed, Artist, ArtistParsed, \
    SongRelations, LyricLink, LyricLinkParsed, Sense, NamedEntity
from dictionary.utils import slugify


class ExampleParser:

    @staticmethod
    def parse(d: Dict) -> ExampleParsed:
        try:
            primary_artists = [d['artist']['#text'] if isinstance(d['artist'], OrderedDict) else d['artist']]
            nt = ExampleParsed(
                primary_artists=primary_artists,
                song_title=d['songTitle'],
                featured_artists=d['feat'] if 'feat' in d else [],
                release_date=clean_up_date(d['date']),
                release_date_string=d['date'],
                album=d['album'],
                lyric_text=d['lyric']['text'],
                xml_id=d["@id"],
                rhymes=d['lyric']["rhyme"] if "rhyme" in d['lyric'] else [],
                rfs=d['lyric']["rf"] if "rf" in d['lyric'] else [],
                xrefs=d['lyric']["xref"] if "xref" in d['lyric'] else [],
                entities=d['lyric']["entity"] if "entity" in d['lyric'] else []
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
            features_entities=ExampleParser.process_entities(nt, example),
            lyric_links=ExampleParser.process_lyric_links(nt, example)
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
    def extract_entities(nt: ExampleParsed) -> List[LyricLinkParsed]:
        return [NamedEntityParser.parse(a) for a in nt.entities]

    @staticmethod
    def process_entities(nt: ExampleParsed, example: Example):
        def process_entity(entity):
            example.features_entities.add(entity)
            return entity
        return [process_entity(NamedEntityParser.persist(ll)) for ll in ExampleParser.extract_entities(nt)]

    @staticmethod
    def extract_rhymes(nt: ExampleParsed) -> List:
        return list()

    @staticmethod
    def extract_rf(nt: ExampleParsed) -> List:
        return list()

    @staticmethod
    def extract_lyric_links(nt: ExampleParsed) -> List[LyricLinkParsed]:
        def _extract_lyric_links():
            for xref in nt.xrefs:
                yield LyricLinkParser.parse(xref, 'xref', nt.lyric_text)
            for rf in nt.rfs:
                yield LyricLinkParser.parse(rf, 'xref', nt.lyric_text)
            for entity in nt.entities:
                if '@type' in entity and entity['@type'] == 'artist':
                    n = entity['@prefLabel'] if 'prefLabel' in entity else entity['#text']
                    _ = ArtistParser.persist(ArtistParser.parse(n))
                    yield LyricLinkParser.parse(entity, 'artist', nt.lyric_text)
                else:
                    yield LyricLinkParser.parse(entity, 'entity', nt.lyric_text)
        return list(_extract_lyric_links())

    @staticmethod
    def process_lyric_links(nt: ExampleParsed, example: Example) -> List[LyricLink]:
        def process_lyric_link(lyric_link: LyricLink) -> LyricLink:
            example.lyric_links.add(lyric_link)
            try:
                sense = Sense.objects.get(xml_id=lyric_link.target_slug)
            except ObjectDoesNotExist:
                sense = Sense.objects.create(xml_id=lyric_link.target_slug)
            example.illustrates_senses.add(sense)
            for artist in example.artist.all():
                artist.primary_senses.add(sense)
            for artist in example.feat_artist.all():
                artist.featured_senses.add(sense)
            return lyric_link
        return [process_lyric_link(LyricLinkParser.persist(lyric_link_parsed)) for lyric_link_parsed in ExampleParser.extract_lyric_links(nt)]
