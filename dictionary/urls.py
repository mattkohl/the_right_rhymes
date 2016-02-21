__author__ = 'MBK'

from django.conf.urls import url
from django.contrib import admin


from . import views

urlpatterns = [

    # /admin/
    url(r'^admin/?', admin.site.urls),

    # /
    url(r'^$', views.index, name="dictionary_index"),

    # /statistics/
    url(r"^statistics/$", views.stats, name='stats'),

    # /search-results/
    url(r'^search/$', views.search, name='search'),

    # /search-headwords/
    url(r'^search_headwords/$', views.search_headwords, name='search_headwords'),

    # /about/
    url(r'^about/$', views.about, name='about'),

    # /random/
    url(r'^random/$', views.random_entry, name='random_entry'),

    # /<headword-slug>/
    url(r"^(?P<headword_slug>[a-zA-Z0-9\-_#’']+)/?$", views.entry, name='entry'),

    # /artists/<artist-slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½]+)/$", views.artist, name='artist'),

    # /songs/<song-slug>/
    url(r"^songs/(?P<song_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½]+)/$", views.song, name='song'),

    # /dates/<date-slug>/
    url(r"^dates/(?P<date_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½]+)/$", views.date, name='date'),

    # /senses/<sense_id>/artist_origins/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artist_origins/$", views.sense_artist_origins, name="sense_artist_origins"),

    # /senses/<sense_id>/remaining_examples/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/remaining_examples/$", views.remaining_examples, name="remaining_examples"),

    # /timelines/<sense_id>/
    url(r"^timelines/(?P<sense_id>[a-zA-Z0-9\-_’']+)/$", views.timeline, name='timeline'),

    # /senses/<sense_id>/timeline/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/timeline/$", views.sense_timeline_json, name="sense_timeline_json"),

    # /artist_origins/<artist_slug>/
    url(r"^artist_origins/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.artist_origins, name="artist_origins"),

    # /places/<place-name-slug>/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.place, name='place'),

    # /places/<place-name-slug>/latlng/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/latlng/$", views.place_latlng, name='place_latlng'),

    # /domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /domain_json/<domain-slug>/
    url(r"^domain_json/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain_json, name='domain_json'),

    # /entities/<named-entity-slug>/
    url(r"^entities/(?P<entity_slug>[a-zA-Z0-9\-_'’]+)/$", views.entity, name='entity'),

    # /rhymes/<rhyme-slug>/
    url(r"^rhymes/(?P<rhyme_slug>[a-zA-Z0-9\-_#’']+)/?$", views.rhyme, name='rhyme'),

]

