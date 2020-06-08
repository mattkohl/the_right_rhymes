from operator import itemgetter
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view

from api.utils import APIUtils
from dictionary.models import Artist, Domain, Region, Entry, Example, \
    NamedEntity, Place, Salience, SemanticClass, Sense, Song
from dictionary.utils import build_artist, build_example, build_beta_example, \
    build_place, build_place_with_artist_slugs, build_sense, build_timeline_example, build_song, \
    check_for_image, reduce_ordered_list, reformat_name, slugify, build_heatmap_feature
from dictionary.views import NUM_QUOTS_TO_SHOW


@api_view(('GET',))
def api_root(request, _format=None):
    return Response({
        'artists': reverse('artists', request=request, format=_format),
        'senses': reverse('senses', request=request, format=_format)
    })


@api_view(('GET',))
def artist(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        data = {
            'user': str(request.user),
            'auth': str(request.auth),
            'artists': [build_artist(_artist) for _artist in results]
        }
        return Response(data)
    else:
        return Response({})


@api_view(("GET",))
def artist_geojson(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug).first()
    if results and results.origin:
        return Response({"type": "FeatureCollection", "features": [build_heatmap_feature(results.origin.first(), 1)]})
    else:
        return Response({"type": "FeatureCollection", "features": []})


@api_view(('GET',))
def artist_network(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        a = results[0]
        primary_examples = a.primary_examples.all()
        featured_examples = a.featured_examples.all()

        network = []
        artist_cache = dict()
        example_cache = dict()

        for example in primary_examples:
            if example.song_title not in example_cache:
                example_cache[example.song_title] = 1
                for ar in example.feat_artist.all():
                    if ar not in artist_cache:
                        artist_cache[ar] = 1
                    else:
                        artist_cache[ar] += 1

        for example in featured_examples:
            if example.song_title not in example_cache:
                example_cache[example.song_title] = 1
                for ar in example.artist.all():
                    if ar not in artist_cache:
                        artist_cache[ar] = 1
                    else:
                        artist_cache[ar] += 1
                for ar in example.feat_artist.exclude(slug=a.slug):
                    if ar is not a:
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
    _artist = artist_results[0]
    feat = request.GET.get('feat', '')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    if not feat:
        salient_senses = _artist.get_salient_senses()
        if not salient_senses.count():
            p_senses = _artist.primary_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by(
                '-num_examples')[5:]
        else:
            p_senses = [s.sense for s in salient_senses][5:]
        _senses = [
            {
                'headword': _sense.headword,
                'slug': _sense.slug,
                'xml_id': _sense.xml_id,
                'example_count': _sense.examples.filter(artist=_artist).count(),
                'examples': [build_example(example, published) for example in _sense.examples.filter(artist=_artist).order_by('release_date')]
            } for _sense in p_senses
        ]
    else:
        _senses = [
            {
                'headword': _sense.headword,
                'slug': _sense.slug,
                'xml_id': _sense.xml_id,
                'example_count': _sense.examples.filter(feat_artist=_artist).count(),
                'examples': [build_example(example, published) for example in _sense.examples.filter(feat_artist=_artist).order_by('release_date')]
            } for _sense in _artist.featured_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('num_examples')[5:]
        ]
    if _senses:
        data = {
            'senses': _senses
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def named_entities_missing_metadata(request):
    results = NamedEntity.objects.filter(entity_type='person').annotate(num_mentions=Count('examples')).order_by('-num_mentions')
    if results:
        BASE_URL = "https://" + request.META.get('HTTP_HOST', 'example.org/')
        data = [
            {
                'name': entity.name,
                'slug': entity.slug,
                'pref_label': entity.pref_label,
                'pref_label_slug': entity.pref_label_slug,
                'site_link': BASE_URL + '/entities/' + entity.pref_label_slug,
                'type': entity.entity_type,
                'num_mentions': entity.num_mentions
            } for entity in results if '__none' in check_for_image(entity.pref_label_slug, 'entities')][:5]

        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def artists(request):
    results = Artist.objects.order_by("slug")
    if results:
        data = {
            'user': str(request.user),
            'auth': str(request.auth),
            'artists': [build_artist(_artist) for _artist in results]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def artists_missing_metadata(request):
    BASE_URL = "https://" + request.META.get('HTTP_HOST', 'example.org')

    primary_results_no_image = [_artist for _artist in Artist.objects.annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    feat_results_no_image = [_artist for _artist in Artist.objects.annotate(num_cites=Count('featured_examples')).order_by('-num_cites')]

    primary_results_no_origin = [_artist for _artist in Artist.objects.filter(origin__isnull=True).annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    feat_results_no_origin = [_artist for _artist in Artist.objects.filter(origin__isnull=True).annotate(num_cites=Count('featured_examples')).order_by('-num_cites')]

    if primary_results_no_image or feat_results_no_image:
        data = {
            'primary_artists_no_image': [
                                   {
                                       'name': _artist.name,
                                       'slug': _artist.slug,
                                       'site_link': BASE_URL + '/artists/' + _artist.slug,
                                       'num_cites': _artist.num_cites
                                   } for _artist in primary_results_no_image if '__none' in check_for_image(_artist.slug)][:3],
            'feat_artists_no_image': [
                                   {
                                       'name': _artist.name,
                                       'slug': _artist.slug,
                                       'site_link': BASE_URL + '/artists/' + _artist.slug,
                                       'num_cites': _artist.num_cites
                                   } for _artist in feat_results_no_image if '__none' in check_for_image(_artist.slug)][:3],
            'primary_artists_no_origin': [
                                   {
                                       'name': _artist.name,
                                       'slug': _artist.slug,
                                       'site_link': BASE_URL + '/artists/' + _artist.slug,
                                       'num_cites': _artist.num_cites
                                   } for _artist in primary_results_no_origin][:3],
            'feat_artists_no_origin': [
                                   {
                                       'name': _artist.name,
                                       'slug': _artist.slug,
                                       'site_link': BASE_URL + '/artists/' + _artist.slug,
                                       'num_cites': _artist.num_cites
                                   } for _artist in feat_results_no_origin][:3]

        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def artist_salient_senses(request, artist_slug):
    BASE_URL = "https://" + request.META.get('HTTP_HOST', 'example.org')
    try:
        _artist = Artist.objects.get(slug=artist_slug)
    except Exception as e:
        return Response({})
    else:
        results = Salience.objects.filter(artist=_artist).order_by('-score')

        linked = [{
            "headword": s.sense.headword,
            "link": BASE_URL + '/' + s.sense.slug + "#" + s.sense.xml_id,
            "salience": s.score
        } for s in results[:10]]
        data = {
            "artist": BASE_URL + '/artists/' + _artist.slug,
            "senses": linked
        }
        return Response(data)


@api_view(('GET',))
def definitions(request, headword):
    results = Sense.objects.filter(headword=headword)
    if results:
        data = {
            "headword": headword,
            "definitions": [
                {
                    "definition": _sense.definition,
                    "part_of_speech": _sense.part_of_speech
                } for _sense in results
            ]
        }
        return Response(data)
    else:
        return Response({"Message": f"'{headword}' not found"})


@api_view(('GET',))
def domain(request, domain_slug):
    results = Domain.objects.filter(slug=domain_slug)
    if results:
        _domain = results[0]
        _senses = _domain.senses.annotate(num_examples=Count('examples')).order_by('num_examples')
        data = {
            'name': _domain.name,
            'children': [
                {
                    'word': _sense.headword,
                    'weight': _sense.num_examples,
                    'url': '/' + _sense.slug + '#' + _sense.xml_id
                } for _sense in _senses
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
                        'word': _domain.name,
                        'weight': _domain.num_senses,
                        'url': '/domains/' + _domain.slug
                    } for _domain in results
                ]
            }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def region(request, region_slug):
    results = Region.objects.filter(slug=region_slug)
    if results:
        region_object = results[0]
        _senses = region_object.senses.annotate(num_examples=Count('examples')).order_by('num_examples')
        data = {
            'name': region_object.name,
            'children': [
                {
                    'word': _sense.headword,
                    'weight': _sense.num_examples,
                    'url': '/' + _sense.slug + '#' + _sense.xml_id
                } for _sense in _senses
                ]
            }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def regions(request):
    results = Region.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    if results:
        data = {
            'name': "Regions",
            'children': [
                    {
                        'word': _region.name,
                        'weight': _region.num_senses,
                        'url': '/regions/' + _region.slug
                    } for _region in results
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
                    'id': _entry.slug,
                    'label': _entry.headword,
                    'value': _entry.headword
                } for _entry in results]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def entry(request, entry_slug):
    _entry = Entry.objects.filter(publish=True).filter(slug=entry_slug).first()
    if _entry:
        data = {
            'headword': _entry.headword,
            'slug': _entry.slug,
            'senses': [
                {
                    'part_of_speech': _sense.part_of_speech,
                    'definition': _sense.definition,
                    'example_count': _sense.examples.count(),
                    'link': reverse('sense', args=[_sense.xml_id], request=request)
                } for _sense in _entry.senses.all()]
        }
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def entries(request):
    q = request.GET.get('q', '')
    results = Entry.objects.filter(publish=True).filter(headword__istartswith=q)[:20]
    if results:
        data = {
            "entries": [
                {
                    'slug': _entry.slug,
                    'headword': _entry.headword,
                    'link': reverse('entry', args=[_entry.slug], request=request)
                } for _entry in results]
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


@api_view(("GET",))
def place_geojson(request, place_slug):
    results = Place.objects.filter(slug=place_slug).first()
    if results and results.longitude:
        return Response({"type": "FeatureCollection", "features": [build_heatmap_feature(results, 1)]})
    else:
        return Response({"type": "FeatureCollection", "features": []})


@api_view(('GET',))
def places(request):
    results = Place.objects.filter(longitude__isnull=False).annotate(num_artists=Count('artists')).order_by('-num_artists')
    return Response({'places': [build_place_with_artist_slugs(p) for p in results]}) if results else Response({})


@api_view(('GET',))
def place_artists(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    return Response({'artists': [build_place(p, include_artists=True) for p in results]}) if results else Response({})


@api_view(('GET',))
def random_entry(request):
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    _entry = Entry.objects.filter(publish=True).order_by('?').first()
    if _entry:
        _senses = [build_sense(_sense, published) for _sense in _entry.get_senses_ordered_by_example_count()]
        data = {'headword': _entry.headword, 'slug': _entry.slug, 'pub_date': _entry.pub_date, 'senses': _senses}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def random_artist(request):
    a = Artist.objects.all().order_by('?').first()
    return Response(build_artist(a)) if a else Response({})


@api_view(('GET',))
def random_song(request):
    s = Song.objects.all().order_by('?').first()
    return Response(build_song(s)) if s else Response({})


@api_view(('GET',))
def random_place(request):
    p = Place.objects.filter(longitude__isnull=False).order_by('?').first()
    return Response(build_place(p)) if p else Response({})


@api_view(('GET',))
def random_sense(request):
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    s = Sense.objects.filter(publish=True).order_by('?').first()
    return Response(build_sense(s, published)) if s else Response({})


@api_view(('GET',))
def random_example(request):
    result = Example.objects.order_by('?').first()
    return Response(build_beta_example(result)) if result else Response({})


@api_view(('GET',))
def remaining_place_examples(request, place_slug):
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
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
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
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
                        'word': _sense.headword,
                        'weight': _sense.examples.count(),
                        'url': '/' + _sense.slug + '#' + _sense.xml_id
                    } for _sense in semantic_class_object.senses.all()
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
                        'word': _semantic_class.name,
                        'weight': _semantic_class.num_senses,
                        'url': '/semantic-classes/' + _semantic_class.slug
                    } for _semantic_class in results
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
        _sense = results[0]
        sense_artist_dicts = [
            build_artist(a, require_origin=True, count=_sense.examples.filter(artist=a).count())
            for a in _sense.cites_artists.all()
        ]
        data = {'artists': [a for a in sense_artist_dicts if a is not None]}
        return Response(data)
    else:
        return Response({})


@api_view(('GET',))
def sense_artists_geojson(request, sense_id):
    _sense = Sense.objects.filter(xml_id=sense_id).first()

    if _sense:
        _artists = [a for a in _sense.cites_artists.all() if a.origin.first() is not None]
        sense_artist_dicts = [build_heatmap_feature(a.origin.first(), count=_sense.examples.filter(artist=a).count()) for a in _artists]
        return Response({"type": "FeatureCollection", "features": [a for a in sense_artist_dicts if a is not None]})
    else:
        return Response({"type": "FeatureCollection", "features": []})


@api_view(('GET',))
def sense_artists_salience(request, sense_id):
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        _sense = results[0]
        _saliences = Salience.objects.filter(sense=_sense).order_by("-score")

        sorted_data = [{
            "artist": build_artist(s.artist),
            "salience": s.score
        } for s in _saliences[:10]]

        return Response(
            {"artists": sorted_data,
             "headword": _sense.headword,
             "xml_id": _sense.xml_id,
             "definition": _sense.definition}
        )
    else:
        return Response({})


@api_view(('GET',))
def sense_timeline(request, sense_id):
    EXX_THRESHOLD = 30
    published_entries = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        _sense = results[0]
        exx = _sense.examples.order_by('release_date')
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
    q = request.GET.get('q', '')
    limit, offset = APIUtils.extract_limit_offset(request)
    results = Sense.objects.filter(publish=True).filter(headword__istartswith=q).order_by('headword')[offset:limit+offset]
    if results:
        data = {
            'senses': [
                {
                    "headword": _sense.headword,
                    "part_of_speech": _sense.part_of_speech,
                    "xml_id": _sense.xml_id,
                    "definition": _sense.definition,
                    'link': reverse('sense', args=[_sense.xml_id], request=request)
                } for _sense in results
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

        for _artist in artist_cache:
            img = check_for_image(_artist.slug)
            artist_object = {
              "name": reformat_name(_artist.name),
              "link": "/artists/" + _artist.slug,
              "img":  img,
              "size": artist_cache[_artist]
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
        cache = set()
        for s in Song.objects.filter(release_date=song.release_date, examples__isnull=False).order_by('artist_name'):
            if s != song and s.slug not in cache:
                cache.add(s.slug)
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


@api_view(('GET',))
def senses_unpublished(request):
    unpublished_senses = Sense.objects.filter(publish=False).annotate(num_examples=Count('examples')).order_by('-num_examples')[:5]
    data = {
        "senses": [{
            "xml_id": unpublished_sense.xml_id,
            "num_examples": unpublished_sense.num_examples
        } for unpublished_sense in unpublished_senses]
    }
    return Response(data)
