import json
from genericpath import isfile
from os import listdir
from os.path import join
from typing import AnyStr, List, Dict

from dictionary.ingestion.artist_origin_parser import ArtistOriginParser
from dictionary.ingestion.artist_alias_parser import ArtistAliasParser
from dictionary.ingestion.artist_membership_parser import ArtistMembershipParser
from dictionary.ingestion.dictionary_parser import DictionaryParser
from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import FileReader


class DirectoryLoader:

    @staticmethod
    def collect_xml_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and f.endswith("xml")]

    @staticmethod
    def collect_json_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and f.endswith("json")]

    @staticmethod
    def collect_csv_files(directory: AnyStr) -> List[AnyStr]:
        return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f)) and f.endswith("csv")]

    @staticmethod
    def process_xml(xml_list: List[str], force_update: bool = False) -> None:
        from dictionary.management.commands.utils import print_progress
        iterations = len(xml_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete ')

        for i, xml in enumerate(xml_list):
            if "malformed" not in xml:
                xml_string: str = FileReader.read_file(xml)
                xml_dict: Dict = JSONConverter.parse_to_dict(xml_string)
                print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete ", filename=xml)
                entry_tuples = DictionaryParser.parse(xml_dict)
                _ = DictionaryParser.process_entries(entry_tuples, force_update)

    @staticmethod
    def process_json(json_list) -> None:
        from dictionary.management.commands.utils import print_progress
        iterations = len(json_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete ')

        for i, doc in enumerate(json_list):
            if "malformed" not in doc:
                json_string: str = FileReader.read_file(doc)
                json_doc = json.loads(json_string)
                print_progress(i + 1, iterations, prefix='Progress:', suffix=f"Complete", filename=doc)

    @staticmethod
    def process_csv(csv_list: List[str]) -> None:
        from dictionary.management.commands.utils import print_progress
        import csv
        iterations = len(csv_list)
        print_progress(0, iterations, prefix='Progress:', suffix='Complete ')

        for i, doc in enumerate(csv_list):
            print(doc)
            if doc.endswith("artist-origins.csv"):
                with open(doc) as csv_string:
                    reader = csv.reader(csv_string, delimiter=';')
                    next(reader)  # skip header
                    for row in reader:
                        ArtistOriginParser.parse(row)
            if doc.endswith("artist-aliases.csv"):
                with open(doc) as csv_string:
                    reader = csv.reader(csv_string, delimiter=';')
                    next(reader)  # skip header
                    for row in reader:
                        ArtistAliasParser.parse(row)
            if doc.endswith("artist-membership.csv"):
                with open(doc) as csv_string:
                    reader = csv.reader(csv_string, delimiter=';')
                    next(reader)  # skip header
                    for row in reader:
                        ArtistMembershipParser.parse(row)

