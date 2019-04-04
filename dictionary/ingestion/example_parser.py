from collections import OrderedDict
from typing import Dict

from dictionary.management.commands.xml_handler import clean_up_date
from dictionary.models import ExampleParsed, Example
from dictionary.utils import slugify


class ExampleParser:

    @staticmethod
    def parse(d: Dict) -> ExampleParsed:
        try:
            artist_name = d['artist']['#text'] if isinstance(d['artist'], OrderedDict) else d['artist']
            nt = ExampleParsed(
                artist_name=artist_name,
                artist_slug=slugify(artist_name),
                song_title=d['songTitle'],
                release_date=clean_up_date(d['date']),
                release_date_string=d['date'],
                album=d['album'],
                lyric_text=d['lyric']['text'],
                xml_id=d["@id"]
            )
        except Exception as e:
            raise KeyError(f"Example parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: ExampleParsed):
        example, _ = Example.objects.get_or_create(song_title=nt.song_title,
                                                   artist_name=nt.artist_name,
                                                   release_date=nt.release_date,
                                                   release_date_string=nt.release_date_string,
                                                   album=nt.album,
                                                   lyric_text=nt.lyric_text)
        example.artist_slug = nt.artist_slug
        example.save()
        return example
