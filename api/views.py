from operator import itemgetter
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dictionary.models import Artist, Domain, Entry, NamedEntity, Place, SemanticClass, Sense
from dictionary.utils import build_artist, build_example, build_place_latlng, \
    collect_place_artists
from dictionary.views import NUM_ARTISTS_TO_SHOW, NUM_QUOTS_TO_SHOW


@api_view(('GET',))
def artist(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        data = {'places': [build_artist(artist) for artist in results]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def artist_sense_examples(request, artist_slug):
    artist_results = Artist.objects.filter(slug=artist_slug)
    artist = artist_results[0]
    feat = request.GET.get('feat', '')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    if not feat:
        senses = [
            {
                'headword': sense.headword,
                'slug': sense.slug,
                'xml_id': sense.xml_id,
                'example_count': sense.examples.filter(artist=artist).count(),
                'examples': [build_example(example, published) for example in sense.examples.filter(artist=artist).order_by('release_date')]
            } for sense in artist.primary_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('-num_examples')[5:]
        ]
    else:
        senses = [
            {
                'headword': sense.headword,
                'slug': sense.slug,
                'xml_id': sense.xml_id,
                'example_count': sense.examples.filter(feat_artist=artist).count(),
                'examples': [build_example(example, published) for example in sense.examples.filter(feat_artist=artist).order_by('release_date')]
            } for sense in artist.featured_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('num_examples')[5:]
        ]
    if senses:
        data = {
            'senses': senses
        }
        return Response(data)
    else:
        return Response({})


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
def place_latlng(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    if results:
        data = {'places': [build_place_latlng(place) for place in results]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def remaining_place_examples(request, place_slug):
    published = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    examples = []
    if len(entity_results) >= 1:
        for entity in entity_results:
            examples += [build_example(example, published) for example in entity.examples.order_by('release_date')]

    if examples:
        data = {
            'place': place_slug,
            'examples': sorted(examples, key=itemgetter('release_date'))[NUM_QUOTS_TO_SHOW:]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def remaining_sense_examples(request, sense_id):
    published = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    sense_object = Sense.objects.filter(xml_id=sense_id)[0]
    example_results = sense_object.examples.order_by('release_date')

    if example_results:
        data = {
            'sense_id': sense_id,
            'examples': [build_example(example, published) for example in example_results[NUM_QUOTS_TO_SHOW:]]
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


@api_view(('GET',))
def sense_artist(request, sense_id, artist_slug):
    feat = request.GET.get('feat', '')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    sense_results = Sense.objects.filter(xml_id=sense_id)
    artist_results = Artist.objects.filter(slug=artist_slug)
    if sense_results and artist_results:
        sense_object = sense_results[0]
        artist_object = artist_results[0]
        if feat:
            example_results = sense_object.examples.filter(feat_artist=artist_object).order_by('release_date')[1:]
        else:
            example_results = sense_object.examples.filter(artist_name=artist_object.name).order_by('release_date')[1:]

        if example_results:
            data = {
                'sense_id': sense_id,
                'artist_slug': artist_slug,
                'examples': [build_example(example, published, rf=False) for example in example_results]
            }
            return Response(data)
        else:
            return Response({})
    else:
        return Response({})


@api_view(('GET',))
def sense_artists(request, sense_id):
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        sense_object = results[0]
        data = {'places': [build_artist(artist, require_origin=True) for artist in sense_object.cites_artists.all()]}
        return Response(data)
    else:
        return Response({})
