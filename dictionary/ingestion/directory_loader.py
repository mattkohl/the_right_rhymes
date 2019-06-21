from genericpath import isfile
from os import listdir
from os.path import join
from typing import AnyStr, List, Generator, Dict

from dictionary.ingestion.dictionary_parser import DictionaryParser
from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import XmlFileReader


class DirectoryLoader:

    @staticmethod
    def collect_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]

    @staticmethod
    def process(xml_list) -> None:
        from dictionary.management.commands.utils import print_progress
        iterations = len(xml_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete')

        for i, xml in enumerate(xml_list):
            if "malformed" not in xml:
                xml_string: str = XmlFileReader.read_xml_file(xml)
                xml_dict: Dict = JSONConverter.parse_to_dict(xml_string)
                print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete ({xml})")
                entry_tuples = DictionaryParser.parse(xml_dict)
                _ = DictionaryParser.process_entries(entry_tuples)

