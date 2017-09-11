from unittest import mock
from django.test import TestCase
from dictionary.models import Artist, Place


class TestArtistEndpoints(TestCase):

    def setUp(self):
        self.artist = Artist(name="EPMD", slug="epmd")
        self.artist.save()

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
    def test_artists_get(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/", follow=True)
        expected = {
            'user': 'AnonymousUser',
            'artists': [{'image': 'some_image.png', 'name': 'EPMD', 'slug': 'epmd'}],
            'auth': 'None'
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)
