from typing import Dict, List, Tuple

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from dictionary.ingestion.sense_parser import SenseParser
from dictionary.ingestion.form_parser import FormParser
from dictionary.models import EntryParsed, Entry, EntryRelations, FormParsed, Form, SenseParsed, Sense, SenseRelations, \
    FormRelations
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
            print(f" ['{headword}']")
            return nt

    @staticmethod
    def persist(nt: EntryParsed, force_update: bool = False) -> Tuple[Entry, EntryRelations]:
        update = force_update
        try:
            entry = Entry.objects.get(slug=nt.slug)
            update = force_update or (nt.xml_dict != entry.json)
            if update:
                entry.publish = nt.publish
                entry.json = nt.xml_dict
                entry.letter = nt.letter
                entry.sort_key = nt.sort_key
                entry.save()
        except MultipleObjectsReturned as e:
            print(nt.slug, e)
            raise
        except ObjectDoesNotExist:
            entry = Entry.objects.create(headword=nt.headword, slug=nt.slug, publish=nt.publish, json=nt.xml_dict,
                                         letter=nt.letter, sort_key=nt.sort_key)
            update = True
        return EntryParser.update_relations(entry, nt, update)

    @staticmethod
    def purge_relations(entry: Entry) -> Entry:
        entry.forms.clear()
        entry.senses.clear()
        return entry

    @staticmethod
    def update_relations(entry: Entry, nt: EntryParsed, update: bool = False) -> Tuple[Entry, EntryRelations]:
        if update:
            purged = EntryParser.purge_relations(entry)
            return purged, EntryRelations(
                forms=EntryParser.process_forms(nt, purged),
                senses=EntryParser.process_senses(nt, purged)
            )
        return entry, EntryRelations(forms=list(), senses=list())

    @staticmethod
    def extract_forms(nt: EntryParsed) -> List[FormParsed]:
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses']['forms'] in {nt.xml_dict}: {e}")
        else:
            return [FormParser.parse(form) for lexeme in lexemes for form in lexeme['forms']]

    @staticmethod
    def process_forms(nt: EntryParsed, entry: Entry) -> List[Tuple[Form, FormRelations]]:
        def process_form(form: Form, relations: FormRelations) -> Tuple[Form, FormRelations]:
            _, _ = FormParser.update_relations(form)
            entry.forms.add(form)
            return form, relations
        return [process_form(*FormParser.persist(a)) for a in EntryParser.extract_forms(nt)]

    @staticmethod
    def extract_senses(nt: EntryParsed) -> List[SenseParsed]:
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses'] in {nt.xml_dict}: {e}")
        else:
            return [SenseParser.parse(sense, nt.headword, lexeme['pos'], nt.publish) for lexeme in lexemes for sense in
                    lexeme['sense']]

    @staticmethod
    def process_senses(nt: EntryParsed, entry: Entry) -> List[Tuple[Sense, SenseRelations]]:
        def process_sense(sense: Sense, relations: SenseRelations) -> Tuple[Sense, SenseRelations]:
            entry.senses.add(sense)
            return sense, relations
        return [process_sense(*SenseParser.persist(a)) for a in EntryParser.extract_senses(nt)]
