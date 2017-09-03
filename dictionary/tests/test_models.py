from django.test import TestCase
from dictionary.models import Artist


class ArtistTest(TestCase):

    def test_default_name(self):
        artist = Artist()
        self.assertEqual(artist.name, None)

