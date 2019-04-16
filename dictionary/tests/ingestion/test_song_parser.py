from dictionary.ingestion.example_parser import SongParser
from dictionary.models import Song
from dictionary.tests.base import BaseXMLParserTest


class TestSongParser(BaseXMLParserTest):
    def test_parse(self):
        result = SongParser.parse(self.zootie_example_nt)
        self.assertEqual(result, self.zootie_song_nt)

    def test_persist(self):
        result = SongParser.persist(self.zootie_song_nt)
        song = Song.objects.get(slug=self.zootie_song_nt.slug)
        self.assertEqual(result, song)

    def test_update_relations(self):
        song = SongParser.persist(self.zootie_song_nt)
        self.assertEqual(song.artist.count(), 1)
        self.assertEqual(song.feat_artist.count(), 1)

    def test_purge_relations(self):

        song = SongParser.persist(self.zootie_song_nt)
        song_purged = SongParser.purge_relations(song)
        self.assertEqual(song_purged.artist.count(), 0)
        self.assertEqual(song_purged.feat_artist.count(), 0)


