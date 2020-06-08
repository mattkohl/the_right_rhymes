from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),

    path("artists/", views.artists, name="artists"),
    path("artists/missing_metadata/", views.artists_missing_metadata, name="artists_missing_metadata"),
    path("artists/random/", views.random_artist, name="random_artist"),
    path("artists/<str:artist_slug>/", views.artist, name="artist"),
    path("artists/<str:artist_slug>/geojson", views.artist_geojson, name="artist_geojson"),
    path("artists/<str:artist_slug>/network/", views.artist_network, name="artist_network"),
    path("artists/<str:artist_slug>/sense_examples/", views.artist_sense_examples, name="artist_sense_examples"),
    path("artists/<str:artist_slug>/salience/", views.artist_salient_senses, name="artist_salient_senses"),

    path("definitions/<str:headword>/", views.definitions, name="definitions"),

    path("domains/", views.domains, name="domains"),
    path("domains/<slug:domain_slug>/", views.domain, name="domain"),

    path("regions/", views.regions, name="regions"),
    path("regions/<slug:region_slug>/", views.region, name="region"),

    path("entries/random/", views.random_entry, name="random_entry"),
    path("entries/", views.entries, name="entries"),
    path("entries/<slug:entry_slug>/", views.entry, name="entry"),

    path("examples/random/", views.random_example, name="random_example"),

    path("headword_search/", views.headword_search, name="headword_search"),

    path("entities/missing_metadata/", views.named_entities_missing_metadata, name="named_entities_missing_metadata"),

    path("places/", views.places, name="places"),
    path("places/random/", views.random_place, name="random_place"),
    path("places/<slug:place_slug>/", views.place, name="place"),
    path("places/<slug:place_slug>/geojson", views.place_geojson, name="place_geojson"),
    path("places/<slug:place_slug>/artists/", views.place_artists, name="place_artists"),
    path("places/<slug:place_slug>/remaining_examples/", views.remaining_place_examples, name="remaining_place_examples"),

    path("semantic-classes/", views.semantic_classes, name="semantic_classes"),
    path("semantic-classes/<slug:semantic_class_slug>/", views.semantic_class, name="semantic_class"),

    path("senses/", views.senses, name="senses"),
    path("senses/unpublished", views.senses_unpublished, name="senses_unpublished"),
    path("senses/random/", views.random_sense, name="random_sense"),
    path("senses/<slug:sense_id>/", views.sense, name="sense"),
    path("senses/<slug:sense_id>/artists/geojson", views.sense_artists_geojson, name="sense_artists_geojson"),
    path("senses/<slug:sense_id>/artists/", views.sense_artists, name="sense_artists"),
    path("senses/<slug:sense_id>/artists/salience/", views.sense_artists_salience, name="sense_artists_salience"),
    path("senses/<slug:sense_id>/artists/<str:artist_slug>/", views.sense_artist, name="sense_artist"),
    path("senses/<slug:sense_id>/remaining_examples/", views.remaining_sense_examples, name="remaining_sense_examples"),
    path("senses/<slug:sense_id>/timeline/", views.sense_timeline, name="sense_timeline"),

    path("songs/random/", views.random_song, name="random_song"),
    path("songs/<str:song_slug>/artist_network/", views.song_artist_network, name="song_artist_network"),
    path("songs/<str:song_slug>/release_date_tree/", views.song_release_date_tree, name="song_release_date_tree"),

]
