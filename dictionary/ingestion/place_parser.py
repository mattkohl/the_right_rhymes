from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import Place, PlaceParsed


class PlaceParser:

    @staticmethod
    def parse(d: Dict) -> PlaceParsed:
        try:
            nt = PlaceParsed(
                latitude=d.get("latitude"),
                longitude=d.get("longitude"),
                name=d["name"],
                slug=d["slug"]
            )
        except Exception as e:
            raise KeyError(f"Sense parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: PlaceParsed) -> Place:
        try:
            place = Place.objects.get(slug=nt.slug)
            place.name = nt.name
            if nt.latitude and nt.longitude:
                place.latitude = nt.latitude
                place.longitude = nt.longitude
            place.save()
        except ObjectDoesNotExist:
            place = Place.objects.create(slug=nt.slug, name=nt.name, latitude=nt.latitude, longitude=nt.longitude)
        return place
