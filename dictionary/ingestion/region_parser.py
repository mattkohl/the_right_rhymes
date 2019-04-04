from dictionary.models import RegionParsed, Region
from dictionary.utils import make_label_from_camel_case, slugify


class RegionParser:

    @staticmethod
    def parse(n: str) -> RegionParsed:
        name = make_label_from_camel_case(n)
        return RegionParsed(name=name, slug=slugify(name))

    @staticmethod
    def persist(nt: RegionParsed):
        region, _ = Region.objects.get_or_create(slug=nt.slug)
        region.name = nt.name
        region.save()
        return region
