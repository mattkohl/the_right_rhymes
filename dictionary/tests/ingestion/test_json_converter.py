from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import XmlFileReader
from dictionary.tests.base import BaseXMLParserTest


class TestJSONConverter(BaseXMLParserTest):

    def test_malformed_file(self):
        with self.assertRaises(Exception):
            x = XmlFileReader.read_xml_file("dictionary/tests/resources/malformed.xml")
            JSONConverter.parse_to_dict(x)

    def test_json_parse(self):
        file_read = XmlFileReader.read_xml_file("dictionary/tests/resources/zootie.xml")
        as_dict = JSONConverter.parse_to_dict(file_read)
        self.assertTrue('dictionary' in as_dict)