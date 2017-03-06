from django.conf.urls import url, include
from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token
from rest_framework import routers
# from rest_framework.authtoken import views as rf_views
from . import views


# for user in User.objects.all():
#     Token.objects.get_or_create(user=user)

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^api-token-auth/', rf_views.obtain_auth_token),

    # /data/artists/
    url(r"^artists/$", views.artists, name='artists'),

    # /data/artists/missing_metadata/
    url(r"^artists/missing_metadata/$", views.artists_missing_metadata, name='artists_missing_metadata'),

    # /data/artists/<artist_slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!\*ōé½@áó]+)/$", views.artist, name="artist"),

    # /data/artists/<artist_slug>/network/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!\*ōé½@áó]+)/network/$", views.artist_network, name="artist_network"),

    # /data/artists/<artist_slug>/sense_examples/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!\*ōé½@áó]+)/sense_examples/$", views.artist_sense_examples, name="artist_sense_examples"),

    # /data/domains/
    url(r"^domains/$", views.domains, name='domains'),

    # /data/domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /data/regions/
    url(r"^regions/$", views.regions, name='regions'),

    # /data/regions/<region-slug>/
    url(r"^regions/(?P<region_slug>[a-zA-Z0-9\-_’']+)/$", views.region, name='region'),

    # /data/entries/random/
    url(r"^entries/random/$", views.random_entry, name='random_entry'),

    # /data/examples/random/
    url(r"^examples/random/$", views.random_example, name='random_example'),

    # /data/headword_search/
    url(r'^headword_search/$', views.headword_search, name='headword_search'),

    # /data/places/<place-name-slug>/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.place, name='place'),

    # /data/places/<place-name-slug>/artists/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/artists/$", views.place_artists, name='place_artists'),

    # /data/places/<place-name-slug>/remaining_examples/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)–]+)/remaining_examples/$", views.remaining_place_examples, name='remaining_place_examples'),

    # /data/semantic-classes/
    url(r"^semantic\-classes/$", views.semantic_classes, name='semantic_classes'),

    # /data/semantic-classes/<semantic-class-slug>/
    url(r"^semantic\-classes/(?P<semantic_class_slug>[a-zA-Z0-9\-_’']+)/$", views.semantic_class, name='semantic_class'),

    # /data/senses/
    url(r"^senses/$", views.senses, name="senses"),

    # /data/senses/<sense_id>/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/$", views.sense, name="sense"),

    # /data/senses/<sense_id>/artists/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artists/$", views.sense_artists, name="sense_artists"),

    # /data/senses/<sense_id>/artists/<artist_slug>/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.sense_artist, name="sense_artist"),

    # /data/senses/<sense_id>/remaining_examples/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/remaining_examples/$", views.remaining_sense_examples, name="remaining_sense_examples"),

    # /data/senses/<sense_id>/timeline/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/timeline/$", views.sense_timeline, name="sense_timeline"),

    # /data/songs/<song-slug>/artist_network/
    url(r"^songs/(?P<song_slug>[a-zA-Z0-9\-_'’,\{\}\[\]\(\)\+\!\*ōóéáñ½#%´=@\^]+)/artist_network/$", views.song_artist_network, name='song_artist_network'),

    # /data/songs/<song-slug>/release_date_tree/
    url(r"^songs/(?P<song_slug>[a-zA-Z0-9\-_'’,\{\}\[\]\(\)\+\!\*ōóéáñ½#%´=@\^]+)/release_date_tree/$", views.song_release_date_tree, name='song_release_date_tree'),

]
