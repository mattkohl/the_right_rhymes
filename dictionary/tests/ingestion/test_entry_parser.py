from typing import List

from dictionary.ingestion.entry_parser import EntryParser
from dictionary.models import Entry, Form, EntryParsed, FormParsed
from dictionary.tests.base import BaseXMLParserTest


class TestEntryParser(BaseXMLParserTest):

    def test_no_entry_key(self):
        with self.assertRaises(KeyError):
            EntryParser.parse({"entries": []})

    def test_parse(self):
        result = EntryParser.parse(self.zootie_entry_dict)
        self.assertEqual(result, self.zootie_entry_nt)

    def test_persist(self):
        print(f"ENTRIES: [{','.join(Entry.objects.all())}]")
        entry, relations = EntryParser.persist(self.zootie_entry_nt)
        print(f"""ENTRIES: [{','.join([f"{e.headword}({e.senses.count()})" for e in Entry.objects.all()])}]""")
        queried: Entry = Entry.objects.get(slug="zootie")
        self.assertEqual(entry, queried)
        print(queried.senses.all())
        self.assertNotEqual(list(queried.senses.all()), list())

    def test_purge_relations(self):
        self.assertEqual(Form.objects.count(), 0)
        entry, relations = EntryParser.persist(self.zootie_entry_nt)

        entry_updated, _ = EntryParser.update_relations(entry, self.zootie_entry_nt, True)
        self.assertEqual(entry_updated.forms.count(), 1)
        self.assertEqual(Form.objects.count(), 1)

        entry_purged = EntryParser.purge_relations(entry_updated)
        self.assertEqual(entry_purged.forms.count(), 0)

    def test_persist_and_update(self):
        _, _ = EntryParser.persist(self.zootie_entry_nt)
        update_parsed: EntryParsed = EntryParser.parse(self.zootie_entry_dict_forms_updated)
        update_persisted, update_relations = EntryParser.persist(update_parsed)
        queried: Entry = Entry.objects.get(slug="zootie")
        self.assertEqual(update_persisted, queried)

    def test_extract_forms(self):
        result: List[FormParsed] = EntryParser.extract_forms(self.zootie_entry_nt)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].slug, 'zootie')

    def test_process_forms(self):
        self.assertEqual(Form.objects.count(), 0)
        zootie, relations = EntryParser.persist(self.zootie_entry_nt)
        forms = EntryParser.process_forms(self.zootie_entry_nt, zootie)
        self.assertEqual(forms[0][0], zootie.forms.first())
        self.assertEqual(Form.objects.count(), 1)

    def test_extract_sense(self):
        result = EntryParser.extract_senses(self.zootie_entry_nt)
        self.assertEqual(len(result), 1)
        self.assertEqual(f"{result[0].slug}#{result[0].xml_id}", 'zootie#e11730_n_1')

    def test_process_senses(self):
        entry, _ = EntryParser.persist(self.zootie_entry_nt)
        sense, _ = EntryParser.process_senses(self.zootie_entry_nt, entry)[0]
        self.assertEqual(entry.senses.count(), 1)
        self.assertEqual(sense.examples.count(), 5)
        exx = [e for e in sense.examples.all()]
        self.assertTrue(exx[-1].lyric_text.endswith("pass the zootie"))

        entry_updated, _ = EntryParser.persist(self.zootie_entry_nt_updated)
        sense_updated, _ = EntryParser.process_senses(self.zootie_entry_nt_updated, entry_updated)[0]
        self.assertEqual(entry_updated.senses.count(), 1)
        self.assertEqual(sense_updated.examples.count(), 5)
        exx = [e for e in sense_updated.examples.all()]
        self.assertTrue(exx[-1].lyric_text.endswith("pass the zootie, yo"))


