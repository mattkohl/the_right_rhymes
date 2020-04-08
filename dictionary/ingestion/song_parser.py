from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from typing import List, Tuple

from dictionary.models import SongParsed, Song, ExampleParsed, SongRelations, Artist
from dictionary.utils import slugify


class SongParser:

    @staticmethod
    def parse(nt: ExampleParsed) -> SongParsed:
        try:
            artist_name = nt.primary_artists
            d = SongParsed(
                xml_id=nt.xml_id,
                slug=slugify(artist_name + ' ' + nt.song_title),
                title=nt.song_title,
                artist_name=artist_name,
                artist_slug=slugify(artist_name),
                release_date=nt.release_date,
                release_date_string=nt.release_date_string,
                album=nt.album,
                spot_uri=nt.spot_uri
            )
        except Exception as e:
            raise KeyError(f"Song parse failed: {e}")
        else:
            return d

    @staticmethod
    def persist(nt: SongParsed, primary_artists: List[Artist], featured_artists: List[Artist]) -> Tuple[Song, SongRelations]:
        try:
            song = Song.objects.get(slug=nt.slug, album=nt.album)
            song.title = nt.title
            song.album = nt.album
            song.xml_id = nt.xml_id
            song.release_date = nt.release_date
            song.release_date_string = nt.release_date_string
            song.artist_name = nt.artist_name
            song.artist_slug = nt.artist_slug
            song.spot_uri = nt.spot_uri
            song.save()
        except MultipleObjectsReturned as e:
            print(nt.slug, e)
            raise
        except ObjectDoesNotExist:
            song = Song.objects.create(
                xml_id=nt.xml_id,
                title=nt.title,
                album=nt.album,
                slug=nt.slug,
                release_date=nt.release_date,
                release_date_string=nt.release_date_string,
                artist_name=nt.artist_name,
                artist_slug=nt.artist_slug,
                spot_uri=nt.spot_uri
            )
        return SongParser.update_relations(song, primary_artists, featured_artists)

    @staticmethod
    def update_relations(song: Song, primary_artists: List[Artist], featured_artists: List[Artist]) -> Tuple[Song, SongRelations]:
        purged = SongParser.purge_relations(song)
        purged.artist.add(*primary_artists)
        purged.feat_artist.add(*featured_artists)
        relations = SongRelations(
            artist=primary_artists,
            feat_artist=featured_artists
        )
        return purged, relations

    @staticmethod
    def purge_relations(song: Song) -> Song:
        song.artist.clear()
        song.feat_artist.clear()
        return song
