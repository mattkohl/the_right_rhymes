from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from dictionary.sitemaps import EntrySitemap, ArtistSitemap, SongSitemap

sitemaps = {
    "entries": EntrySitemap,
    "artists": ArtistSitemap,
    "songs": SongSitemap
}


urlpatterns = [

    path("", views.index, name="dictionary_index"),
    path("statistics/", views.stats, name="stats"),
    path("search/", views.search, name="search"),
    path("about-the-right-rhymes/", views.about, name="about"),
    path("index/", views.a_to_z, name="a_to_z"),
    path("random/", views.random_entry, name="random_entry"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("semantic-classes/", views.semantic_classes, name="semantic_classes"),
    path("domains/", views.domains, name="domains"),
    path("regions/", views.regions, name="regions"),

    path("<slug:headword_slug>/", views.entry, name="entry"),
    path("artists/<str:artist_slug>/", views.artist, name="artist"),
    path("domains/<slug:domain_slug>/", views.domain, name="domain"),
    path("regions/<slug:region_slug>/", views.region, name="region"),
    path("entities/<str:entity_slug>/", views.entity, name="entity"),
    path("places/<str:place_slug>/", views.place, name="place"),
    path("rhymes/<str:rhyme_slug>/", views.rhyme, name="rhyme"),
    path("semantic-classes/<slug:semantic_class_slug>/", views.semantic_class, name="semantic_class"),
    path("senses/<slug:sense_id>/timeline/", views.sense_timeline, name="sense_timeline"),
    path("songs/<str:song_slug>/", views.song, name="song")

]

