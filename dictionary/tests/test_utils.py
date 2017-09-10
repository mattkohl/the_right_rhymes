from unittest import mock
from django.test import TestCase
from dictionary.models import Entry, Artist, Collocate, LyricLink, Example, Place, Xref
from dictionary.utils import slugify, extract_short_name, extract_parent, build_example, build_beta_example, add_links, \
    inject_link, swap_place_lat_long, format_suspicious_lat_longs, gather_suspicious_lat_longs, build_entry_preview, \
    build_collocate, build_xref, build_artist, check_for_image


class TestUtils(TestCase):

    def slugify_test(self):
        self.assertEqual(slugify("The Notorious B.I.G."), "notorious-b-i-g--the")

    def test_extract_short_name(self):
        self.assertEqual(extract_short_name("Houston, Texas, USA"), "Houston")

    def test_extract_parent(self):
        self.assertEqual(extract_parent("Houston, Texas, USA"), "Texas, USA")

    def test_build_entry_preview(self):
        e = Entry(headword="headword", slug="headword", pub_date="2017-01-01", last_updated="2017-01-01")
        result = build_entry_preview(e)
        expected = {
            "headword": "headword",
            "slug": "headword",
            "pub_date": "2017-01-01",
            "last_updated": "2017-01-01"
        }
        self.assertDictEqual(result, expected)

    def test_build_collocate(self):
        c = Collocate(
            collocate_lemma="lemma",
            source_sense_xml_id="x1",
            target_slug="target1",
            target_id="target1",
            frequency=1
        )
        result = build_collocate(c)
        expected = {
            "collocate_lemma": "lemma",
            "source_sense_xml_id": "x1",
            "target_slug": "target1",
            "target_id": "target1",
            "frequency": 1
        }
        self.assertDictEqual(result, expected)

    def test_build_xref(self):
        x = Xref(
            xref_word="word",
            xref_type="type",
            target_lemma="target_lemma",
            target_slug="target_slug",
            target_id="target_id",
            frequency=1,
            position=1
        )
        result = build_xref(x)
        expected = {
            "xref_word": "word",
            "xref_type": "type",
            "target_lemma": "target_lemma",
            "target_slug": "target_slug",
            "target_id": "target_id",
            "frequency": 1,
            "position": 1
        }
        self.assertDictEqual(result, expected)


class TestBuildArtist(TestCase):
    def setUp(self):
        self.a = Artist(name='EPMD', slug='epmd')
        self.a.save()
        self.p = Place(name="Brentwood", full_name="Brentwood, New York, USA", slug="brentwood-new-york-usa")
        self.p.save()
        self.a.origin.add(self.p)

    @mock.patch('dictionary.utils.check_for_image')
    def test_build_artist(self, mock_check_for_image):
        mock_check_for_image.return_value = "foo"
        result = build_artist(self.a)
        expected = {
            "name": "EPMD",
            "slug": "epmd",
            "image": "foo"
        }
        self.assertDictEqual(result, expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_build_artist_require_origin(self, mock_check_for_image):
        mock_check_for_image.return_value = "foo"
        result = build_artist(Artist(name="name", slug="slug"), True)
        self.assertIsNone(result)


class TestBuildSense(TestCase):
    pass


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
        self.a.save()
        self.e.artist.add(self.a)
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
        self.published = ['rock', 'loco',]

    @mock.patch('dictionary.utils.add_links')
    def test_build_example(self, mock_add_links):
        mock_add_links.return_value = "foo"
        built = build_example(self.e, self.published)
        expected = {
            'featured_artists': [],
            'album': 'Crossover',
            'release_date': '1992-07-28',
            'linked_lyric': 'foo',
            'release_date_string': '1992-07-28',
            'lyric': "Now, it's time for me, the E, to rock it loco",
            'artist_slug': 'EPMD',
            'artist_name': 'EPMD',
            'song_slug': 'epmd-brothers-from-brentwood-l-i',
            'song_title': 'Brothers From Brentwood L.I.'
        }
        self.assertDictEqual(built, expected)

    @mock.patch('dictionary.utils.build_artist')
    def test_build_beta_example(self, mock_build_artist):
        mock_build_artist.return_value = {'foo': 'bar'}
        result = build_beta_example(self.e)
        expected = {
            'featured_artists': [],
            'links': [
                {'target_lemma': 'E',
                 'text': 'E',
                 'type': 'artist',
                 'target_slug': 'erick-sermon',
                 'offset': 27
                 },
                {'target_lemma': 'rock',
                 'text': 'rock',
                 'type': 'xref',
                 'target_slug': 'rock#e9060_trV_1',
                 'offset': 33
                 },
                {'target_lemma': 'loco',
                 'text': 'loco',
                 'type': 'xref',
                 'target_slug': 'loco#e7360_adv_1',
                 'offset': 41}
            ],
            'album': 'Crossover',
            'text': "Now, it's time for me, the E, to rock it loco",
            'release_date': '1992-07-28',
            'release_date_string': '1992-07-28',
            'primary_artists': [{"foo": "bar"}],
            'title': 'Brothers From Brentwood L.I.'
        }
        self.assertDictEqual(result, expected)

    def test_add_links(self):
        lyric_links = self.e.lyric_links.order_by('position')
        result = add_links(self.e.lyric_text, lyric_links, self.published)
        expected = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it <a href="/loco#e7360_adv_1">loco</a>"""
        self.assertEqual(result, expected)

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