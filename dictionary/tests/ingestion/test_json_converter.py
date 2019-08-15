from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import FileReader
from dictionary.tests.base import BaseXMLParserTest


class TestJSONConverter(BaseXMLParserTest):

    def test_malformed_file(self):
        with self.assertRaises(Exception):
            x = FileReader.read_file("dictionary/tests/resources/malformed.xml")
            JSONConverter.parse_to_dict(x)

    def test_json_parse_zootie(self):
        file_read = FileReader.read_file("dictionary/tests/resources/zootie.xml")
        as_dict = JSONConverter.parse_to_dict(file_read)
        self.assertTrue('dictionary' in as_dict)

    def test_json_parse_12(self):
        file_read = FileReader.read_file("dictionary/tests/resources/12.xml")
        as_dict = JSONConverter.parse_to_dict(file_read)
        self.assertTrue('dictionary' in as_dict)

    def test_json_parse_50(self):
        file_read = FileReader.read_file("dictionary/tests/resources/50.xml")
        as_dict = JSONConverter.parse_to_dict(file_read)
        self.assertTrue('dictionary' in as_dict)