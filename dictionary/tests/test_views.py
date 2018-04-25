from dictionary.tests.base import BaseTest


class TemplateTests(BaseTest):

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
        response = self.client.get("/entities/oprah-winfrey/")
        self.assertTemplateUsed(response, "dictionary/named_entity.html")

    def test_uses_entry_template(self):
        response = self.client.get("/mad/")
        self.assertTemplateUsed(response, "dictionary/entry.html")

    def test_random_uses_entry_template(self):
        response = self.client.get("/random/")
        self.assertEqual(response.status_code, 302)

    def test_uses_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "dictionary/index.html")

    def test_uses_rhyme_template(self):
        response = self.client.get("/rhymes/foo/")
        self.assertTemplateUsed(response, "dictionary/rhyme.html")

    def test_uses_search_template(self):
        response = self.client.get("/search/?q=test")
        self.assertTemplateUsed(response, "dictionary/search_results.html")

    def test_uses_semantic_class_template(self):
        response = self.client.get("/semantic-classes/drugs/")
        self.assertTemplateUsed(response, "dictionary/semantic_class.html")

    def test_uses_semantic_classes_template(self):
        response = self.client.get("/semantic-classes/")
        self.assertTemplateUsed(response, "dictionary/semantic_classes.html")

    def test_uses_timeline_template(self):
        response = self.client.get("/senses/bar/timeline/")
        self.assertTemplateUsed(response, "dictionary/_timeline.html")

    def test_uses_song_template(self):
        response = self.client.get("/songs/erick-sermon-foo/")
        self.assertTemplateUsed(response, "dictionary/song.html")

    def test_uses_stats_template(self):
        response = self.client.get("/statistics/")
        self.assertTemplateUsed(response, "dictionary/stats.html")

    def test_uses_search_template_with_form(self):
        response = self.client.get("/search/?q=madder")
        self.assertRedirects(response, "/mad/")

