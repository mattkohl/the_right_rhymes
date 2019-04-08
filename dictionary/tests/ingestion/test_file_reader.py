from dictionary.ingestion.xml_file_reader import XmlFileReader
from dictionary.tests.base import BaseXMLParserTest


class TestFileReader(BaseXMLParserTest):

    def test_cannot_read_file(self):
        with self.assertRaises(Exception):
            XmlFileReader.read_xml_file("foo.xml")

    def test_xml_dict(self):
        result = XmlFileReader.read_xml_file("dictionary/tests/resources/zootie.xml")
        self.assertIn('<?xml version="1.0"', str(result))