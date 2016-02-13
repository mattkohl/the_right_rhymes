import os
import random
import json
from operator import itemgetter
from django.shortcuts import redirect, get_object_or_404, get_list_or_404, render_to_response
from django.template import loader, RequestContext
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .utils import build_query, decimal_default, slugify, reformat_name
from .models import Entry, Sense, Artist, NamedEntity, Domain, Example, Place, ExampleRhyme

NUM_QUOTS_TO_SHOW = 3

def index(request):
    template = loader.get_template('dictionary/index.html')
    context = {}
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


def build_index():
    ABC = 'abcdefghijklmnopqrstuvwxyz#'
    index = []
    published = Entry.objects.filter(publish=True)
    for letter in ABC:
        let = {
            'letter': letter.upper(),
            'entries': [entry for entry in published if entry.letter == letter]
        }
        index.append(let)
    return index


def assign_image(examples):
    THRESHOLD = 3
    if len(examples) < THRESHOLD:
        THRESHOLD = len(examples)
    count = 0
    artist_slug, artist_name, image = '', '', ''
    for example in examples:
        count += 1
        if 'artist_slug' in example and 'artist_name' in example:
            artist_slug = example['artist_slug']
            artist_name = example['artist_name']
            image = check_for_artist_image(artist_slug, 'full')
        if image:
            return artist_slug, artist_name, image
        if count >= THRESHOLD:
            return '', '', ''
    return '', '', ''


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
    artist_slug, artist_name, image = assign_image(image_exx)

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


