from django.test import TestCase
from dictionary.models import Entry, Artist, NamedEntity, Song, Domain, Place, Region, SemanticClass, Sense


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
        self.r = Region(slug="west-coast", name="West Coast")
        self.r.save()
        self.ne = NamedEntity(name="foo", slug="foo", entity_type="product", pref_label="Foo", pref_label_slug="foo")
        self.ne.save()
        self.e = Entry(headword="foo", slug="foo", letter="f", publish=True)
        self.e.save()
        self.s = Sense(headword="foo", slug="foo", xml_id="bar", part_of_speech="noun")
        self.s.save()
        self.e.senses.add(self.s)

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

    def test_uses_region_template(self):
        response = self.client.get("/regions/west-coast/")
        self.assertTemplateUsed(response, "dictionary/region.html")

    def test_uses_regions_template(self):
        response = self.client.get("/regions/")
        self.assertTemplateUsed(response, "dictionary/regions.html")

    def test_uses_named_entity_template(self):
        response = self.client.get("/entities/foo/")
        self.assertTemplateUsed(response, "dictionary/named_entity.html")

    def test_uses_entry_template(self):
        response = self.client.get("/foo/")
        self.assertTemplateUsed(response, "dictionary/entry.html")

    def test_random_uses_entry_template(self):
        response = self.client.get("/random/")
        self.assertRedirects(response, '/foo')

    def test_uses_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "dictionary/index.html")

    def test_uses_rhymes_template(self):
        response = self.client.get("/rhymes/foo/")
        self.assertTemplateUsed(response, "dictionary/rhyme.html")

    def test_uses_search_template(self):
        response = self.client.get("/search/?q=test")
        self.assertTemplateUsed(response, "dictionary/search_results.html")

