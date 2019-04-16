from typing import Dict

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
    def persist(nt: FormParsed) -> Form:
        form, _ = Form.objects.get_or_create(slug=nt.slug)
        form.frequency = nt.frequency
        form.save()
        return form

    @staticmethod
    def update_relations(form: Form) -> (Form, FormRelations):
        _ = FormParser.purge_relations(form)
        relations = FormRelations(
            parent_entry=[]
        )
        return form, relations

    @staticmethod
    def purge_relations(form: Form) -> Form:
        form.parent_entry.clear()
        return form
