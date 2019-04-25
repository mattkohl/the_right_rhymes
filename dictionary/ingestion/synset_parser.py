from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import SynSetParsed, SynSet
from dictionary.utils import make_label_from_camel_case, slugify


class SynSetParser:

    @staticmethod
    def parse(n: str) -> SynSetParsed:
        name = make_label_from_camel_case(n)
        return SynSetParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: SynSetParsed) -> SynSet:
        try:
            synset = SynSet.objects.get(slug=nt.slug)
            synset.name = nt.name
            synset.save()
        except ObjectDoesNotExist:
            synset = SynSet.objects.create(name=nt.name, slug=nt.slug)
        return synset
