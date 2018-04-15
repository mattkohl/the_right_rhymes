from django.test import TestCase
from dictionary.tests.base import BaseTest
from dictionary.models import Artist


class ArtistTest(TestCase):

    def test_default_name(self):
        artist = Artist()
        self.assertEqual(artist.name, None)


class ExampleTest(BaseTest):

    def test_remove_lyric_links(self):
        links = self.example_2.lyric_links.all()
        count = links.count()
        self.assertEqual(count, 3)
        for link in links:
            self.example_2.lyric_links.remove(link)
        self.assertEqual(self.example_2.lyric_links.count(), 0)
