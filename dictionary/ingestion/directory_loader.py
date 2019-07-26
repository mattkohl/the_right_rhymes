import json
from genericpath import isfile
from os import listdir
from os.path import join
from typing import AnyStr, List, Dict

from dictionary.ingestion.dictionary_parser import DictionaryParser
from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import FileReader


class DirectoryLoader:

    @staticmethod
    def collect_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]

    @staticmethod
    def process_xml(xml_list) -> None:
        from dictionary.management.commands.utils import print_progress
        iterations = len(xml_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete')

        for i, xml in enumerate(xml_list):
            if "malformed" not in xml:
                xml_string: str = FileReader.read_file(xml)
                xml_dict: Dict = JSONConverter.parse_to_dict(xml_string)
                print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete ({xml})")
                entry_tuples = DictionaryParser.parse(xml_dict)
                _ = DictionaryParser.process_entries(entry_tuples)

    @staticmethod
    def process_json(json_list) -> None:
        from dictionary.management.commands.utils import print_progress
        iterations = len(json_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete')

        for i, doc in enumerate(json_list):
            if "malformed" not in doc:
                json_string: str = FileReader.read_file(doc)
                json_doc = json.loads(json_string)
                print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete ({doc})")
                entry_tuples = DictionaryParser.parse(xml_dict)
                _ = DictionaryParser.process_entries(entry_tuples)

