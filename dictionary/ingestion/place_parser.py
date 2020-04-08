from typing import Dict

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from dictionary.models import Place, PlaceParsed


class PlaceParser:

    @staticmethod
    def parse(d: Dict) -> PlaceParsed:
        try:
            name = d["name"]
            full_name = d.get("full_name")
            nt = PlaceParsed(
                latitude=d.get("latitude"),
                longitude=d.get("longitude"),
                full_name=full_name if full_name else name,
                name=name,
                slug=d["slug"]
            )
        except Exception as e:
            raise KeyError(f"Place parse of {d} failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: PlaceParsed) -> Place:
        try:
            place = Place.objects.get(slug=nt.slug)
            place.name = nt.name
            place.full_name = nt.full_name
            if nt.latitude and nt.longitude:
                place.latitude = nt.latitude
                place.longitude = nt.longitude
            place.save()
        except MultipleObjectsReturned as e:
            print(nt.slug, e)
            raise
        except ObjectDoesNotExist:
            place = Place.objects.create(slug=nt.slug, name=nt.name, full_name=nt.full_name, latitude=nt.latitude, longitude=nt.longitude)
        return place
