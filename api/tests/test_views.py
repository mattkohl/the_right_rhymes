from django.test import TestCase
from dictionary.models import Artist, Place


class TestArtistEndpoints(TestCase):

    def setUp(self):
        self.artist = Artist(name="EPMD", slug="epmd")
        self.artist.save()

    def test_artist_get(self):
        result = self.client.get("/data/artists/epmd", follow=True)
        self.assertEqual(result.status_code, 200)
