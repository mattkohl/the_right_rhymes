from dictionary.ingestion.example_parser import ExampleParser
from dictionary.models import Example
from dictionary.tests.base import BaseXMLParserTest


class TestExampleParser(BaseXMLParserTest):
    def test_parse(self):
        result = ExampleParser.parse(self.zootie_example_dict)
        self.assertEqual(result, self.zootie_example_nt)

    def test_persist(self):
        result = ExampleParser.persist(self.zootie_example_nt)
        example = Example.objects.get(artist_name=self.zootie_example_nt.artist_name, song_title=self.zootie_example_nt.song_title, lyric_text=self.zootie_example_nt.lyric_text)
        self.assertEqual(result, example)

    def test_update_relations(self):
        example = ExampleParser.persist(self.zootie_example_nt)
        example_updated, _ = ExampleParser.update_relations(example, self.zootie_example_nt)
        self.assertEqual(example_updated.from_song.count(), 1)

    def test_purge_relations(self):
        example = ExampleParser.persist(self.zootie_example_nt)
        example_updated, relations = ExampleParser.update_relations(example, self.zootie_example_nt)
        self.assertEqual(example_updated.from_song.count(), 1)
        example_updated = ExampleParser.purge_relations(example)
        self.assertEqual(example_updated.from_song.count(), 0)
