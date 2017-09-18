from unittest import mock
from django.test import TestCase
from dictionary.tests.base import BaseTest
from dictionary.models import Artist, Place
from dictionary.utils import slugify, extract_short_name, extract_parent, build_example, build_beta_example, add_links, \
    inject_link, swap_place_lat_long, format_suspicious_lat_longs, gather_suspicious_lat_longs, build_entry_preview, \
    build_collocate, build_xref, build_artist, build_sense, build_timeline_example, reduce_ordered_list, \
    count_place_artists, make_label_from_camel_case, dedupe_rhymes


class TestUtils(BaseTest):

    def slugify_test(self):
        self.assertEqual(slugify("The Notorious B.I.G."), "notorious-b-i-g--the")

    def test_extract_short_name(self):
        self.assertEqual(extract_short_name("Houston, Texas, USA"), "Houston")

    def test_extract_parent(self):
        self.assertEqual(extract_parent("Houston, Texas, USA"), "Texas, USA")

    def test_build_entry_preview(self):
        result = build_entry_preview(self.mad_entry)
        self.assertEqual(result['headword'], 'mad')

    def test_build_collocate(self):
        result = build_collocate(self.collocate)
        expected = {
            "collocate_lemma": "lemma",
            "source_sense_xml_id": "x1",
            "target_slug": "target1",
            "target_id": "target1",
            "frequency": 1
        }
        self.assertDictEqual(result, expected)

    def test_build_xref(self):
        result = build_xref(self.xref)
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

    def test_reduce_ordered_list(self):
        ol = list("abcdeabcdefghabcdefghijkijkabcdeabcdefghijkfghijk")
        threshold = 20
        reduced = reduce_ordered_list(ol, threshold)
        self.assertTrue(len(list(reduced)) < len(ol))

    def test_count_place_artists(self):
        result = count_place_artists(self.brentwood_place, [0])
        self.assertGreater(result, 0)

    def test_make_label_from_camel_case(self):
        pass

    def test_dedupe_rhymes(self):
        pass


class TestBuildArtist(BaseTest):

    @mock.patch('dictionary.utils.check_for_image')
    def test_build_artist(self, mock_check_for_image):
        mock_check_for_image.return_value = "foo"
        result = build_artist(self.epmd)
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


class TestBuildSense(BaseTest):
    @mock.patch('dictionary.utils.build_example')
    def test_build_sense(self, mock_build_example):
        mock_build_example.return_value = {"example": "example"}
        built = build_sense(self.mad_sense, self.published_headwords)
        expected = {'xml_id': 'bar', 'collocates': [], 'regions': [], 'etymology': None, 'semantic_classes': [], 'antonyms': [], 'ancestors': [], 'artist_name': '', 'artist_slug': '', 'sense_image': None, 'holonyms': [], 'related_words': [], 'image': '', 'examples': [{'example': 'example'}, {'example': 'example'}, {'example': 'example'}], 'form': None, 'part_of_speech': 'adj', 'instance_of': [], 'definition': None, 'num_examples': 4, 'meronyms': [], 'notes': None, 'rhymes': [], 'related_concepts': [], 'instances': [], 'derivatives': [], 'synonyms': [], 'headword': 'mad', 'domains': []}
        self.assertDictEqual(built, expected)


class TestBuildExample(BaseTest):

    @mock.patch('dictionary.utils.add_links')
    @mock.patch('dictionary.utils.check_for_image')
    def test_build_example(self, mock_check_for_image, mock_add_links):
        mock_add_links.return_value = "foo"
        mock_check_for_image.return_value = "__none.png"
        built = build_example(self.example_2, self.published_headwords)
        expected = {'lyric': "Now, it's time for me, the E, to rock it loco", 'featured_artists': [], 'song_title': 'Brothers From Brentwood L.I.', 'artist_name': 'EPMD', 'release_date_string': '1992-07-28', 'release_date': '1992-07-28', 'linked_lyric': 'foo', 'album': 'Crossover', 'artist_slug': 'epmd', 'song_slug': 'epmd-brothers-from-brentwood-l-i'}
        self.assertDictEqual(built, expected)

    @mock.patch('dictionary.utils.build_artist')
    def test_build_beta_example(self, mock_build_artist):
        mock_build_artist.return_value = {'foo': 'bar'}
        result = build_beta_example(self.example_2)
        expected = {'links': [{'offset': 27, 'target_lemma': 'E', 'target_slug': 'erick-sermon', 'type': 'artist', 'text': 'E'}, {'offset': 33, 'target_lemma': 'rock', 'target_slug': 'rock#e9060_trV_1', 'type': 'xref', 'text': 'rock'}, {'offset': 41, 'target_lemma': 'loco', 'target_slug': 'loco#e7360_adv_1', 'type': 'xref', 'text': 'loco'}], 'text': "Now, it's time for me, the E, to rock it loco", 'title': 'Brothers From Brentwood L.I.', 'primary_artists': [{'foo': 'bar'}], 'album': 'Crossover', 'release_date_string': '1992-07-28', 'featured_artists': [], 'release_date': '1992-07-28'}
        self.assertDictEqual(result, expected)

    def test_add_links(self):
        lyric_links = self.example_2.lyric_links.order_by('position')
        result = add_links(self.example_2.lyric_text, lyric_links, self.published_headwords)
        expected = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it <a href="/loco#e7360_adv_1">loco</a>"""
        self.assertEqual(result, expected)

    def test_inject_link(self):
        lyric = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it loco"""
        start, end = 109, 113
        a = """<a href="/loco#e7360_adv_1">loco</a>"""
        result = inject_link(lyric, start, end, a)
        expected = """Now, it's time for me, the <a href="/artists/erick-sermon">E</a>, to <a href="/rock#e9060_trV_1">rock</a> it <a href="/loco#e7360_adv_1">loco</a>"""
        self.assertEqual(result, expected)

    @mock.patch('dictionary.utils.add_links')
    @mock.patch('dictionary.utils.check_for_image')
    def test_build_timeline_example(self, mock_check_for_image, mock_add_links):
        mock_add_links.return_value = "foo"
        mock_check_for_image.return_value = "__none.png"
        built = build_timeline_example(self.example_2, self.published_headwords)
        expected = {'background': {'url': '__none.png'}, 'start_date': {'month': '07', 'day': '28', 'year': '1992'}, 'media': {'thumbnail': '__none.png'}, 'text': {'headline': 'foo', 'text': '<a href="/artists/epmd">EPMD</a> - "<a href="/songs/epmd-brothers-from-brentwood-l-i">Brothers From Brentwood L.I.</a>"'}}
        self.assertDictEqual(built, expected)


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