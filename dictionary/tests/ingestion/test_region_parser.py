from dictionary.ingestion.region_parser import RegionParser
from dictionary.models import Region, RegionParsed
from dictionary.tests.base import BaseXMLParserTest


class TestRegionParser(BaseXMLParserTest):

    def test_parse(self):
        expected = RegionParsed("Foo", "foo")
        result = RegionParser.parse("foo")
        self.assertEqual(result, expected)

    def test_persist(self):
        parsed = RegionParsed("Foo", "foo")
        result = RegionParser.persist(parsed)
        region = Region.objects.get(slug="foo")
        self.assertEqual(region, result)
