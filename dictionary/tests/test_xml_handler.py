from unittest import mock
from collections import OrderedDict
from dictionary.tests.base import BaseXMLTest, BaseTest
from dictionary.management.commands.xml_handler import XMLDict, TRRDict, TRREntry


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
