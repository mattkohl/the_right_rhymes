from dictionary.models import DomainParsed, Domain
from dictionary.utils import make_label_from_camel_case, slugify


class DomainParser:

    @staticmethod
    def parse(n: str) -> DomainParsed:
        name = make_label_from_camel_case(n)
        return DomainParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: DomainParsed):
        domain, _ = Domain.objects.get_or_create(slug=nt.slug)
        domain.name = nt.name
        domain.save()
        return domain
