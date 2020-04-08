from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from dictionary.models import RegionParsed, Region
from dictionary.utils import make_label_from_camel_case, slugify


class RegionParser:

    @staticmethod
    def parse(n: str) -> RegionParsed:
        name = make_label_from_camel_case(n)
        return RegionParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: RegionParsed):
        try:
            region = Region.objects.get(slug=nt.slug)
            region.name = nt.name
            region.save()
        except MultipleObjectsReturned as e:
            print(nt.slug, e)
            raise
        except ObjectDoesNotExist:
            region = Region.objects.create(slug=nt.slug, name=nt.name)
        return region
