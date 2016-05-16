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

    # /data/domains/
    url(r"^domains/$", views.domains, name='domains'),

    # /domains/<domain-slug>/
    url(r"^domains/(?P<domain_slug>[a-zA-Z0-9\-_’']+)/$", views.domain, name='domain'),

    # /data/places/<place-name-slug>/artists/
    url(r"^places/(?P<place_slug>[a-zA-Z0-9\-_'’,\(\)]+)/artists/$", views.place_artists, name='place_artists'),

    # /data/semantic-classes/
    url(r"^semantic\-classes/$", views.semantic_classes, name='semantic_classes'),

    # /data/semantic-classes/<semantic-class-slug>/
    url(r"^semantic\-classes/(?P<semantic_class_slug>[a-zA-Z0-9\-_’']+)/$", views.semantic_class, name='semantic_class'),



]
