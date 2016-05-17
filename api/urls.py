__author__ = 'MBK'

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from . import views


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),

    # /data/artists/<artist_slug>/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½@áó]+)/$", views.artist, name="artist"),

    # /data/artists/<artist_slug>/sense_examples/
    url(r"^artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)\+\!ōé½@áó]+)/sense_examples/$", views.artist_sense_examples, name="artist_sense_examples"),

    # /data/domains/
    url(r"^domains/$", views.domains, name='domains'),

    # /data/domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /data/places/<place-name-slug>/artists/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/artists/$", views.place_artists, name='place_artists'),

    # /data/places/<place-name-slug>/latlng/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/latlng/$", views.place_latlng, name='place_latlng'),

    # /data/semantic-classes/
    url(r"^semantic\-classes/$", views.semantic_classes, name='semantic_classes'),

    # /data/semantic-classes/<semantic-class-slug>/
    url(r"^semantic\-classes/(?P<semantic_class_slug>[a-zA-Z0-9\-_’']+)/$", views.semantic_class, name='semantic_class'),

    # /data/senses/<sense_id>/artists/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artists/$", views.sense_artists, name="sense_artists"),

    # /data/senses/<sense_id>/artists/<artist_slug>/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/artists/(?P<artist_slug>[a-zA-Z0-9\-_'’,\(\)]+)/$", views.sense_artist, name="sense_artist"),

    # /data/senses/<sense_id>/remaining_examples/
    url(r"^senses/(?P<sense_id>[a-zA-Z0-9_]+)/remaining_examples/$", views.remaining_sense_examples, name="remaining_sense_examples"),




]
