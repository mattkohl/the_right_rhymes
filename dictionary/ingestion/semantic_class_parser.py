from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import SemanticClassParsed, SemanticClass
from dictionary.utils import make_label_from_camel_case, slugify


class SemanticClassParser:

    @staticmethod
    def parse(n: str) -> SemanticClassParsed:
        name = make_label_from_camel_case(n)
        return SemanticClassParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: SemanticClassParsed):
        try:
            semantic_class = SemanticClass.objects.get(slug=nt.slug)
            semantic_class.name = nt.name
            semantic_class.save()
        except ObjectDoesNotExist:
            semantic_class = SemanticClass.objects.create(slug=nt.slug, name=nt.name)
        return semantic_class
