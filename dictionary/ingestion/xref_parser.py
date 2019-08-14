from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import Xref, XrefParsed
from dictionary.utils import slugify


class XrefParser:

    @staticmethod
    def parse(d: Dict) -> XrefParsed:

        type_map = {
            'conceptRelatesTo': 'Related Concept',
            'derivesFrom': 'Derives From',
            'hasAntonym': 'Antonym',
            'hasInstance': 'Instance',
            'hasPart': 'Meronym',
            'hasSynonym': 'Synonym',
            'hasDerivative': 'Derivative',
            'instanceOf': 'Instance Of',
            'lemmaRelatesTo': 'Related Word',
            'partOf': 'Holonym',
        }

        target_lemma = d["@lemma"] if "@lemma" in d else d["#text"]

        return XrefParsed(
            xref_word=d['#text'],
            xref_type=type_map[d["@type"]] if "@type" in d else "Related Concept",
            target_lemma=target_lemma,
            target_slug=XrefParser.extract_target_slug(d),
            target_id=d['@target'],
            position=d.get("@position"),
            frequency=d.get('@freq')
        )

    @staticmethod
    def persist(nt: XrefParsed) -> Xref:
        try:
            xref = Xref.objects.get(xref_word=nt.xref_word,
                                    xref_type=nt.xref_type,
                                    target_id=nt.target_id,
                                    target_lemma=nt.target_lemma,
                                    target_slug=nt.target_slug)
            xref.position = nt.position
            xref.frequency = nt.frequency
            xref.save()
        except ObjectDoesNotExist:
            xref = Xref.objects.create(xref_word=nt.xref_word,
                                       xref_type=nt.xref_type,
                                       target_id=nt.target_id,
                                       target_lemma=nt.target_lemma,
                                       target_slug=nt.target_slug,
                                       position=nt.position,
                                       frequency=nt.frequency)
        return xref

    @staticmethod
    def extract_target_slug(d):
        if '@target' in d and '@lemma' in d:
            return slugify(d['@lemma'])
        elif '@prefLabel' in d:
            return slugify(d['@prefLabel'])
        else:
            return slugify(d['#text'])
