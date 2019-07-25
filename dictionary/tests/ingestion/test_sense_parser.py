from dictionary.ingestion.sense_parser import SenseParser
from dictionary.models import Sense, SynSet
from dictionary.tests.base import BaseXMLParserTest


class TestSenseParser(BaseXMLParserTest):
    def test_parse(self):
        result = SenseParser.parse(self.zootie_sense_dict, 'zootie', 'noun', True)
        self.assertEqual(result, self.zootie_sense_nt)

    def test_persist(self):
        result, relations = SenseParser.persist(self.zootie_sense_nt)
        sense = Sense.objects.get(slug=self.zootie_sense_nt.slug)
        self.assertEqual(result, sense)

    def test_update_relations(self):
        sense, relations = SenseParser.persist(self.zootie_sense_nt)
        self.assertEqual(sense.domains.count(), 2)
        self.assertEqual(sense.regions.count(), 0)
        self.assertEqual(sense.semantic_classes.count(), 0)
        self.assertEqual(sense.synset.count(), 1)
        self.assertEqual(sense.examples.count(), 5)
        self.assertEqual(sense.collocates.count(), 2)
        self.assertEqual(sense.xrefs.count(), 2)

    def test_purge_relations(self):
        sense, relations = SenseParser.persist(self.zootie_sense_nt)
        self.assertEqual(sense.domains.count(), 2)
        self.assertEqual(sense.regions.count(), 0)
        self.assertEqual(sense.semantic_classes.count(), 0)
        self.assertEqual(sense.synset.count(), 1)
        self.assertEqual(sense.examples.count(), 5)
        self.assertEqual(sense.collocates.count(), 2)

        sense_purged = SenseParser.purge_relations(sense)
        self.assertEqual(sense_purged.domains.count(), 0)
        self.assertEqual(sense_purged.regions.count(), 0)
        self.assertEqual(sense_purged.semantic_classes.count(), 0)
        self.assertEqual(sense_purged.synset.count(), 0)
        self.assertEqual(sense_purged.examples.count(), 0)
        self.assertEqual(sense.collocates.count(), 0)