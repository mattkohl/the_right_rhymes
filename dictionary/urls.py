__author__ = 'MBK'

from django.conf.urls import url
from django.contrib import admin

from . import views


urlpatterns = [

    # /
    url(r'^$', views.index, name="dictionary_index"),

    # /admin/
    url(r'^admin/?', admin.site.urls),

    # /statistics/
    url(r"^statistics/$", views.stats, name='stats'),

    # /search-results/
    url(r'^search/$', views.search, name='search'),

    # /about/
    url(r'^about/$', views.about, name='about'),

    # /index/
    url(r'^index/$', views.a_to_z, name='a_to_z'),

    # /random/
    url(r'^random/$', views.random_entry, name='random_entry'),

    # /semantic-classes/
    url(r"^semantic\-classes/$", views.semantic_classes, name='semantic_classes'),

    # /domains/
    url(r"^domains/$", views.domains, name='domains'),

    # /<headword-slug>/
    url(r"^(?P<headword_slug>[a-zA-Z0-9\-_#’']+)/?$", views.entry, name='entry'),

    # /artists/<artist-slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½@áó]+)/$", views.artist, name='artist'),

    # /domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

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
    url(r"^songs/(?P<song_slug>[a-zA-Z0-9\-_'’,\{\}\[\]\(\)\+\!ōóéáñ½#%´=@]+)/$", views.song, name='song')

]

