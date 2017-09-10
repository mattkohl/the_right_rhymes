from django.test import TestCase
from dictionary.models import Entry, Artist, NamedEntity, Song, Domain, Place


class TemplateTests(TestCase):
    def setUp(self):
        self.a = Artist(name="EPMD", slug="epmd")
        self.a.save()
        self.a1 = Artist(name="Erick Sermon", slug="erick-sermon")
        self.a1.save()
        self.p = Place(full_name="Brentwood, New York, USA", slug="brentwood-new-york-usa", name="Brentwood")
        self.p.save()
        self.d = Domain(name="drugs", slug="drugs")
        self.d.save()

    def test_uses_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "dictionary/index.html")

    def test_uses_atoz_template(self):
        response = self.client.get("/index/")
        self.assertTemplateUsed(response, "dictionary/a_to_z.html")
        
    def test_uses_about_template(self):
        response = self.client.get("/about-the-right-rhymes/")
        self.assertTemplateUsed(response, "dictionary/about.html")

    def test_uses_artist_template(self):
        response = self.client.get("/artists/epmd/")
        self.assertTemplateUsed(response, "dictionary/artist.html")

    def test_uses_place_template(self):
        response = self.client.get("/places/brentwood-new-york-usa/")
        self.assertTemplateUsed(response, "dictionary/place.html")

    def test_uses_domain_template(self):
        response = self.client.get("/domains/drugs/")
        self.assertTemplateUsed(response, "dictionary/domain.html")

    def test_uses_domains_template(self):
        response = self.client.get("/domains/")
        self.assertTemplateUsed(response, "dictionary/domains.html")

