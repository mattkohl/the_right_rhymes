from dictionary.models import SongParsed, Song, ExampleParsed, SongRelations
from dictionary.utils import slugify


class SongParser:

    @staticmethod
    def parse(nt: ExampleParsed) -> SongParsed:
        try:
            artist_name = nt.primary_artists[0]
            d = SongParsed(
                xml_id=nt.xml_id,
                slug=slugify(artist_name + ' ' + nt.song_title),
                title=nt.song_title,
                artist_name=artist_name,
                artist_slug=slugify(artist_name),
                release_date=nt.release_date,
                release_date_string=nt.release_date_string,
                album=nt.album
            )
        except Exception as e:
            raise KeyError(f"Song parse failed: {e}")
        else:
            return d

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

    @staticmethod
    def update_relations(song: Song, nt: SongParsed) -> (Song, SongRelations):
        _ = SongParser.purge_relations(song)
        relations = SongRelations(
            artist=[],
            feat_artist=[],
            examples=[]
        )
        return song, relations

    @staticmethod
    def purge_relations(song: Song) -> Song:
        song.artist.clear()
        song.feat_artist.clear(),
        song.examples.clear()
        return song
