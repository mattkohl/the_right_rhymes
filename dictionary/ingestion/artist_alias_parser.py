from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.utils import slugify


class ArtistAliasParser:

    @staticmethod
    def parse(row):
        artist_name, alias_name = row
        alias = {
            "name": alias_name,
            "slug": slugify(alias_name)
        }
        artist = {
            "name": artist_name,
            "slug": slugify(artist_name),
            "also_known_as": [alias]
        }
        artist_parsed = ArtistParser.parse(artist)
        done = ArtistParser.persist(artist_parsed)
        print(done)
