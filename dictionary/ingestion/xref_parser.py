from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import Xref, XrefParsed, Sense, Example
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
            target_slug=slugify(target_lemma),
            target_id=d['@target'],
            position=d["@position"] if "@position" in d else None,
            frequency=d['@freq'] if "@freq" in d else None
        )

    @staticmethod
    def persist(nt: XrefParsed, example: Example) -> Xref:
        # xref_sense_object, _ = Sense.objects.get_or_create(xml_id=xref['@target'])
        # self.example_object.illustrates_senses.add(xref_sense_object)
        # for artist in self.primary_artists:
        #     artist.artist_object.primary_senses.add(xref_sense_object)
        # self.lyric_links.append(TRRLyricLink(link_dict=xref, link_type='xref', example_text=self.lyric_text))
        # if '@rhymeTarget' in xref:
        #     self.example_rhymes.append(TRRExampleRhyme(xref))
        try:
            sense = Sense.objects.get(xml_id=nt.target_id)
        except ObjectDoesNotExist:
            sense = Sense.objects.create(xml_id=nt.target_id)
        finally:
            example.illustrates_senses(sense)
            for artist in example.artist:
                artist.primary_senses.add(sense)
            for artist in example.feat_artist:
                artist.featured_senses.add(sense)

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
