from django.contrib.sitemaps import Sitemap

from dictionary.models import Entry, Artist, Song


class EntrySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Entry.objects.filter(publish=True)

    def lastmod(self, obj):
        return obj.pub_date


class ArtistSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Artist.objects.all()


class SongSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Song.objects.all()