from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.utils import slugify


class ArtistMembershipParser:

    @staticmethod
    def parse(row):
        artist_name, group_name = row
        group = {
            "name": group_name,
            "slug": slugify(group_name)
        }
        artist = {
            "name": artist_name,
            "slug": slugify(artist_name),
            "member_of": [group]
        }
        artist_parsed = ArtistParser.parse(artist)
        done = ArtistParser.persist(artist_parsed)
        print(done)
