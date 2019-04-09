from dictionary.models import SongParsed, Song, ExampleParsed
from dictionary.utils import slugify


class SongParser:

    @staticmethod
    def parse(nt: ExampleParsed) -> SongParsed:
        try:
            nt = SongParsed(
                xml_id=nt.xml_id,
                slug=slugify(nt.artist_name + ' ' + nt.song_title),
                title=nt.song_title,
                artist_name=nt.artist_name,
                artist_slug=nt.artist_slug,
                release_date=nt.release_date,
                release_date_string=nt.release_date_string,
                album=nt.album
            )
        except Exception as e:
            raise KeyError(f"Song parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: SongParsed):
        song, _ = Song.objects.get_or_create(xml_id=nt.xml_id)
        song.title = nt.title
        song.album = nt.album
        song.slug = nt.slug
        song.release_date = nt.release_date
        song.release_date_string = nt.release_date_string
        song.artist_name = nt.artist_name
        song.artist_slug = nt.artist_slug
        song.save()
        return song
