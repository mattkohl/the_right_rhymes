from dictionary.models import SemanticClassParsed, SemanticClass
from dictionary.utils import make_label_from_camel_case, slugify


class SemanticClassParser:

    @staticmethod
    def parse(n: str) -> SemanticClassParsed:
        name = make_label_from_camel_case(n)
        return SemanticClassParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: SemanticClassParsed):
        semantic_class, _ = SemanticClass.objects.get_or_create(slug=nt.slug)
        semantic_class.name = nt.name
        semantic_class.save()
        return semantic_class
