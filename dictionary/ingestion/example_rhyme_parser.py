from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import ExampleRhyme, ExampleRhymeParsed
from dictionary.utils import slugify


class ExampleRhymeParser:

    @staticmethod
    def parse(d: Dict) -> ExampleRhymeParsed:

        if "#text" and "@rhymeTargetWord" not in d:
            print(f"Missing keys from rhyme dict: {d}")

        word_one = d['#text']
        word_one_position = d['@position']
        word_two = d['@rhymeTargetWord']
        word_two_position = d['@rhymeTargetPosition']

        return ExampleRhymeParsed(
            word_one=word_one,
            word_one_slug=slugify(word_one),
            word_one_position=word_one_position,
            word_two=word_two,
            word_two_slug=slugify(word_two),
            word_two_position=word_two_position,
            word_two_target_id=d['@rhymeTarget'] if '@rhymeTarget' in d else None
        )

    @staticmethod
    def persist(nt: ExampleRhymeParsed) -> ExampleRhyme:
        try:
            example_rhyme = ExampleRhyme.objects.get(word_one=nt.word_one, word_two=nt.word_two,
                                                     word_one_position=nt.word_one_position,
                                                     word_two_position=nt.word_two_position)
            example_rhyme.word_one_slug = nt.word_one_slug
            example_rhyme.word_two_slug = nt.word_two_slug
            example_rhyme.word_two_target_id = nt.word_two_target_id
            example_rhyme.save()
        except ObjectDoesNotExist:
            example_rhyme = ExampleRhyme.objects.create(word_one=nt.word_one, word_two=nt.word_two,
                                                        word_one_position=nt.word_one_position,
                                                        word_two_position=nt.word_two_position,
                                                        word_one_slug=nt.word_one_slug,
                                                        word_two_slug=nt.word_two_slug,
                                                        word_two_target_id=nt.word_two_target_id,
                                                        )
        return example_rhyme
