from collections import Iterator

from typing import List

from dictionary.models import Place, Form, Entry, EntryParsed, FormParsed, Sense
from dictionary.tests.base import BaseXMLParserTest, BaseTest
from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import XmlFileReader
from dictionary.ingestion.sense_parser import SenseParser
from dictionary.ingestion.form_parser import FormParser
from dictionary.ingestion.entry_parser import EntryParser
from dictionary.ingestion.dictionary_parser import DictionaryParser


class TestFileReader(BaseXMLParserTest):

    def test_cannot_read_file(self):
        with self.assertRaises(Exception):
            XmlFileReader.read_xml_file("foo.xml")

    def test_xml_dict(self):
        result = XmlFileReader.read_xml_file("dictionary/tests/resources/zootie.xml")
        self.assertIn('<?xml version="1.0"', str(result))


class TestJSONConverter(BaseXMLParserTest):

    def test_malformed_file(self):
        with self.assertRaises(Exception):
            x = XmlFileReader.read_xml_file("dictionary/tests/resources/malformed.xml")
            JSONConverter.parse_to_dict(x)

    def test_json_parse(self):
        file_read = XmlFileReader.read_xml_file("dictionary/tests/resources/zootie.xml")
        as_dict = JSONConverter.parse_to_dict(file_read)
        self.assertTrue('dictionary' in as_dict)


class TestDictionaryParser(BaseTest):

    def test_no_dictionary_key(self):
        with self.assertRaises(Exception):
            DictionaryParser.parse({})


class TestEntryParser(BaseXMLParserTest):

    def test_no_entry_key(self):
        with self.assertRaises(KeyError):
            EntryParser.parse({"entries": []})

    def test_parse(self):
        result = EntryParser.parse(self.zootie_entry_dict)
        self.assertEqual(result, self.zootie_entry_nt)

    def test_persist(self):
        persisted: Entry = EntryParser.persist(self.zootie_entry_nt)
        queried: Entry = Entry.objects.get(slug="zootie")
        self.assertEqual(persisted, queried)

    def test_purge_relations(self):
        self.assertEqual(Form.objects.count(), 0)
        entry = EntryParser.persist(self.zootie_entry_nt)
        updated, _ = EntryParser.update_relations(entry, self.zootie_entry_nt)
        self.assertEqual(updated.forms.count(), 1)
        self.assertEqual(Form.objects.count(), 1)
        EntryParser.purge_relations(updated)
        self.assertEqual(updated.forms.count(), 0)

    def test_persist_and_update(self):
        EntryParser.persist(self.zootie_entry_nt)
        update_parsed: EntryParsed = EntryParser.parse(self.zootie_entry_dict_forms_updated)
        update_persisted: Entry = EntryParser.persist(update_parsed)
        queried: Entry = Entry.objects.get(slug="zootie")
        self.assertEqual(update_persisted, queried)

    def test_extract_forms(self):
        result: EntryParsed = EntryParser.extract_forms(self.zootie_entry_nt)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].slug, 'zootie')

    def test_process_forms(self):
        self.assertEqual(Form.objects.count(), 0)
        zootie: Entry = EntryParser.persist(self.zootie_entry_nt)
        forms: List[Form] = EntryParser.process_forms(zootie, [self.zootie_form_nt1])
        self.assertEqual(forms[0], zootie.forms.first())
        self.assertEqual(Form.objects.count(), 1)

    def test_extract_sense(self):
        result = EntryParser.extract_senses(self.zootie_entry_nt)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].slug, 'zootie#e11730_n_1')


class TestFormParser(BaseXMLParserTest):

    def test_parse(self):
        result = FormParser.parse(self.zootie_form_dict1)
        self.assertEqual(result, self.zootie_form_nt1)

    def test_persist(self):
        result = FormParser.persist(self.zootie_form_nt1)
        form = Form.objects.get(slug="zootie")
        self.assertEqual(result, form)


