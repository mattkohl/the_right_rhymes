from django.test import TestCase
from dictionary.models import Entry, Artist, Song, LyricLink, Example, Place
from dictionary.utils import slugify, extract_short_name, extract_parent, build_example, add_links, \
    inject_link, swap_place_lat_long, format_suspicious_lat_longs, gather_suspicious_lat_longs


class TestUtils(TestCase):

    def slugify_test(self):
        self.assertEqual(slugify("The Notorious B.I.G."), "notorious-b-i-g--the")

    def test_extract_short_name(self):
        self.assertEqual(extract_short_name("Houston, Texas, USA"), "Houston")

    def test_extract_parent(self):
        self.assertEqual(extract_parent("Houston, Texas, USA"), "Texas, USA")


class TestBuildExample(TestCase):

    def setUp(self):
        self.e = Example(
            lyric_text="Now, it's time for me, the E, to rock it loco",
            artist_name='EPMD',
            artist_slug='EPMD',
            song_title='Brothers From Brentwood L.I.',
            album='Crossover',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.e.save()
        self.a = Artist(name='EMPD')
        self.l1 = LyricLink(
            link_text="E",
            link_type="artist",
            position=27,
            target_lemma="E",
            target_slug="erick-sermon"
        )
        self.l2 = LyricLink(
            link_text='loco',
            link_type='xref',
            position=41,
            target_lemma='loco',
            target_slug='loco#e7360_adv_1'
        )
        self.l3 = LyricLink(
            link_text='rock',
            link_type='xref',
            position=33,
            target_lemma='rock',
            target_slug='rock#e9060_trV_1'
        )
        self.l1.save()
        self.l2.save()
        self.l3.save()
        self.e.lyric_links.add(self.l1)
        self.e.lyric_links.add(self.l2)
        self.e.lyric_links.add(self.l3)

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


class TestPlaceMgmtUtils(TestCase):

    def setUp(self):
        self.lat = -1.23
        self.lng = 2.34
        self.p = Place(name="test", slug="test-usa", latitude=self.lat, longitude=self.lng)
        self.p.save()

    def test_swap_place_lat_long(self):

        swap_place_lat_long(self.p)
        self.assertEqual(self.p.latitude, self.lng)
        self.assertEqual(self.p.longitude, self.lat)

    def test_format_suspicious_lat_longs(self):
        results = format_suspicious_lat_longs([self.p])
        self.assertEqual(results[0], '0 -1.23\t2.34\ttest-usa')

    def test_gather_suspicious_lat_longs(self):
        suspects = gather_suspicious_lat_longs()
        self.assertEqual(suspects.count(), 1)
        self.assertEqual(suspects.first(), self.p)