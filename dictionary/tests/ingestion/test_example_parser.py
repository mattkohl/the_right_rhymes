from dictionary.ingestion.example_parser import ExampleParser
from dictionary.models import Example
from dictionary.tests.base import BaseXMLParserTest


class TestExampleParser(BaseXMLParserTest):
    def test_parse(self):
        result = ExampleParser.parse(self.zootie_example_dict)
        self.assertEqual(result, self.zootie_example_nt)

    def test_persist(self):
        result, relations = ExampleParser.persist(self.zootie_example_nt)
        example = Example.objects.get(artist_name=self.zootie_example_nt.primary_artists[0], song_title=self.zootie_example_nt.song_title, lyric_text=self.zootie_example_nt.lyric_text)
        self.assertEqual(result, example)

    def test_update_relations(self):
        example, relations = ExampleParser.persist(self.zootie_example_nt1)
        example_updated, _ = ExampleParser.update_relations(example, self.zootie_example_nt1)
        self.assertEqual(example_updated.from_song.count(), 1)
        self.assertEqual(example_updated.artist.count(), 1)
        self.assertEqual(example_updated.feat_artist.count(), 1)

    def test_purge_relations(self):
        example, relations = ExampleParser.persist(self.zootie_example_nt)

        example_updated, _ = ExampleParser.update_relations(example, self.zootie_example_nt1)
        self.assertEqual(example_updated.from_song.count(), 1)
        self.assertEqual(example_updated.artist.count(), 1)
        self.assertEqual(example_updated.feat_artist.count(), 1)

        example_purged = ExampleParser.purge_relations(example_updated)
        self.assertEqual(example_purged.from_song.count(), 0)
        self.assertEqual(example_purged.artist.count(), 0)
        self.assertEqual(example_purged.feat_artist.count(), 0)


