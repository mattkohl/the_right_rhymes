from unittest import mock
from django.test import TestCase
from dictionary.models import Artist, Example


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

    def test_artist_network(self):
        result = self.client.get("/data/artists/epmd/network")

    @mock.patch('dictionary.utils.check_for_image')
    def test_artists_get(self, mock_check_for_image):
        mock_check_for_image.return_value = 'some_image.png'
        result = self.client.get("/data/artists/", follow=True)
        expected = {
            'user': 'AnonymousUser',
            'artists': [{'image': 'some_image.png', 'name': 'EPMD', 'slug': 'epmd'}, {'image': 'some_image.png', 'name': 'Method Man', 'slug': 'method-man'}],
            'auth': 'None'
        }
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.json(), expected)

