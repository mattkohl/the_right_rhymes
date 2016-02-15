import json

from operator import itemgetter

from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from django.template import loader
from django.http import HttpResponse, JsonResponse

from django.db.models import Q, Count

from dictionary.utils import build_place_latlng, build_artist, assign_artist_image, build_sense, build_sense_preview, \
    build_artist_origin, build_example, check_for_image, abbreviate_place_name
from .utils import build_query, decimal_default, slugify, reformat_name
from .models import Entry, Sense, Artist, NamedEntity, Domain, Example, Place, ExampleRhyme


NUM_QUOTS_TO_SHOW = 3


def about(request):
    template = loader.get_template('dictionary/about.html')
    context = {}
    return HttpResponse(template.render(context, request))


def artist(request, artist_slug):
    artist_results = get_list_or_404(Artist, slug=artist_slug)
    artist = artist_results[0]
    origin_results = artist.origin.all()
    if origin_results:
        origin = origin_results[0].name
        origin_slug = origin_results[0].slug
    else:
        origin = ''
        origin_slug = ''
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    template = loader.get_template('dictionary/artist.html')
    entity_results = NamedEntity.objects.filter(pref_label_slug=artist_slug)

    primary_senses = [{'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(artist=artist).order_by('release_date')]} for sense in artist.primary_senses.filter(publish=True).order_by('headword')]
    featured_senses = [{'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(feat_artist=artist).order_by('release_date')]} for sense in artist.featured_senses.filter(publish=True).order_by('headword')]
    entity_examples = []
    for e in entity_results:
        for example in e.examples.all():
            entity_examples.append(build_example(example, published))

    image = check_for_image(artist.slug, 'artists', 'full')

    name = reformat_name(artist.name)

    context = {
        'artist': name,
        'slug': artist.slug,
        'origin': origin,
        'origin_slug': origin_slug,
        'primary_senses': primary_senses,
        'featured_senses': featured_senses,
        'entity_examples': entity_examples,
        'image': image
    }
    return HttpResponse(template.render(context, request))


def artist_origins(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        data = {'places': [build_artist_origin(artist) for artist in results]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def domain(request, domain_slug):
    template = loader.get_template('dictionary/domain.html')
    domain = get_object_or_404(Domain, slug=domain_slug)
    sense_objects = domain.senses.filter(publish=True).order_by('headword')
    senses = [build_sense_preview(sense) for sense in sense_objects]
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    data = [sense.headword for sense in sense_objects]
    context = {
        'domain': domain.name,
        'senses': senses,
        'published_entries': published,
        'data': json.dumps(data)
    }
    return HttpResponse(template.render(context, request))


def domain_json(request, domain_slug):
    results = Domain.objects.filter(slug=domain_slug)
    if results:
        domain_object = results[0]
        data = {'name': domain_object.name, 'children': [ {'name': sense.headword } for sense in domain_object.senses.all()]}
        return JsonResponse(json.dumps(data), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def entity(request, entity_slug):
    results = get_list_or_404(NamedEntity, pref_label_slug=entity_slug)
    template = loader.get_template('dictionary/named_entity.html')
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]

    if len(results) > 0:
        entities = []
        title = ''
        for entity in results:
            title = entity.pref_label
            if entity.entity_type == 'artist':
                return redirect('/artists/' + entity.pref_label_slug)
            if entity.entity_type == 'place':
                return redirect('/places/' + entity.pref_label_slug)
            entities.append({
                'name': entity.name,
                'pref_label': entity.pref_label,
                'senses': [{'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.filter(publish=True).order_by('headword')]
            })

        image_exx = entities[0]['senses'][0]['examples']
        artist_slug, artist_name, image = assign_artist_image(image_exx)

        context = {
            'title': title,
            'entities': entities,
            'image': image,
            'artist_slug': artist_slug,
            'artist_name': artist_name
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(entity_slug))


def entry(request, headword_slug):
    if '#' in headword_slug:
        slug = headword_slug.split('#')[0]
    else:
        slug = headword_slug
    template = loader.get_template('dictionary/entry.html')

    entry = get_object_or_404(Entry, slug=slug, publish=True)
    sense_objects = entry.senses.all()
    senses = [build_sense(sense) for sense in sense_objects]
    published = [entry.slug for entry in Entry.objects.filter(publish=True)]
    image_exx = [example for example in senses[0]['examples']]
    artist_slug, artist_name, image = assign_artist_image(image_exx)

    context = {
        'headword': entry.headword,
        'pub_date': entry.pub_date,
        'last_updated': entry.last_updated,
        'senses': senses,
        'published_entries': published,
        'image': image,
        'artist_slug': artist_slug,
        'artist_name': artist_name
    }
    return HttpResponse(template.render(context, request))


def index(request):
    template = loader.get_template('dictionary/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def collect_place_artists(place_object, artists):

    artists.extend([build_artist(artist) for artist in place_object.artists.all()])
    contains = place_object.contains.all()
    if contains:
        for contained in contains:
            collect_place_artists(contained, artists)
    return sorted(artists, key=itemgetter('name'))

def place(request, place_slug):
    place = get_object_or_404(Place, slug=place_slug)
    template = loader.get_template('dictionary/place.html')

    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    entity_senses = []

    artists = collect_place_artists(place, [])

    artists_with_image = [artist for artist in artists if '__none.png' not in artist['image']]
    artists_without_image = [artist for artist in artists if '__none.png' in artist['image']]

    contains = [{'name': c.name, 'slug': c.slug} for c in place.contains.order_by('name')]
    within = {}
    if ', ' in place.name:
        w_name = ', '.join(place.name.split(', ')[1:])
        w_slug = slugify(w_name)
        within = {'name': w_name, 'slug': w_slug}

    if len(entity_results) >= 1:
        for entity in entity_results:
            entity_senses += [{'name': entity.name, 'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.filter(publish=True).order_by('headword')]

    context = {
        'place': abbreviate_place_name(place.name),
        'place_name_full': place.name,
        'slug': place.slug,
        'contains': contains,
        'within': within,
        'num_artists': len(artists),
        'artists_with_image': artists_with_image,
        'artists_without_image': artists_without_image,
        'entity_senses': entity_senses,
        'image': check_for_image(place.slug, 'places', 'full')
    }
    return HttpResponse(template.render(context, request))


def place_latlng(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    if results:
        data = {'places': [build_place_latlng(place) for place in results]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def remaining_examples(request, sense_id):
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    sense_object = Sense.objects.filter(xml_id=sense_id)[0]
    example_results = sense_object.examples.order_by('release_date')

    if example_results:
        data = {
            'sense_id': sense_id,
            'examples': [build_example(example, published) for example in example_results[NUM_QUOTS_TO_SHOW:]]
        }
        return JsonResponse(json.dumps(data), safe=False)
    else:
        return JsonResponse(json.dumps({}))

def rhyme(request, rhyme_slug):
    template = loader.get_template('dictionary/rhyme.html')
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    published_slugs = [entry.slug for entry in Entry.objects.filter(publish=True)]
    title = rhyme_slug

    rhyme_results = ExampleRhyme.objects.filter(Q(word_one_slug=rhyme_slug)|Q(word_two_slug=rhyme_slug))
    rhymes_intermediate = {}
    image_exx = []

    for r in rhyme_results:
        if r.word_one_slug == rhyme_slug:
            title = r.word_one
            rhyme = r.word_two
            slug = r.word_two_slug
        else:
            title = r.word_two
            rhyme = r.word_one
            slug = r.word_one_slug

        exx = [build_example(example, published) for example in r.parent_example.all()]
        if exx:
            image_exx.extend(exx)

        if slug in rhymes_intermediate:
            rhymes_intermediate[slug]['examples'].extend(exx)
        else:
            rhymes_intermediate[slug] = {
               'rhyme': rhyme,
               'examples': exx
            }
        rhymes_intermediate[slug]['examples'] = sorted(rhymes_intermediate[slug]['examples'], key=itemgetter('release_date'))

    artist_slug, artist_name, image = assign_artist_image(image_exx)

    rhymes = [{'slug': r, 'rhyme': rhymes_intermediate[r]['rhyme'], 'examples': rhymes_intermediate[r]['examples']} for r in rhymes_intermediate]

    context = {
        'published_entries': published_slugs,
        'rhyme': title,
        'rhymes': rhymes,
        'artist_slug': artist_slug,
        'artist_name': artist_name,
        'image': image
        }

    return HttpResponse(template.render(context, request))


def search(request):
    published_entries = [entry.headword for entry in Entry.objects.filter(publish=True)]
    published_entry_slugs = [entry.slug for entry in Entry.objects.filter(publish=True)]

    artist_slugs = [artist.slug for artist in Artist.objects.all()]

    template = loader.get_template('dictionary/search_results.html')
    context = dict()
    if ('q' in request.GET) and request.GET['q'].strip():
        search_param = request.GET['search_param']
        search_slug = request.GET['search_slug']
        query_string = request.GET['q']
        query_slug = slugify(query_string)
        context['search_param'] = search_param
        if search_param == 'headwords':
            return redirect('entry', headword_slug=search_slug)
        elif query_slug in published_entry_slugs:
            return redirect('entry', headword_slug=query_slug)
        elif query_slug in artist_slugs:
            return redirect('artist', artist_slug=query_slug)
        else:
            sense_query = build_query(query_string, ['lyric_text'])
            example_results = [build_example(example, published_entries) for example in Example.objects.filter(sense_query).order_by('release_date')]
            context['query'] = query_string
            context['examples'] = example_results

    return HttpResponse(template.render(context, request))


def search_headwords(request):
    q = request.GET.get('term', '')
    entries = Entry.objects.filter(publish=True).filter(headword__istartswith=q)[:20]
    results = []
    for entry in entries:
        result = dict()
        result['id'] = entry.slug
        result['label'] = entry.headword
        result['value'] = entry.headword
        results.append(result)

    data = {'headwords': results}
    return JsonResponse(json.dumps(data), safe=False)


def sense_artist_origins(request, sense_id):
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        sense_object = results[0]
        data = {'places': [build_artist_origin(artist) for artist in sense_object.cites_artists.all()]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def stats(request):

    LIST_LENGTH = 5

    published_entries = Entry.objects.filter(publish=True)
    published_senses = [sense for entry in published_entries for sense in entry.senses.all()]
    examples = [example for sense in published_senses for example in sense.examples.all()]
    best_attested_senses = [sense for sense in Sense.objects.annotate(num_examples=Count('examples')).order_by('-num_examples')]

    dates = [example for example in Example.objects.order_by('release_date')]
    seventies = [example.release_date for example in Example.objects.filter(release_date__range=["1970-01-01", "1979-12-31"])]
    eighties = [example.release_date for example in Example.objects.filter(release_date__range=["1980-01-01", "1989-12-31"])]
    nineties = [example.release_date for example in Example.objects.filter(release_date__range=["1990-01-01", "1999-12-31"])]
    noughties = [example.release_date for example in Example.objects.filter(release_date__range=["2000-01-01", "2009-12-31"])]
    twenty_tens = [example.release_date for example in Example.objects.filter(release_date__range=["2010-01-01", "2019-12-31"])]
    artists = [artist for artist in Artist.objects.annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    places = [place for place in Place.objects.annotate(num_artists=Count('artists')).order_by('-num_artists')]
    linked_exx = [example for example in Example.objects.annotate(num_links=Count('lyric_links')).order_by('-num_links')]

    template = loader.get_template('dictionary/stats.html')
    context = {
        'num_entries': len(published_entries),
        'num_senses': len(published_senses),
        'num_examples': len(examples),
        'best_attested_senses': [{'headword': sense.headword, 'definition': sense.definition, 'num_examples': sense.num_examples} for sense in best_attested_senses[:LIST_LENGTH]],
        'num_artists': len(artists),
        'num_places': len(places),
        'best_represented_places': [{'name': place.name.split(', ')[0], 'slug': place.slug, 'num_artists': place.num_artists} for place in places[:LIST_LENGTH+20]],
        'earliest_date': {'example': [build_example(date, published_entries) for date in dates[:LIST_LENGTH]]},
        'latest_date': {'example': [build_example(date, published_entries) for date in dates[-LIST_LENGTH:]]},
        'num_seventies': len(seventies),
        'num_eighties': len(eighties),
        'num_nineties': len(nineties),
        'num_noughties': len(noughties),
        'num_twenty_tens': len(twenty_tens),
        'most_linked_example': {'example': [build_example(linked_exx[0], published_entries)], 'count': linked_exx[0].num_links},
        'most_cited_artists': [{'artist': build_artist(artist), 'count': artist.num_cites} for artist in artists[:LIST_LENGTH]]
    }
    return HttpResponse(template.render(context, request))


def handler404(request):
    template = loader.get_template('dictionary/404.html')
    context = {}
    return HttpResponse(template.render(context, request), status=404)


def handler500(request):
    template = loader.get_template('dictionary/500.html')
    context = {}
    return HttpResponse(template.render(context, request), status=500)
