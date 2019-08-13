from typing import List, Dict, Tuple

from dictionary.ingestion.models import OriginParsed
from dictionary.models import Place, PlaceRelations


class OriginParser:

    @staticmethod
    def parse(json_doc: Dict) -> List[OriginParsed]:
        pass

    @staticmethod
    def process_origins(nts: List[OriginParsed]) -> List[Tuple[Place, PlaceRelations]]:
        pass
