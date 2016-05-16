import json
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import generics
from dictionary.models import SemanticClass, Domain, Place
from dictionary.utils import collect_place_artists
import api.serializers as serializers


class SemanticClassesAPI(generics.ListCreateAPIView):
    queryset = SemanticClass.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    serializer_class = serializers.SemanticClassSerializer


@api_view(('GET',))
def domain(request, domain_slug):
    results = Domain.objects.filter(slug=domain_slug)
    if results:
        domain_object = results[0]
        senses = domain_object.senses.annotate(num_examples=Count('examples')).order_by('num_examples')
        data = {
            'name': domain_object.name,
            'children': [
                {
                    'word': sense.headword,
                    'weight': sense.num_examples,
                    'url': '/' + sense.slug + '#' + sense.xml_id
                } for sense in senses
                ]
            }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def domains(request):
    results = Domain.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    if results:
        data = {
            'name': "Domains",
            'children': [
                    {
                        'word': domain.name,
                        'weight': domain.num_senses,
                        'url': '/domains/' + domain.slug
                    } for domain in results
                ]
            }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def place_artists(request, place_slug):
    place = Place.objects.filter(slug=place_slug)[0]
    artists = collect_place_artists(place, [])
    artists_with_image = [artist for artist in artists if '__none.png' not in artist['image']]
    artists_without_image = [artist for artist in artists if '__none.png' in artist['image']]

    if artists_with_image or artists_without_image:
        data = {
            'artists_with_image': artists_with_image,
            'artists_without_image': artists_without_image,
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def semantic_class(request, semantic_class_slug):
    results = SemanticClass.objects.filter(slug=semantic_class_slug)
    if results:
        semantic_class_object = results[0]
        data = {
            'name': semantic_class_object.name,
            'children': [
                    {
                        'word': sense.headword,
                        'weight': sense.examples.count(),
                        'url': '/' + sense.slug + '#' + sense.xml_id
                    } for sense in semantic_class_object.senses.all()
                ]
            }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def semantic_classes(request):
    results = SemanticClass.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    if results:
        data = {
            'name': "Semantic Classes",
            'children': [
                    {
                        'word': semantic_class.name,
                        'weight': semantic_class.num_senses,
                        'url': '/semantic-classes/' + semantic_class.slug
                    } for semantic_class in results
                ]
            }
        return Response(data)
    else:
        return Response({})