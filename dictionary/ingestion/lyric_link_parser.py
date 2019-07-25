from typing import Dict, Optional

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import LyricLink, LyricLinkParsed
from dictionary.utils import slugify


class LyricLinkParser:

    XREF = 'xref'
    RHYME = 'rhyme'
    ARTIST = 'artist'
    ENTITY = 'entity'

    @staticmethod
    def parse(d: Dict, link_type: str, example_text: str) -> LyricLinkParsed:
        target_lemma = d["@lemma"] if "@lemma" in d else d["#text"]
        link_text = d['#text']
        return LyricLinkParsed(
            link_text=link_text,
            link_type=link_type,
            target_lemma=target_lemma,
            target_slug=LyricLinkParser.extract_target_slug(d),
            position=LyricLinkParser.confirm_position(link_text, example_text, d['@position']) if '@position' in d else None
        )

    @staticmethod
    def persist(nt: LyricLinkParsed) -> LyricLink:
        try:
            lyric_link = LyricLink.objects.get(link_text=nt.link_text,
                                               link_type=nt.link_type,
                                               target_lemma=nt.target_lemma,
                                               target_slug=nt.target_slug,
                                               position=nt.position)
        except ObjectDoesNotExist:
            lyric_link = LyricLink.objects.create(link_text=nt.link_text,
                                                  link_type=nt.link_type,
                                                  target_lemma=nt.target_lemma,
                                                  target_slug=nt.target_slug,
                                                  position=nt.position)
        return lyric_link

    @staticmethod
    def extract_target_slug(d) -> str:
        if '@target' in d and '@lemma' in d:
            return slugify(d['@lemma']) + '#' + d['@target']
        elif '@prefLabel' in d:
            return slugify(d['@prefLabel'])
        else:
            return slugify(d['#text'])

    @staticmethod
    def confirm_position(link_text: str, example_text: str, position: Optional[int]) -> int:
        try:
            pos = int(position)
            i = example_text.index(link_text)
            if pos != i and example_text.count(link_text) == 1 and pos - 1 == i:
                return pos - 1
            return pos
        except Exception as e:
            print(f"Unable to confirm position of {link_text} in {example_text}")
            raise e
