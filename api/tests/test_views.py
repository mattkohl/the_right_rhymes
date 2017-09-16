from unittest import mock
from django.test import TestCase
from dictionary.models import Artist, Example, Sense, Domain, Region, Entry, Place


class TestArtistEndpoints(TestCase):

    def setUp(self):
        self.example = Example(
            lyric_text="I must go hard, then take charge",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title="Never Defeat 'Em",
            album='We Mean Business',
            release_date='2008-12-09',
            release_date_string='2008-12-09'
        )
        self.example.save()
        self.epmd = Artist(name='EPMD', slug="epmd")
        self.epmd.save()
        self.example.artist.add(self.epmd)
        self.method_man = Artist(name="Method Man", slug="method-man")
        self.method_man.save()
        self.example.feat_artist.add(self.method_man)
        self.sense = Sense(headword="headword", part_of_speech="noun", xml_id="foo", slug="headword")
        self.sense.save()

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
            'primary_artists_no_image': [],
            'primary_artists_no_origin': [
                {'site_link': 'https://example.org/artists/epmd', 'slug': 'epmd', 'num_cites': 1, 'name': 'EPMD'},
                {'site_link': 'https://example.org/artists/method-man', 'slug': 'method-man', 'num_cites': 0, 'name': 'Method Man'}
            ],
            'feat_artists_no_image': [],
            'feat_artists_no_origin': [
                {'site_link': 'https://example.org/artists/method-man', 'slug': 'method-man', 'num_cites': 1, 'name': 'Method Man'},
                {'site_link': 'https://example.org/artists/epmd', 'slug': 'epmd', 'num_cites': 0, 'name': 'EPMD'}
            ]
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

    @mock.patch('dictionary.utils.check_for_image')
    def test_random_artist(self, mock_check_for_image):
        mock_check_for_image.return_value = '__none.png'
        result = self.client.get("/data/artists/random/", follow=True)
        j = result.json()
        self.assertEqual(result.status_code, 200)
        self.assertIn(j['slug'], ['method-man', 'epmd'])


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

    def test_headword_views(self):
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