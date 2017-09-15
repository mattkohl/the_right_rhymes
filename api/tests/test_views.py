from unittest import mock
from django.test import TestCase
from dictionary.models import Artist, Example, Sense


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


