from typing import Dict, List, Tuple

from dictionary.ingestion.entry_parser import EntryParser
from dictionary.models import Entry, EntryParsed, EntryRelations


class DictionaryParser:

    @staticmethod
    def parse(xml_dict: Dict) -> List[EntryParsed]:
        """
        :param xml_dict: {"dictionary": { "entry": [ {...}, {...}, ... ] } }
        :return: list of dict entries
        """
        try:
            return [EntryParser.parse(d) for d in xml_dict['dictionary']['entry']]
        except Exception as e:
            raise KeyError(f"Could not access ['dictionary']['entry'] in {xml_dict}: {e}")

    @staticmethod
    def process_entries(entry_nts: List[EntryParsed], force_update: bool = False) -> List[Tuple[Entry, EntryRelations]]:
        def process_entry(entry: Entry, relations: EntryRelations) -> Tuple[Entry, EntryRelations]:
            return entry, relations
        return [process_entry(*EntryParser.persist(nt, force_update)) for nt in entry_nts]
