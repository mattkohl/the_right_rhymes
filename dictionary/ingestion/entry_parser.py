from typing import Dict, List

from dictionary.management.commands.xml_parser import logger
from dictionary.ingestion.sense_parser import SenseParser
from dictionary.ingestion.form_parser import FormParser
from dictionary.models import EntryParsed, Entry, EntryRelations, FormParsed, Form, SenseParsed, Sense
from dictionary.utils import slugify, move_definite_article_to_end, get_letter


class EntryParser:

    @staticmethod
    def parse(d: Dict) -> EntryParsed:
        try:
            headword = d['head']['headword']
            nt = EntryParsed(
                headword=headword,
                slug=slugify(headword),
                sort_key=move_definite_article_to_end(headword).lower(),
                letter=get_letter(headword),
                publish=False if d['@publish'] == 'no' else True,
                xml_dict=d
            )
        except Exception as e:
            raise KeyError(f"Entry parse failed: {e}")
        else:
            logger.info(f"------ Processing: '{headword}' ------")
            return nt

    @staticmethod
    def purge_relations(entry: Entry) -> Entry:
        entry.forms.clear()
        entry.senses.clear()
        return entry

    @staticmethod
    def update_relations(entry: Entry, nt: EntryParsed) -> (Entry, EntryRelations):
        EntryParser.purge_relations(entry)
        return entry, EntryRelations(
            forms=EntryParser.process_forms(entry, EntryParser.extract_forms(nt)),
            senses=EntryParser.process_senses(entry, EntryParser.extract_senses(nt))
        )

    @staticmethod
    def persist(nt: EntryParsed) -> Entry:
        entry, _ = Entry.objects.get_or_create(headword=nt.headword, slug=nt.slug)
        purged = EntryParser.purge_relations(entry)
        purged.publish = nt.publish
        purged.json = nt.xml_dict
        purged.letter = nt.letter
        purged.sort_key = nt.sort_key
        purged.save()
        return purged

    @staticmethod
    def extract_forms(nt: EntryParsed) -> List[FormParsed]:
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses']['forms'] in {nt.xml_dict}: {e}")
        else:
            return [FormParser.parse(form) for lexeme in lexemes for form in lexeme['forms']]

    @staticmethod
    def process_forms(entry: Entry, forms: List[FormParsed]) -> List[Form]:
        def process_form(form: Form) -> Form:
            entry.forms.add(form)
            return form
        return [process_form(FormParser.persist(nt)) for nt in forms]

    @staticmethod
    def extract_senses(nt: EntryParsed):
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses'] in {nt.xml_dict}: {e}")
        else:
            return [SenseParser.parse(sense, nt.headword, lexeme['pos'], nt.publish) for lexeme in lexemes for sense in lexeme['sense']]

    @staticmethod
    def process_senses(entry: Entry, senses: List[SenseParsed]) -> List[Sense]:
        def process_sense(sense: Sense) -> Sense:
            entry.senses.add(sense)
            return sense
        return [process_sense(SenseParser.persist(nt)) for nt in senses]
