from unittest import mock
from django.test import TestCase
from dictionary.tests.base import BaseTest
from dictionary.models import Artist, Example, Sense, Domain, Region, Entry, Place, SemanticClass


class TestArtistEndpoints(BaseTest):

    @mock.patch('dictionary.utils.check_for_image')
    def test_artist_get(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/epmd", follow=True)
        expected = {
            'user': 'AnonymousUser',
            'artists': [{'image': 'some_image.png', 'name': 'EPMD', 'slug': 'epmd'}],
            'auth': 'None'
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_artist_network(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/epmd/network", follow=True)
        parsed = result.json()
        self.assertIn('size', parsed)
        self.assertIn('children', parsed)
        self.assertIn('name', parsed)
        self.assertTrue(len(parsed['children']) > 0)

    @mock.patch('dictionary.utils.check_for_image')
    def test_artists_no_sense_examples(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/epmd/sense_examples", follow=True)
        expected = {}
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_artists_sense_examples(self, mock_check_for_image):
        self.sense.cites_artists.add(self.epmd)
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/epmd/sense_examples", follow=True)
        expected = {}
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_artists_get(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/", follow=True)
        expected = {
            'user': 'AnonymousUser',
            'artists': [
                {'image': 'some_image.png', 'name': 'EPMD', 'slug': 'epmd'},
                {'image': 'some_image.png', 'name': 'Erick Sermon', 'slug': 'erick-sermon'},
                {'image': 'some_image.png', 'name': 'Method Man', 'slug': 'method-man'}
            ],
            'auth': 'None'
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_artists_missing_metadata(self, mock_check_for_image):
        mock_check_for_image.return_value = '__none.png'
        result = self.client.get("/data/artists/missing_metadata/", follow=True)
        expected = {
            'feat_artists_no_image': [],
            'feat_artists_no_origin': [
                {'name': 'Method Man',
                 'num_cites': 1,
                 'site_link': 'https://example.org/artists/method-man',
                 'slug': 'method-man'},
                {'name': 'Erick Sermon',
                 'num_cites': 0,
                 'site_link': 'https://example.org/artists/erick-sermon',
                 'slug': 'erick-sermon'}
            ],
            'primary_artists_no_image': [],
            'primary_artists_no_origin': [
                {'name': 'Erick Sermon',
                 'num_cites': 1,
                 'site_link': 'https://example.org/artists/erick-sermon',
                 'slug': 'erick-sermon'},
                {'name': 'Method Man',
                 'num_cites': 0,
                 'site_link': 'https://example.org/artists/method-man',
                 'slug': 'method-man'}
            ]
        }
        j = result.json()
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(j, expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_random_artist(self, mock_check_for_image):
        mock_check_for_image.return_value = '__none.png'
        result = self.client.get("/data/artists/random/", follow=True)
        j = result.json()
        self.assertEqual(result.status_code, 200)
        self.assertIn(j['slug'], ['method-man', 'epmd', 'erick-sermon'])

    @mock.patch('dictionary.utils.check_for_image')
    def test_artist_salient_senses(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/epmd/salience", follow=True)
        parsed = result.json()
        self.assertIn('senses', parsed)
        self.assertTrue(len(parsed['senses']) == 0)


class TestDomainEndpoints(TestCase):
    
    def setUp(self):
        self.domain = Domain(name="foo", slug="foo")
        self.domain.save()
        
    def test_domain_get(self):
        result = self.client.get("/data/domains/foo", follow=True)
        expected = {
            'name': "foo",
            'children': [],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)
        
    def test_domains_get(self):
        result = self.client.get("/data/domains", follow=True)
        expected = {
            'name': "Domains",
            'children': [{'word': 'foo', 'weight': 0, 'url': '/domains/foo'}],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)


class TestRegionEndpoints(TestCase):
    def setUp(self):
        self.region = Region(name="foo", slug="foo")
        self.region.save()

    def test_region_get(self):
        result = self.client.get("/data/regions/foo", follow=True)
        expected = {
            'name': "foo",
            'children': [],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    def test_regions_get(self):
        result = self.client.get("/data/regions", follow=True)
        expected = {
            'name': "Regions",
            'children': [{'word': 'foo', 'weight': 0, 'url': '/regions/foo'}],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)


class TestEntry(TestCase):

    def setUp(self):
        self.headwords = ["foo", "bar", "baz"]

        for hw in self.headwords:
            e = Entry(headword=hw, slug=hw, letter=hw[0], publish=True)
            e.save()

    def test_headword_search(self):
        result = self.client.get("/data/headword_search/?term=ba")
        expected = {
            'entries': [
                {'id': 'bar', 'label': 'bar', 'value': 'bar'},
                {'id': 'baz', 'label': 'baz', 'value': 'baz'}
            ]
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    def test_random_entry(self):
        result = self.client.get("/data/entries/random/", follow=True)
        j = result.json()
        self.assertEqual(result.status_code, 200)
        self.assertIn(j['headword'], self.headwords)


class TestExample(TestCase):

    def setUp(self):
        self.example = Example(
            lyric_text="Now, it's time for me, the E, to rock it loco",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title='Brothers From Brentwood L.I.',
            album='Crossover',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.example.save()
        self.artist = Artist(name='EPMD')
        self.artist.save()
        self.example.artist.add(self.artist)

    @mock.patch('dictionary.utils.check_for_image')
    def test_random_example(self, mock_check_for_image):
        mock_check_for_image.return_value = '__none.png'
        result = self.client.get("/data/examples/random/", follow=True)
        j = result.json()
        expected = {
            'album': 'Crossover',
            'featured_artists': [],
            'links': [],
            'primary_artists': [{'image': '__none.png', 'name': 'EPMD', 'slug': ''}],
            'release_date': '1992-07-28',
            'release_date_string': '1992-07-28',
            'text': "Now, it's time for me, the E, to rock it loco",
            'title': 'Brothers From Brentwood L.I.'
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(j, expected)


class TestPlace(TestCase):

    def setUp(self):
        self.place = Place(name="foo", full_name="foo, usa", slug="foo-usa")
        self.place.save()

    def test_place(self):
        result = self.client.get("/data/places/foo-usa", follow=True)
        expected = {
            'places': [
                {'full_name': 'foo, usa', 'name': 'foo', 'slug': 'foo-usa'}
            ]
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    def test_place_artists(self):
        result = self.client.get("/data/places/foo-usa/artists", follow=True)
        expected = {
            'places': [
                {
                    'artists_with_image': [],
                    'artists_without_image': [],
                    'full_name': 'foo, usa',
                    'name': 'foo',
                    'slug': 'foo-usa'}
            ]
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    def test_random_place(self):
        self.place.longitude = 0.1
        self.place.save()
        result = self.client.get("/data/places/random/", follow=True)
        j = result.json()
        expected = {'full_name': 'foo, usa', 'name': 'foo', 'slug': 'foo-usa'}
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(j, expected)


class TestSemanticClassEndpoints(TestCase):

    def setUp(self):
        self.semantic_class = SemanticClass(name="foo", slug="foo")
        self.semantic_class.save()

    def test_semantic_class_get(self):
        result = self.client.get("/data/semantic-classes/foo", follow=True)
        expected = {
            'name': "foo",
            'children': [],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    def test_semantic_classes_get(self):
        result = self.client.get("/data/semantic-classes", follow=True)
        expected = {
            'name': "Semantic Classes",
            'children': [{'word': 'foo', 'weight': 0, 'url': '/semantic-classes/foo'}],
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)


class TestSenseEndpoints(BaseTest):

    def test_remaining_sense_examples(self):
        result = self.client.get("/data/senses/bar/remaining_examples/")
        j = result.json()
        expected = {'examples': [
            {'album': 'Business Never Personal',
             'artist_name': 'EPMD',
             'artist_slug': 'epmd',
             'featured_artists': [],
             'linked_lyric': 'No static, Uncle Sam, I got mad loot',
             'lyric': 'No static, Uncle Sam, I got mad loot',
             'release_date': '1992-07-28',
             'release_date_string': '1992-07-28',
             'song_slug': 'epmd-boon-dox',
             'song_title': 'Boon Dox'}],
          'sense_id': 'bar'}
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(j, expected)
