import time
import sys
import logging
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from typing import List, Dict, AnyStr, Generator, Any
from dictionary.models import Place, Form, Entry, EntryTuple, FormTuple, SenseTuple, DomainTuple, RegionTuple, \
    SemanticClassTuple, SynSetTuple

import xmltodict

from geopy.geocoders import Nominatim
from dictionary.models import Entry, Sense, Example, Artist, Domain, SynSet, \
    NamedEntity, Xref, Collocate, SenseRhyme, ExampleRhyme, LyricLink, \
    Place, Song, SemanticClass, Region, Form
from dictionary.utils import slugify, make_label_from_camel_case, geocode_place, move_definite_article_to_end, \
    update_stats, get_letter


logger = logging.getLogger(__name__)


geolocator = Nominatim(user_agent=__name__)
geocache = []


CHECK_FOR_UPDATES = True


class DictionaryParser:

    @staticmethod
    def parse(xml_dict: Dict) -> List[Dict]:
        """
        :param xml_dict: {"dictionary": { "entry": [ {...}, {...}, ... ] } }
        :return: list of dict entries
        """
        try:
            return xml_dict['dictionary']['entry']
        except Exception as e:
            raise KeyError(f"Could not access ['dictionary']['entry'] in {xml_dict}: {e}")


class EntryParser:

    @staticmethod
    def parse(d: Dict) -> EntryTuple:
        try:
            headword = d['head']['headword']
            nt = EntryTuple(
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
    def update_relations(entry: Entry, nt: EntryTuple) -> Entry:
        entry.forms.add(
            *[FormParser.persist(d) for d in EntryParser.extract_forms(nt)]
        )
        entry.senses.add(
            *[SenseParser.persist(r) for r in EntryParser.extract_senses(nt)]
        )

        return entry

    @staticmethod
    def persist(nt: EntryTuple) -> Entry:
        entry, _ = Entry.objects.get_or_create(headword=nt.headword, slug=nt.slug)
        purged = EntryParser.purge_relations(entry)
        purged.publish = nt.publish
        purged.json = nt.xml_dict
        purged.letter = nt.letter
        purged.sort_key = nt.sort_key
        purged.save()
        return purged

    @staticmethod
    def extract_forms(nt: EntryTuple) -> List[FormTuple]:
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses']['forms'] in {nt.xml_dict}: {e}")
        else:
            return [FormParser.parse(form) for lexeme in lexemes for form in lexeme['forms']]

    @staticmethod
    def process_forms(entry: Entry, forms: List[FormTuple]) -> Generator[Form, None, None]:
        for nt in forms:
            form = FormParser.persist(nt)
            entry.forms.add(form)
            yield form

    @staticmethod
    def extract_senses(nt: EntryTuple):
        try:
            lexemes = nt.xml_dict["senses"]
        except Exception as e:
            raise KeyError(f"Could not access ['senses'] in {nt.xml_dict}: {e}")
        else:
            return [SenseParser.parse(sense, nt.headword, lexeme['pos'], nt.publish) for lexeme in lexemes for sense in lexeme['sense']]

    @staticmethod
    def process_senses(entry: Entry, senses: List[SenseTuple]) -> Generator[Sense, None, None]:
        for nt in senses:
            sense = SenseParser.persist(nt)
            entry.forms.add(sense)
            yield sense


class FormParser:

    @staticmethod
    def parse(d: Dict) -> FormTuple:
        try:
            label, freq = d['form'][0]['#text'], d["form"][0]["@freq"]
            nt = FormTuple(
                slug=slugify(label),
                label=label,
                frequency=int(freq)
            )
        except Exception as e:
            raise KeyError(f"Form parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: FormTuple) -> Form:
        form, _ = Form.objects.get_or_create(slug=nt.slug)
        form.frequency = nt.frequency
        form.save()
        return form


class SenseParser:
    
    @staticmethod
    def parse(d: Dict, headword: str, pos: str, publish: bool) -> SenseTuple:
        try:
            notes = '; '.join([note['#text'].strip() for note in d['note']]) if 'notes' in d else ""
            etymology = '; '.join([etymology['text'] for etymology in d['etym']]) if 'etym' in d else ""
            nt = SenseTuple(
                headword=headword,
                slug=f"{slugify(headword)}#{d['@id']}",
                publish=publish,
                xml_id=d['@id'],
                part_of_speech=pos,
                xml_dict=d,
                definition='; '.join([definition['text'] for definition in d['definition']]),
                notes=notes,
                etymology=etymology
            )
        except Exception as e:
            raise KeyError(f"Sense parse failed: {e}")
        else:
            return nt

    @staticmethod
    def purge_relations(sense: Sense) -> Sense:
        sense.examples.clear()
        sense.domains.clear()
        sense.regions.clear()
        sense.semantic_classes.clear()
        sense.synset.clear()
        sense.xrefs.clear()
        sense.sense_rhymes.clear()
        sense.collocates.clear()
        sense.features_entities.clear()
        sense.cites_artists.clear()
        return sense

    @staticmethod
    def persist(nt: SenseTuple) -> Sense:
        sense, _ = Sense.objects.get_or_create(xml_id=nt.xml_id)
        purged = SenseParser.purge_relations(sense)
        purged.json = nt.xml_dict
        purged.headword = nt.headword
        purged.part_of_speech = nt.part_of_speech
        purged.definition = nt.definition
        purged.etymology = nt.etymology
        purged.notes = nt.notes
        purged.slug = nt.slug
        purged.publish = nt.publish
        purged.save()
        return purged

    @staticmethod
    def update_relations(sense: Sense, nt: SenseTuple) -> Sense:
        sense.domains.add(
            *[DomainParser.persist(d) for d in SenseParser.extract_domains(nt.xml_dict)]
        )
        sense.regions.add(
            *[RegionParser.persist(r) for r in SenseParser.extract_regions(nt.xml_dict)]
        )
        sense.semantic_classes.add(
            *[SemanticClassParser.persist(s) for s in SenseParser.extract_semantic_classes(nt.xml_dict)]
        )
        sense.synset.add(
            *[SynSetParser.persist(r) for r in SenseParser.extract_synsets(nt.xml_dict)]
        )
        return sense

    @staticmethod
    def extract_domains(d: Dict) -> List[DomainTuple]:
        try:
            return [DomainParser.parse(domain_name['@type']) for domain_name in d['domain']]
        except KeyError as _:
            return list()

    @staticmethod
    def extract_regions(d: Dict) -> List[DomainTuple]:
        try:
            return [RegionParser.parse(region_name['@type']) for region_name in d['region']]
        except KeyError as _:
            return list()

    @staticmethod
    def extract_semantic_classes(d: Dict) -> List[SemanticClassTuple]:
        try:
            return [SemanticClassParser.parse(semantic_class_name['@type']) for semantic_class_name in d['semanticClass']]
        except KeyError as _:
            return list()

    @staticmethod
    def extract_synsets(d: Dict) -> List[SynSetTuple]:
        try:
            return [SynSetParser.parse(synset_name['@target']) for synset_name in d['synSetRef']]
        except KeyError as _:
            return list()


class DomainParser:

    @staticmethod
    def parse(n: str) -> DomainTuple:
        name = make_label_from_camel_case(n)
        return DomainTuple(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: DomainTuple):
        domain, _ = Domain.objects.get_or_create(slug=nt.slug)
        domain.name = nt.name
        domain.save()
        return domain


class SemanticClassParser:

    @staticmethod
    def parse(n: str) -> SemanticClassTuple:
        name = make_label_from_camel_case(n)
        return SemanticClassTuple(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: SemanticClassTuple):
        semantic_class, _ = SemanticClass.objects.get_or_create(slug=nt.slug)
        semantic_class.name = nt.name
        semantic_class.save()
        return semantic_class
    
    
class RegionParser:

    @staticmethod
    def parse(n: str) -> RegionTuple:
        name = make_label_from_camel_case(n)
        return RegionTuple(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: RegionTuple):
        region, _ = Region.objects.get_or_create(slug=nt.slug)
        region.name = nt.name
        region.save()
        return region


class SynSetParser:

    @staticmethod
    def parse(n: str) -> SynSetTuple:
        name = make_label_from_camel_case(n)
        return SynSetTuple(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: SynSetTuple):
        synset, _ = SynSet.objects.get_or_create(slug=nt.slug)
        synset.name = nt.name
        synset.save()
        return synset


class FileReader:

    @staticmethod
    def read_xml_file(filename: AnyStr) -> AnyStr:
        f = open(filename, 'rb')
        try:
            xml_string = f.read()
        except Exception as e:
            raise IOError(f"Can't read in source XML: {e}")
        else:
            f.close()
            return xml_string


class JSONConverter:

    @staticmethod
    def parse_to_dict(xml_string: AnyStr) -> Dict:
        force_list = ('entry',
                      'senses',
                      'forms',
                      'form',
                      'sense',
                      'definition',
                      'domain',
                      'region',
                      'semanticClass',
                      'synSetRef'
                      'collocate',
                      'xref',
                      'feat',
                      'note',
                      'etym',
                      'rhyme',
                      'entity',
                      'rf')
        try:
            j = xmltodict.parse(xml_string, force_list=force_list)
        except Exception as e:
            raise SyntaxError(f"Failed to parse XML string: {e}")
        else:
            return j


class DirectoryLoader:

    @staticmethod
    def collect_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]

    @staticmethod
    def process(xml_list) -> Generator:
        from dictionary.management.commands.utils import print_progress
        iterations = len(xml_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete')

        for i, xml in enumerate(xml_list):
            xml_string: str = FileReader.read_xml_file(xml)
            xml_dict: Dict = JSONConverter.parse_to_dict(xml_string)
            print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete ({xml})")
            yield DictionaryParser.parse(xml_dict)


def main(directory='../tRR/XML/tRR_Django'):
    start = time.time()
    xml_files = sorted(DirectoryLoader.collect_files(directory), key=lambda f: f.lower())
    DirectoryLoader.process(xml_files)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    msg = 'Processed dictionary in %d:%02d:%02d\n' % (h, m, s)
    logger.info(msg)
    sys.stdout.write(msg)
    update_stats()
