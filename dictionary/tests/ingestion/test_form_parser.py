from dictionary.ingestion.form_parser import FormParser
from dictionary.models import Form
from dictionary.tests.base import BaseXMLParserTest


class TestFormParser(BaseXMLParserTest):

    def test_parse(self):
        result = FormParser.parse(self.zootie_form_dict1)
        self.assertEqual(result, self.zootie_form_nt1)

    def test_persist(self):
        result, relations = FormParser.persist(self.zootie_form_nt1)
        form = Form.objects.get(slug="zootie")
        self.assertEqual(result, form)
