from dictionary.ingestion.artist_parser import ArtistParser
from dictionary.utils import slugify


class ArtistOriginParser:

    @staticmethod
    def parse(row):
        artist_name, origin_full_name, latitude, longitude = row
        origin = {
            "full_name": origin_full_name,
            "name": origin_full_name.split(", ")[0],
            "latitude": latitude,
            "longitude": longitude,
            "slug": slugify(origin_full_name)
        }
        artist = {
            "name": artist_name,
            "slug": slugify(artist_name),
            "origin": origin
        }
        artist_parsed = ArtistParser.parse(artist)
        _ = ArtistParser.persist(artist_parsed)
