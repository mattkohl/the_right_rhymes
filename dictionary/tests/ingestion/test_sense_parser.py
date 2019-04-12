from dictionary.ingestion.sense_parser import SenseParser
from dictionary.models import Sense
from dictionary.tests.base import BaseXMLParserTest


class TestSenseParser(BaseXMLParserTest):
    def test_parse(self):
        result = SenseParser.parse(self.zootie_sense_dict, 'zootie', 'noun', True)
        self.assertEqual(result, self.zootie_sense_nt)

    def test_persist(self):
        result = SenseParser.persist(self.zootie_sense_nt)
        sense = Sense.objects.get(slug=self.zootie_sense_nt.slug)
        self.assertEqual(result, sense)

    def test_update_relations(self):
        sense = SenseParser.persist(self.zootie_sense_nt)
        sense_updated, _ = SenseParser.update_relations(sense, self.zootie_sense_nt)
        self.assertEqual(sense_updated.domains.count(), 2)
        self.assertEqual(sense_updated.regions.count(), 0)
        self.assertEqual(sense_updated.semantic_classes.count(), 0)
        self.assertEqual(sense_updated.synset.count(), 1)
        self.assertEqual(sense_updated.examples.count(), 5)

    def test_purge_relations(self):
        sense = SenseParser.persist(self.zootie_sense_nt)

        sense_updated, relations = SenseParser.update_relations(sense, self.zootie_sense_nt)
        self.assertEqual(sense_updated.domains.count(), 2)
        self.assertEqual(sense_updated.regions.count(), 0)
        self.assertEqual(sense_updated.semantic_classes.count(), 0)
        self.assertEqual(sense_updated.synset.count(), 1)
        self.assertEqual(sense_updated.examples.count(), 5)

        sense_purged = SenseParser.purge_relations(sense_updated)
        self.assertEqual(sense_purged.domains.count(), 0)
        self.assertEqual(sense_purged.regions.count(), 0)
        self.assertEqual(sense_purged.semantic_classes.count(), 0)
        self.assertEqual(sense_purged.synset.count(), 0)
        self.assertEqual(sense_purged.examples.count(), 0)