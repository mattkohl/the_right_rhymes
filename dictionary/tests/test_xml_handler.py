from collections import OrderedDict
from dictionary.tests.base import BaseXMLTest
from dictionary.management.commands.xml_handler import XMLDict


class TestXMLDict(BaseXMLTest):

    def test_xml_dict(self):
        x = XMLDict(self.source_file)
        self.assertIn('<?xml version="1.0"', str(x.xml_string))

    def test_get_json(self):
        x = XMLDict(self.source_file)
        self.assertIsInstance(x.xml_dict, OrderedDict)
        self.assertTrue('dictionary' in x.xml_dict)


