from typing import List, Dict, Tuple

from dictionary.models import Place, PlaceParsed, PlaceRelations


class PlaceParser:

    @staticmethod
    def parse(d: Dict) -> PlaceParsed:
        pass

    @staticmethod
    def persist(nt: PlaceParsed) -> Tuple[Place, PlaceRelations]:
        pass
