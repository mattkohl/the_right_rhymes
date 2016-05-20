from operator import itemgetter
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from dictionary.models import Artist, Domain, Entry, Example, \
    NamedEntity, Place, SemanticClass, Sense, Song
from dictionary.utils import build_artist, build_example, \
    build_place, build_sense, build_timeline_example, \
    check_for_image, reduce_ordered_list, reformat_name, slugify
from dictionary.views import NUM_QUOTS_TO_SHOW


@api_view(('GET',))
def artist(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        data = {
            'user': str(request.user),
            'auth': str(request.auth),
            'artists': [build_artist(artist) for artist in results]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def artist_network(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        a = results[0]
        primary_examples = a.primary_examples.all()
        featured_examples = a.featured_examples.all()

        network = []
        artist_cache = dict()

        for example in primary_examples:
            for ar in example.feat_artist.all():
                if ar not in artist_cache:
                    artist_cache[ar] = 1
                else:
                    artist_cache[ar] += 1

        for example in featured_examples:
            for ar in example.feat_artist.exclude(slug=a.slug):
                if ar is not a:
                    if ar not in artist_cache:
                        artist_cache[ar] = 1
                    else:
                        artist_cache[ar] += 1

        for example in featured_examples:
            for ar in example.artist.all():
                if ar not in artist_cache:
                    artist_cache[ar] = 1
                else:
                    artist_cache[ar] += 1

        for artist in artist_cache:
            img = check_for_image(artist.slug)
            if 'none' not in img:
                artist_object = {
                  "name": reformat_name(artist.name),
                  "link": "/artists/" + artist.slug,
                  "img":  img,
                  "size": artist_cache[artist]
                }
                network.append(artist_object)

        data = {
            'name': reformat_name(a.name),
            'img': check_for_image(a.slug),
            'link': "/artists/" + a.slug,
            'size': 5,
            'children': network
        }
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
def artists_missing_metadata(request):
    BASE_URL = "http://" + request.META['HTTP_HOST']

    primary_results_no_image = [artist for artist in Artist.objects.annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    feat_results_no_image = [artist for artist in Artist.objects.annotate(num_cites=Count('featured_examples')).order_by('-num_cites')]

    primary_results_no_origin = [artist for artist in Artist.objects.filter(origin__isnull=True).annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    feat_results_no_origin = [artist for artist in Artist.objects.filter(origin__isnull=True).annotate(num_cites=Count('featured_examples')).order_by('-num_cites')]

    if primary_results_no_image or feat_results_no_image:
        data = {
            'primary_artists_no_image': [
                                   {
                                       'name': artist.name,
                                       'slug': artist.slug,
                                       'site_link': BASE_URL + '/artists/' + artist.slug,
                                       'num_cites': artist.num_cites
                                   } for artist in primary_results_no_image if '__none' in check_for_image(artist.slug)][:3],
            'feat_artists_no_image': [
                                   {
                                       'name': artist.name,
                                       'slug': artist.slug,
                                       'site_link': BASE_URL + '/artists/' + artist.slug,
                                       'num_cites': artist.num_cites
                                   } for artist in feat_results_no_image if '__none' in check_for_image(artist.slug)][:3],
            'primary_artists_no_origin': [
                                   {
                                       'name': artist.name,
                                       'slug': artist.slug,
                                       'site_link': BASE_URL + '/artists/' + artist.slug,
                                       'num_cites': artist.num_cites
                                   } for artist in primary_results_no_origin][:3],
            'feat_artists_no_origin': [
                                   {
                                       'name': artist.name,
                                       'slug': artist.slug,
                                       'site_link': BASE_URL + '/artists/' + artist.slug,
                                       'num_cites': artist.num_cites
                                   } for artist in feat_results_no_origin][:3]
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
def headword_search(request):
    q = request.GET.get('term', '')
    results = Entry.objects.filter(publish=True).filter(headword__istartswith=q)[:20]
    if results:
        data = {
            "entries": [
                {
                    'id': entry.slug,
                    'label': entry.headword,
                    'value': entry.headword
                } for entry in results]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def place(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    if results:
        data = {'places': [build_place(place) for place in results]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def place_artists(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    if results:
        data = {'places': [build_place(place, include_artists=True) for place in results]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def random_example(request):
    published = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    result = Example.objects.order_by('?').first()
    if result:
        data = {
            'example': build_example(result, published)
        }
        data['example']['linked_lyric'] = data['example']['linked_lyric'].replace('href="/', 'href="http://www.therightrhymes.com/')
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
def sense(request, sense_id):
    results = Sense.objects.filter(xml_id=sense_id)
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    if results:
        sense_object = results[0]
        data = {'senses': [build_sense(sense_object, published)]}
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
            example_results = sense_object.examples.filter(feat_artist=artist_object).order_by('release_date')
        else:
            example_results = sense_object.examples.filter(artist_name=artist_object.name).order_by('release_date')

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
        data = {'senses': [build_artist(artist, require_origin=True) for artist in sense_object.cites_artists.all()]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def sense_timeline(request, sense_id):
    EXX_THRESHOLD = 30
    published_entries = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        sense_object = results[0]
        exx = sense_object.examples.order_by('release_date')
        exx_count = exx.count()
        if exx_count > 30:
            exx = [ex for ex in reduce_ordered_list(exx, EXX_THRESHOLD)]
        events = [build_timeline_example(example, published_entries) for example in exx if check_for_image(example.artist_slug, 'artists', 'full')]
        data = {
            "events": events
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def senses(request):
    results = Sense.objects.filter(publish=True).order_by('headword')
    if results:
        data = {
            'senses': [
                {
                    "headword": sense_object.headword,
                    "part_of_speech": sense_object.part_of_speech,
                    "xml_id": sense_object.xml_id,
                    "definition": sense_object.definition
                } for sense_object in results
            ]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def song_artist_network(request, song_slug):
    results = Song.objects.filter(slug=song_slug)
    if results:
        song = results[0]
        network = []
        artist_cache = dict()

        a = song.artist.first()

        for ar in song.feat_artist.all():
            if ar not in artist_cache:
                artist_cache[ar] = 5
            else:
                artist_cache[ar] += 1

        for artist in artist_cache:
            img = check_for_image(artist.slug)
            artist_object = {
              "name": reformat_name(artist.name),
              "link": "/artists/" + artist.slug,
              "img":  img,
              "size": artist_cache[artist]
            }
            network.append(artist_object)

        if a:
            data = {
                'name': reformat_name(a.name),
                'img': check_for_image(a.slug),
                'link': "/artists/" + a.slug,
                'size': 5,
                'children': network
            }
            return Response(data)
        else:
            return Response({})
    else:
        return Response({})


@api_view(('GET',))
def song_release_date_tree(request, song_slug):
    results = Song.objects.filter(slug=song_slug)
    if results:
        song = results[0]

        network = dict()
        for s in Song.objects.filter(release_date=song.release_date).order_by('artist_name'):
            if s != song:
                artist_name = s.artist_name
                if artist_name not in network:
                    network[artist_name] = [(s.title, s.slug)]
                else:
                    network[artist_name].extend([(s.title, s.slug)])

        if network:
            data = {
                'name': song.release_date_string,
                'children': [
                    {
                        'name': reformat_name(s),
                        "link": "/artists/" + slugify(s),
                        'children': [
                            {
                                'name': t[0],
                                'link': "/songs/" + t[1]
                            } for t in network[s]]
                     } for s in network
                ]
            }
            return Response(data)
        else:
            return Response({})
    else:
        return Response({})
