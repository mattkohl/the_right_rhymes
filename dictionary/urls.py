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
    url(r"^statistics/?$", views.stats, name='stats'),

    # /search-results/
    url(r'^search/$', views.search, name='search'),

    # /<headword-slug>/
    url(r"^(?P<headword_slug>[a-zA-Z0-9\-_#’']+)/?$", views.entry, name='entry'),

    # /artists/<artist-slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.artist, name='artist'),

    # /senses/<sense_id>/artist_origins/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artist_origins/$", views.sense_artist_origins, name="sense_artist_origins"),

    # /artist_origins/<artist_slug>/
    url(r"^artist_origins/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.artist_origins, name="artist_origins"),

    # /places/<place-name-slug>/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.place, name='place'),

    # /domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /entities/<named-entity-slug>/
    url(r"^entities/(?P<entity_slug>[a-zA-Z0-9\-_'’]+)/$", views.entity, name='entity'),

]

