from unittest import mock
from collections import OrderedDict
from dictionary.tests.base import BaseXMLTest, BaseTest
from dictionary.management.commands.xml_handler import XMLDict, TRRDict, TRREntry, TRRExample, TRRLyricLink


class TestXMLDict(BaseXMLTest):

    def test_cannot_read_file(self):
        with self.assertRaises(Exception):
            XMLDict("foo.xml")

    def test_malformed_file(self):
        with self.assertRaises(Exception):
            x = XMLDict("dictionary/tests/resources/malformed.xml")
            x.get_json()

    def test_xml_dict(self):
        self.assertIn('<?xml version="1.0"', str(self.x.xml_string))

    def test_get_json(self):
        self.assertIsInstance(self.x.xml_dict, OrderedDict)
        self.assertTrue('dictionary' in self.x.xml_dict)


class TestTRRDict(BaseTest):

    def test_no_dictionary_key(self):
        with self.assertRaises(Exception):
            TRRDict({})

    def test_no_entry_key(self):
        with self.assertRaises(Exception):
            TRRDict({"dictionary": {"entries": []}})

    @mock.patch("dictionary.management.commands.xml_handler.TRRDict.print_stats")
    def test_construct_2(self, mock_print_stats):
        mock_print_stats.return_value = ""
        result = TRRDict({"dictionary": {"entry": []}})
        self.assertEqual(result.entry_count, 0)
        self.assertEqual(str(result), "Python dict representation of The Right Rhymes. Entry count: 0")

    def test_print_stats(self):
        result = TRRDict({"dictionary": {"entry": []}})
        self.assertEqual(str(result), "Python dict representation of The Right Rhymes. Entry count: 0")


class TestTRREntry(BaseTest):

    entry_dict = {
            'senses': [],
            'head': {'headword': 'zootie'},
            '@sk': 'zootie',
            '@publish': 'yes',
            '@eid': 'e11730'
        }

    @mock.patch("dictionary.management.commands.xml_handler.TRREntry.update_entry")
    def test_construct(self, mock_update_entry):
        mock_update_entry.return_value = None
        result = TRREntry(self.entry_dict)
        self.assertEqual(str(result), 'zootie')


class TestTRRLyricLink(BaseTest):

    bad_position_ex = {
        'album': 'By Any Means',
        'songTitle': 'Arm and Hammer',
        'artist': 'Kevin Gates',
        '@id': '51232',
        'date': '2014-03-18',
        'lyric': {
            'text': 'She like, "Bae, I\'m at the store"',
            'rf': [{'@lemma': 'bae', '@position': '12', '#text': 'Bae', '@target': 'e2667_n_1'}]
         }
    }
    good_position_ex = {
        'album': 'King Push',
        'songTitle': 'Drug Dealers Anonymous',
        'artist': 'Pusha T',
        '@id': '66175',
        'feat': ['Jay Z'],
        'date': '2015-12-18',
        'lyric': {
            'text': 'He told 12, "Gimme 12"',
            'rf': [
                {'@lemma': '12', '@position': '8', '#text': '12', '@target': 'e2045_n_1'},
                {'@lemma': '12', '@position': '19', '#text': '12', '@target': 'e2045_n_1'}
            ]
        }
    }

    def test_fix_bad_position(self):
        link_dict = self.bad_position_ex['lyric']['rf'][0]
        link_type = 'rf'
        example_text = self.bad_position_ex['lyric']['text']
        l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
        self.assertEqual(l1.position, 11)

    def test_confirm_good_position(self):
        link_dict = self.good_position_ex['lyric']['rf'][0]
        link_type = 'rf'
        example_text = self.good_position_ex['lyric']['text']
        l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
        self.assertEqual(l1.position, 8)
