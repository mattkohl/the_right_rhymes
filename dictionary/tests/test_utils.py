from django.test import TestCase
from dictionary.utils import slugify, extract_short_name, extract_parent


class TestUtils(TestCase):

    def slugify_test(self):
        self.assertEqual(slugify("The Notorious B.I.G."), "notorious-b-i-g--the")

    def test_extract_short_name(self):
        self.assertEqual(extract_short_name("Houston, Texas, USA"), "Houston")

    def test_extract_parent(self):
        self.assertEqual(extract_parent("Houston, Texas, USA"), "Texas, USA")

