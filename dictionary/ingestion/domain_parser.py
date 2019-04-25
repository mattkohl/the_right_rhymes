from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import DomainParsed, Domain
from dictionary.utils import make_label_from_camel_case, slugify


class DomainParser:

    @staticmethod
    def parse(n: str) -> DomainParsed:
        name = make_label_from_camel_case(n)
        return DomainParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: DomainParsed):
        try:
            domain = Domain.objects.get(slug=nt.slug)
        except ObjectDoesNotExist:
            domain = Domain(slug=nt.slug, name=nt.name)
            domain.save()
            return domain
        else:
            domain.name = nt.name
            domain.save()
            return domain
