from unittest import mock
from collections import OrderedDict
from dictionary.tests.base import BaseXMLTest, BaseTRRTest
from dictionary.management.commands.xml_handler import XMLDict, TRRDict


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


class TestTRRDict(BaseTRRTest):

    @mock.patch("dictionary.management.commands.xml_handler.TRRDict.get_dictionary")
    @mock.patch("dictionary.management.commands.xml_handler.TRRDict.get_entries")
    @mock.patch("dictionary.management.commands.xml_handler.TRRDict.print_stats")
    def test_construct(self, mock_print_stats, mock_get_entries, mock_get_dictionary):
        mock_print_stats.return_value = ""
        mock_get_entries.return_value = []
        mock_get_dictionary.return_value = {}
        result = TRRDict(self.x.xml_dict)
        self.assertEqual(result.entry_count, 0)
        self.assertEqual(str(result), "Python dict representation of The Right Rhymes. Entry count: 0")

