from django.test import TestCase


class TemplateTests(TestCase):

    def test_uses_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "dictionary/index.html")

    def test_uses_atoz_template(self):
        response = self.client.get("/index/")
        self.assertTemplateUsed(response, "dictionary/a_to_z.html")
        
    def test_uses_about_template(self):
        response = self.client.get("/about-the-right-rhymes/")
        self.assertTemplateUsed(response, "dictionary/about.html")
