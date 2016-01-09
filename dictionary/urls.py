__author__ = 'MBK'

from django.conf.urls import url
from django.contrib import admin


from . import views

urlpatterns = [

    # /admin/
    url(r'^admin/', admin.site.urls),

    # /
    url(r'^$', views.index, name="dictionary_index"),

    # /headword-as-a-slug/
    url(r'^(?P<headword_slug>[a-zA-Z0-9\-_#]+)/?$', views.entry, name='entry'),

    # /artist-name-as-a-slug/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_',\(\)]+)/$", views.artist, name='artist'),

    # /named-entity-as-a-slug/
    url(r'^domains/(?P<domain_slug>[a-zA-Z0-9\-_]+)/$', views.domain, name='domain'),

    # /named-entity-as-a-slug/
    url(r'^entities/(?P<entity_slug>[a-zA-Z0-9\-_]+)/$', views.entity, name='entity'),

]