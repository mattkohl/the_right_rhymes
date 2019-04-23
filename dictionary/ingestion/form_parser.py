from typing import Dict, Tuple

from django.core.exceptions import ObjectDoesNotExist

from dictionary.models import FormParsed, Form, FormRelations
from dictionary.utils import slugify


class FormParser:

    @staticmethod
    def parse(d: Dict) -> FormParsed:
        try:
            label, freq = d['form'][0]['#text'], d["form"][0]["@freq"]
            nt = FormParsed(
                slug=slugify(label),
                label=label,
                frequency=int(freq)
            )
        except Exception as e:
            raise KeyError(f"Form parse failed: {e}")
        else:
            return nt

    @staticmethod
    def persist(nt: FormParsed) -> Tuple[Form, FormRelations]:
        try:
            form = Form.objects.get(slug=nt.slug)
        except ObjectDoesNotExist:
            form = Form(slug=nt.slug, frequency=nt.frequency)
            form.save()
            return FormParser.update_relations(form)
        else:
            form.frequency = nt.frequency
            form.save()
        return FormParser.update_relations(form)

    @staticmethod
    def update_relations(form: Form) -> Tuple[Form, FormRelations]:
        _ = FormParser.purge_relations(form)
        relations = FormRelations(
            parent_entry=[]
        )
        return form, relations

    @staticmethod
    def purge_relations(form: Form) -> Form:
        form.parent_entry.clear()
        return form
