from django.conf.urls import url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from . import views
from dictionary.sitemaps import EntrySitemap, ArtistSitemap, SongSitemap

sitemaps = {
    'entries': EntrySitemap,
    'artists': ArtistSitemap,
    'songs': SongSitemap
}


urlpatterns = [

    # /
    url(r'^$', views.index, name="dictionary_index"),

    # /statistics/
    url(r"^statistics/$", views.stats, name='stats'),

    # /search-results/
    url(r'^search/$', views.search, name='search'),

    # /about/
    url(r'^about-the-right-rhymes/$', views.about, name='about'),

    # /index/
    url(r'^index/$', views.a_to_z, name='a_to_z'),

    # /random/
    url(r'^random/$', views.random_entry, name='random_entry'),

    # /sitemap.xml
    # url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # /semantic-classes/
    url(r"^semantic\-classes/$", views.semantic_classes, name='semantic_classes'),

    # /domains/
    url(r"^domains/$", views.domains, name='domains'),

    # /regions/
    url(r"^regions/$", views.regions, name='regions'),

    # /<headword-slug>/
    url(r"^(?P<headword_slug>[a-zA-Z0-9\-_#’']+)/?$", views.entry, name='entry'),

    # /artists/<artist-slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!\*ōé½@áó]+)/$", views.artist, name='artist'),

    # /domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /regions/<region-slug>/
    url(r"^regions/(?P<region_slug>[a-zA-Z0-9\-_’']+)/$", views.region, name='region'),

    # /entities/<named-entity-slug>/
    url(r"^entities/(?P<entity_slug>[a-zA-Z0-9\-_'’]+)/$", views.entity, name='entity'),

    # /places/<place-name-slug>/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)–]+)/$", views.place, name='place'),

    # /rhymes/<rhyme-slug>/
    url(r"^rhymes/(?P<rhyme_slug>[a-zA-Z0-9\-_#’'éō]+)/?$", views.rhyme, name='rhyme'),

    # /semantic-classes/<semantic-class-slug>/
    url(r"^semantic\-classes/(?P<semantic_class_slug>[a-zA-Z0-9\-_’']+)/$", views.semantic_class, name='semantic_class'),

    # /senses/<sense_id>/timeline/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/timeline/$", views.sense_timeline, name='sense_timeline'),

    # /songs/<song-slug>/
    url(r"^songs/(?P<song_slug>[a-zA-Z0-9\-_'’,\"\{\}\[\]\(\)\+\!\*ōóéáñ½#%´=@\^\|]+)/$", views.song, name='song')

]