class TestSenseParser(BaseXMLParserTest):
    def test_parse(self):
        result = SenseParser.parse(self.zootie_sense_dict, 'zootie', 'noun', True)
        self.assertEqual(result, self.zootie_sense_nt)

    def test_persist(self):
        result = SenseParser.persist(self.zootie_sense_nt)
        sense = Sense.objects.get(slug=self.zootie_sense_nt.slug)
        self.assertEqual(result, sense)

    def test_update_relations(self):
        sense = SenseParser.persist(self.zootie_sense_nt)
        sense_updated, _ = SenseParser.update_relations(sense, self.zootie_sense_nt)
        self.assertEqual(sense_updated.domains.count(), 2)
        self.assertEqual(sense_updated.regions.count(), 0)
        self.assertEqual(sense_updated.semantic_classes.count(), 0)
        self.assertEqual(sense_updated.synset.count(), 1)
        self.assertEqual(sense_updated.examples.count(), 5)

    def test_purge_relations(self):
        sense = SenseParser.persist(self.zootie_sense_nt)
        sense_updated, relations = SenseParser.update_relations(sense, self.zootie_sense_nt)
        self.assertEqual(sense_updated.domains.count(), 2)
        self.assertEqual(sense_updated.regions.count(), 0)
        self.assertEqual(sense_updated.semantic_classes.count(), 0)
        self.assertEqual(sense_updated.synset.count(), 1)
        self.assertEqual(sense_updated.examples.count(), 5)
        sense_updated = SenseParser.purge_relations(sense)
        self.assertEqual(sense_updated.domains.count(), 0)
        self.assertEqual(sense_updated.regions.count(), 0)
        self.assertEqual(sense_updated.semantic_classes.count(), 0)
        self.assertEqual(sense_updated.synset.count(), 0)
        self.assertEqual(sense_updated.examples.count(), 0)



# class TestTRRExample(BaseTest):
#
#     @mock.patch("dictionary.management.commands.xml_handler.TRRExample.update_example")
#     def test_construct(self, mock_update_example):
#         mock_update_example.return_value = None
#         example_dict = {
#             "@id": "someId",
#             "date": "2017-05-05",
#             "songTitle": "Jammin",
#             "album": "Foo",
#             "artist": "Bar",
#             "lyric": {"text": "Baz"}
#         }
#         result = TRRExample(self.mad_sense, example_dict)
#         self.assertIsInstance(result, TRRExample)
#
#
# class TestTRRSong(BaseTest):
#
#     def test_construct(self):
#
#         class Artist_(object):
#             def __init__(self, artist_object):
#                 self.artist_object = artist_object
#
#         es_ = Artist_(self.erick_sermon)
#
#         xml_id = "a1234"
#         release_date = "1998-01-01"
#         title = "foo"
#         album = "bar"
#         artist_name = "Erick Sermon"
#         slug = "erick-sermon-foo"
#         artist_slug = "erick-sermon"
#         result = TRRSong(xml_id=xml_id,
#                          release_date=release_date,
#                          release_date_string=release_date,
#                          song_title=title,
#                          artist_name=artist_name,
#                          artist_slug=artist_slug,
#                          primary_artists=[es_],
#                          feat_artists=[],
#                          album=album)
#         self.assertIsInstance(result, TRRSong)
#         self.assertEqual(result.slug, slug)
#
#
# class TestTRRPlace(BaseTest):
#
#     def test_construct(self):
#         result = TRRPlace("Paris, Texas, USA")
#         self.assertIsInstance(result, TRRPlace)
#         self.assertEqual(Place.objects.filter(slug="paris-texas-usa").count(), 1)
#         self.assertEqual(Place.objects.filter(slug="texas-usa").count(), 1)
#
#
# class TestTRRLyricLink(BaseTest):
#
#     bad_position_ex = {
#         'album': 'By Any Means',
#         'songTitle': 'Arm and Hammer',
#         'artist': 'Kevin Gates',
#         '@id': '51232',
#         'date': '2014-03-18',
#         'lyric': {
#             'text': 'She like, "Bae, I\'m at the store"',
#             'rf': [{'@lemma': 'bae', '@position': '12', '#text': 'Bae', '@target': 'e2667_n_1'}]
#          }
#     }
#     good_position_ex = {
#         'album': 'King Push',
#         'songTitle': 'Drug Dealers Anonymous',
#         'artist': 'Pusha T',
#         '@id': '66175',
#         'feat': ['Jay Z'],
#         'date': '2015-12-18',
#         'lyric': {
#             'text': 'He told 12, "Gimme 12"',
#             'rf': [
#                 {'@lemma': '12', '@position': '8', '#text': '12', '@target': 'e2045_n_1'},
#                 {'@lemma': '12', '@position': '19', '#text': '12', '@target': 'e2045_n_1'}
#             ]
#         }
#     }
#
#     def test_fix_bad_position(self):
#         link_dict = self.bad_position_ex['lyric']['rf'][0]
#         link_type = 'rf'
#         example_text = self.bad_position_ex['lyric']['text']
#         l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
#         self.assertEqual(l1.position, 11)
#
#     def test_confirm_good_position(self):
#         link_dict = self.good_position_ex['lyric']['rf'][0]
#         link_type = 'rf'
#         example_text = self.good_position_ex['lyric']['text']
#         l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
#         self.assertEqual(l1.position, 8)

