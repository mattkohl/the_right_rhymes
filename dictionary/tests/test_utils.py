from django.test import TestCase
from dictionary.models import Entry
from dictionary.utils import slugify, extract_short_name, extract_parent, build_example, add_links, inject_link


class TestUtils(TestCase):

    def slugify_test(self):
        self.assertEqual(slugify("The Notorious B.I.G."), "notorious-b-i-g--the")

    def test_extract_short_name(self):
        self.assertEqual(extract_short_name("Houston, Texas, USA"), "Houston")

    def test_extract_parent(self):
        self.assertEqual(extract_parent("Houston, Texas, USA"), "Texas, USA")

    def test_build_example(self):
        pass

    def test_add_links(self):
        pass

    def test_inject_link(self):
        lyric = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it loco"""
        start, end = 109, 113
        a = """<a href="/loco#e7360_adv_1">loco</a>"""
        result = inject_link(lyric, start, end, a)
        expected = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it <a href="/loco#e7360_adv_1">loco</a>"""
        self.assertEqual(result, expected)