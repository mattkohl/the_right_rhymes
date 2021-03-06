from typing import Dict

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from dictionary.models import Collocate, CollocateParsed
from dictionary.utils import slugify


class CollocateParser:

    @staticmethod
    def parse(d: Dict, sense_id: str) -> CollocateParsed:
        return CollocateParsed(
            collocate_lemma=d['#text'],
            source_sense_xml_id=sense_id,
            target_id=d['@target'],
            target_slug=slugify(d['#text']),
            frequency=d['@freq']
        )

    @staticmethod
    def persist(nt: CollocateParsed):
        try:
            collocate = Collocate.objects.get(collocate_lemma=nt.collocate_lemma,
                                              source_sense_xml_id=nt.source_sense_xml_id,
                                              target_id=nt.target_id)
            collocate.target_slug = nt.target_slug,
            collocate.frequency = nt.frequency
            collocate.save()
        except MultipleObjectsReturned as e:
            print(nt.collocate_lemma, nt.source_sense_xml_id, nt.target_id, e)
            raise
        except ObjectDoesNotExist:
            collocate = Collocate.objects.create(collocate_lemma=nt.collocate_lemma,
                                                 source_sense_xml_id=nt.source_sense_xml_id,
                                                 target_id=nt.target_id,
                                                 target_slug=nt.target_slug,
                                                 frequency=nt.frequency)
        return collocate