def artist_origins(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if results:
        data = {'places': [build_artist_origin(artist) for artist in results]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def sense_artist_origins(request, sense_id):
    results = Sense.objects.filter(xml_id=sense_id)
    if results:
        sense_object = results[0]
        data = {'places': [build_artist_origin(artist) for artist in sense_object.cites_artists.all()]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def build_sense(sense_object, full=False):
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    example_results = sense_object.examples.order_by('release_date')
    if full:
        examples = [build_example(example, published) for example in example_results]
    else:
        examples = [build_example(example, published) for example in example_results[:NUM_QUOTS_TO_SHOW]]
    result = {
        "sense": sense_object,
        "domains": sense_object.domains.order_by('name'),
        "examples": examples,
        "num_examples": len(example_results),
        "synonyms": sense_object.xrefs.filter(xref_type="Synonym").order_by('xref_word'),
        "antonyms": sense_object.xrefs.filter(xref_type="Antonym").order_by('xref_word'),
        "meronyms": sense_object.xrefs.filter(xref_type="Meronym").order_by('xref_word'),
        "holonyms": sense_object.xrefs.filter(xref_type="Holonym").order_by('xref_word'),
        "derivatives": sense_object.xrefs.filter(xref_type="Derivative").order_by('xref_word'),
        "ancestors": sense_object.xrefs.filter(xref_type="Derives From").order_by('xref_word'),
        "instance_of": sense_object.xrefs.filter(xref_type="Instance Of").order_by('xref_word'),
        "instances": sense_object.xrefs.filter(xref_type="Instance").order_by('xref_word'),
        "related_concepts": sense_object.xrefs.filter(xref_type="Related Concept").order_by('xref_word'),
        "related_words": sense_object.xrefs.filter(xref_type="Related Word").order_by('xref_word'),
        "rhymes": sense_object.sense_rhymes.order_by('-frequency'),
        "collocates": sense_object.collocates.order_by('-frequency'),
        "artist_origins": [build_artist_origin(artist) for artist in sense_object.cites_artists.all()]
    }
    return result


def build_sense_preview(sense_object):
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    result = {
        "sense": sense_object,
        "examples": [build_example(example, published) for example in sense_object.examples.order_by('release_date')][:1]
    }
    return result


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


def build_artist_origin(artist):
    origin_results = artist.origin.all()
    if origin_results:
        origin_object = origin_results[0]
        if origin_object.longitude and origin_object.latitude:
            result = {
                "artist": artist.name,
                "place_name": origin_object.name,
                "place_slug": origin_object.slug,
                "longitude": origin_object.longitude,
                "latitude": origin_object.latitude
            }
            return result
        else:
            return None
    else:
        return None


def build_example(example_object, published, rf=False):
    lyric = example_object.lyric_text
    lyric_links = example_object.lyric_links.order_by('position')
    result = {
        "artist_name": reformat_name(str(example_object.artist_name)),
        "artist_slug": str(example_object.artist_slug),
        "song_title": str(example_object.song_title),
        "album": str(example_object.album),
        "release_date": str(example_object.release_date),
        "release_date_string": str(example_object.release_date_string),
        "featured_artists": [build_artist(feat) for feat in example_object.feat_artist.order_by('name')],
        "linked_lyric": add_links(lyric, lyric_links, published, rf),
        "cited_at": [{'headword': sense.headword, 'slug': sense.slug, 'anchor': sense.xml_id} for sense in example_object.illustrates_senses.order_by('headword')]
    }
    return result

def add_links(lyric, links, published, rf=False):
    linked_lyric = lyric
    buffer = 0
    for link in links:
        try:
            lyric.index(link.link_text)
        except:
            continue
        else:
            start = link.position + buffer
            end = start + len(link.link_text)
            if link.link_type == 'rf' and rf:
                a = '<a href="/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'rhyme':
                a = '<a href="/rhymes/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'xref' and link.target_lemma in published:
                a = '<a href="/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'artist':
                a = '<a href="/artists/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'entity':
                a = '<a href="/entities/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
    return linked_lyric

def inject_link(lyric, start, end, a):
    return lyric[:start] + a + lyric[end:]



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

    image = check_for_artist_image(artist.slug, 'full')

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


def place(request, place_slug):
    place = get_object_or_404(Place, slug=place_slug)
    template = loader.get_template('dictionary/place.html')

    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    entity_senses = []
    artists = [build_artist(artist) for artist in place.artists.order_by('name')]
    artists_with_image = [artist for artist in artists if '__none.png' not in artist['image']]
    artists_without_image = [artist for artist in artists if '__none.png' in artist['image']]
    if len(entity_results) >= 1:
        for entity in entity_results:
            entity_senses += [{'name': entity.name, 'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.filter(publish=True).order_by('headword')]

    if place.name.endswith(', USA'):
        tokens = place.name.split(', ')
        place_name = tokens[0]
    else:
        place_name = place.name

    context = {
        'place': place_name,
        'place_name_full': place.name,
        'slug': place.slug,
        'num_artists': len(artists),
        'artists_with_image': artists_with_image,
        'artists_without_image': artists_without_image,
        'entity_senses': entity_senses
    }
    return HttpResponse(template.render(context, request))


def place_latlng(request, place_slug):
    results = Place.objects.filter(slug=place_slug)
    if results:
        data = {'places': [build_place_latlng(place) for place in results]}
        return JsonResponse(json.dumps(data, default=decimal_default), safe=False)
    else:
        return JsonResponse(json.dumps({}))


def build_place_latlng(place_object):
    if place_object.longitude and place_object.latitude:
        result = {
            "place_name": place_object.name,
            "place_slug": place_object.slug,
            "longitude": place_object.longitude,
            "latitude": place_object.latitude
        }
        return result
    else:
        return None


def build_artist(artist_object):
    result = {
        # "artist": artist_object,
        "name": reformat_name(artist_object.name),
        "slug": artist_object.slug,
        "image": check_for_artist_image(artist_object.slug)
    }
    return result


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
        artist_slug, artist_name, image = assign_image(image_exx)

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


def stats(request):
    published_entries = [entry.senses.all() for entry in Entry.objects.filter(publish=True)]
    template = loader.get_template('dictionary/stats.html')
    context = {
            'published_entries': published_entries
        }
    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template('dictionary/about.html')
    context = {}
    return HttpResponse(template.render(context, request))


def check_for_artist_image(slug, folder='thumb'):
    jpg = 'dictionary/static/dictionary/img/artists/{}/{}.jpg'.format(folder, slug)
    png = 'dictionary/static/dictionary/img/artists/{}/{}.png'.format(folder, slug)
    images = []
    if os.path.isfile(jpg.encode('utf-8').strip()):
        images.append(jpg.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if os.path.isfile(png.encode('utf-8').strip()):
        images.append(png.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if len(images) == 0 and folder == 'thumb':
        # print('No image found for {}.'.format(slug))
        return '/static/dictionary/img/artists/thumb/__none.png'
    elif len(images) == 0:
        # print('No image found for {}.'.format(slug))
        return ''
    else:
        return random.choice(images)


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

    artist_slug, artist_name, image = assign_image(image_exx)

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


def handler404(request):
    template = loader.get_template('dictionary/404.html')
    context = {}
    return HttpResponse(template.render(context, request), status=404)


def handler500(request):
    template = loader.get_template('dictionary/500.html')
    context = {}
    return HttpResponse(template.render(context, request), status=500)
