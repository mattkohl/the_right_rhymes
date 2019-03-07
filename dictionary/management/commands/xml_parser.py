import time
import sys
import logging
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from typing import List, Dict, AnyStr, Generator
from dictionary.models import Place, Form, Entry

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
            raise KeyError(f"Could not access ['dictionary']['entry'] in xml_dict: {e}")


class EntryParser:

    @staticmethod
    def parse(entry_dict: Dict) -> Entry:
        try:
            headword = entry_dict['head']['headword']
            sort_key = move_definite_article_to_end(headword).lower()
            slug = slugify(headword)
            letter = get_letter(headword)
            publish = False if entry_dict['@publish'] == 'no' else True
        except Exception as e:
            raise KeyError(f"Entry parse failed: {e}")
        else:
            logger.info(f"------ Processing: '{headword}' ------")
            entry_created, _ = Entry.objects.get_or_create(headword=headword, slug=slug)
            entry_updated = EntryParser.update(entry_created, publish, entry_dict, sort_key, letter)
            return entry_updated

    @staticmethod
    def update(entry: Entry, publish: bool, entry_dict: Dict, sort_key: AnyStr, letter: chr) -> Entry:
        entry.publish = publish
        entry.json = entry_dict
        entry.letter = letter
        entry.sort_key = sort_key
        entry.save()
        return entry


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
    dictionaries = DirectoryLoader.process(xml_files)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    msg = 'Processed dictionary in %d:%02d:%02d\n' % (h, m, s)
    logger.info(msg)
    sys.stdout.write(msg)
    update_stats()
