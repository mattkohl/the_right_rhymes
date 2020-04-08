from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

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
            domain.name = nt.name
            domain.save()
        except MultipleObjectsReturned as e:
            print(nt.slug, e)
            raise
        except ObjectDoesNotExist:
            domain = Domain.objects.create(slug=nt.slug, name=nt.name)
        return domain
