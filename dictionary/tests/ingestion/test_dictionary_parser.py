from dictionary.ingestion.dictionary_parser import DictionaryParser
from dictionary.tests.base import BaseTest


class TestDictionaryParser(BaseTest):

    def test_no_dictionary_key(self):
        with self.assertRaises(Exception):
            DictionaryParser.parse({})