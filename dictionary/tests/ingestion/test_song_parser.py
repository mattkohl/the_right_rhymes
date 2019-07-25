from dictionary.ingestion.song_parser import SongParser
from dictionary.models import Song, Artist
from dictionary.tests.base import BaseXMLParserTest


class TestSongParser(BaseXMLParserTest):
    def test_parse(self):
        result = SongParser.parse(self.zootie_example_nt)
        self.assertEqual(result, self.zootie_song_nt)

    def test_persist(self):
        artist = Artist(name=self.zootie_song_nt.artist_name, slug=self.zootie_song_nt.artist_slug)
        artist.save()
        primary_artists = [artist]
        featured_artists = []
        result, relations = SongParser.persist(self.zootie_song_nt, primary_artists, featured_artists)
        song = Song.objects.get(slug=self.zootie_song_nt.slug)
        self.assertEqual(result, song)

    def test_update_relations(self):
        artist = Artist(name=self.zootie_song_nt1.artist_name, slug=self.zootie_song_nt1.artist_slug)
        artist.save()
        feat = Artist(name="The Legion", slug="legion-the")
        feat.save()
        primary_artists = [artist]
        featured_artists = [feat]
        song, relations = SongParser.persist(self.zootie_song_nt1, primary_artists, featured_artists)
        self.assertEqual(song.artist.count(), 1)
        self.assertEqual(song.feat_artist.count(), 1)

    def test_purge_relations(self):
        artist = Artist(name=self.zootie_song_nt1.artist_name, slug=self.zootie_song_nt1.artist_slug)
        artist.save()
        feat = Artist(name="The Legion", slug="legion-the")
        feat.save()
        primary_artists = [artist]
        featured_artists = [feat]
        song, relations = SongParser.persist(self.zootie_song_nt1, primary_artists, featured_artists)
        self.assertEqual(song.artist.count(), 1)
        self.assertEqual(song.feat_artist.count(), 1)
        song_purged = SongParser.purge_relations(song)
        self.assertEqual(song_purged.artist.count(), 0)
        self.assertEqual(song_purged.feat_artist.count(), 0)


