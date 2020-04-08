from typing import Dict

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from dictionary.models import NamedEntity, NamedEntityParsed
from dictionary.utils import slugify


class NamedEntityParser:

    @staticmethod
    def parse(d: Dict) -> NamedEntityParsed:

        name = d['#text']
        pref_label = d['@prefLabel'] if '@prefLabel' in d else name

        return NamedEntityParsed(
            name=name,
            slug=slugify(name),
            entity_type=d["@type"],
            pref_label=pref_label,
            pref_label_slug=slugify(pref_label)
        )

    @staticmethod
    def persist(nt: NamedEntityParsed) -> NamedEntity:
        try:
            named_entity = NamedEntity.objects.get(
                entity_type=nt.entity_type,
                pref_label_slug=nt.pref_label_slug
            )
            named_entity.pref_label = nt.pref_label
            named_entity.slug = nt.slug
            named_entity.name = nt.name
            named_entity.save()
        except MultipleObjectsReturned as e:
            print(nt.entity_type, nt.pref_label_slug, e)
            raise
        except ObjectDoesNotExist:
            named_entity = NamedEntity.objects.create(
                entity_type=nt.entity_type,
                pref_label_slug=nt.pref_label_slug,
                pref_label=nt.pref_label,
                slug=nt.slug,
                name=nt.name
            )
        return named_entity
