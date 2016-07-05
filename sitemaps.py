from django.contrib.sitemaps import Sitemap
from dictionary.models import Entry


class DictionarySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Entry.objects.all()