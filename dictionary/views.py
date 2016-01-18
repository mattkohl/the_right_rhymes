import os
import random
import json
from django.shortcuts import redirect, get_object_or_404, get_list_or_404, render_to_response
from django.template import loader, RequestContext
from django.http import HttpResponse, JsonResponse
from .utils import build_query, decimal_default
from .models import Entry, Sense, Artist, NamedEntity, Domain, Example, Place


def index(request):
    index = build_index()
    template = loader.get_template('dictionary/index.html')
    context = {
        'index': index,
    }
    return HttpResponse(template.render(context, request))


def build_index():
    ABC = 'abcdefghijklmnopqrstuvwxyz#'
    index = []
    for letter in ABC:
        let = {
            'letter': letter.upper(),
            'entries': Entry.objects.filter(letter=letter)
        }
        index.append(let)
    return index


def entry(request, headword_slug):
    index = build_index()
    if '#' in headword_slug:
        slug = headword_slug.split('#')[0]
    else:
        slug = headword_slug
    template = loader.get_template('dictionary/entry.html')

    entry = get_object_or_404(Entry, slug=slug)
    sense_objects = entry.senses.all()
    senses = [build_sense(sense) for sense in sense_objects]
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    image = ''
    artist_name = ''
    artist_slug = ''
    try:
        artist_slug = senses[0]['examples'][0]['example'].artist_slug
        artist_name = senses[0]['examples'][0]['example'].artist_name
    except:
        print('Could not locate artist of first quotation')
    else:
        image = check_for_artist_image(artist_slug)

    context = {
        'index': index,
        'entry': entry,
        'senses': senses,
        'published_entries': published,
        'image': image,
        'artist_slug': artist_slug,
        'artist_name': artist_name
    }
    return HttpResponse(template.render(context, request))


def artist_origins(request, artist_slug):
    print(artist_slug)
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


def build_sense(sense_object):
    result = {
        "sense": sense_object,
        "domains": sense_object.domains.order_by('name'),
        "examples": [build_example(example) for example in sense_object.examples.order_by('release_date')],
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
        "rhymes": sense_object.rhymes.order_by('-frequency'),
        "collocates": sense_object.collocates.order_by('-frequency'),
        "artist_origins": [build_artist_origin(artist) for artist in sense_object.cites_artists.all()]
    }
    return result


def build_sense_preview(sense_object):
    result = {
        "sense": sense_object,
        "examples": [build_example(example) for example in sense_object.examples.order_by('release_date')][:1],
    }
    return result


def build_artist_origin(artist):
    origin_results = artist.origin.all()
    if origin_results:
        origin_object = origin_results[0]
        if origin_object.longitude and origin_object.latitude:
            result = {
                "artist": artist.name,
                "place_name": origin_object.name,
                "longitude": origin_object.longitude,
                "latitude": origin_object.latitude
            }
            return result
        else:
            return None
    else:
        return None


def build_example(example_object):
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    lyric = example_object.lyric_text
    lyric_links = example_object.lyric_links.order_by('position')
    result = {
        "example": example_object,
        "featured_artists": example_object.feat_artist.order_by('name'),
        "linked_lyric": add_links(lyric, lyric_links, published)
    }
    return result

def add_links(lyric, links, published):
    linked_lyric = lyric
    buffer = 0
    for link in links:
        try:
            lyric.index(link.link_text)
        except:
            print("Could not inject link for {}".format(link.link_text))
            continue
        else:
            start = link.position + buffer
            end = start + len(link.link_text)
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
    index = build_index()
    artist = get_object_or_404(Artist, slug=artist_slug)
    origin_results = artist.origin.all()
    if origin_results:
        origin = origin_results[0]
    else:
        origin = ''
    entity_results = NamedEntity.objects.filter(pref_label_slug=artist_slug)
    template = loader.get_template('dictionary/artist.html')
    entity_senses = []
    if len(entity_results) >= 1:
        for entity in entity_results:
            entity_senses += [{'name': entity.name, 'sense': sense, 'examples': [build_example(example) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.order_by('headword')]

    primary_senses = [{'sense': sense, 'examples': [build_example(example) for example in sense.examples.filter(artist=artist).order_by('release_date')]} for sense in artist.primary_senses.order_by('headword')]
    featured_senses = [{'sense': sense, 'examples': [build_example(example) for example in sense.examples.filter(feat_artist=artist).order_by('release_date')]} for sense in artist.featured_senses.order_by('headword')]

    image = check_for_artist_image(artist.slug)

    context = {
        'index': index,
        'artist': artist,
        'origin': origin,
        'primary_senses': primary_senses,
        'featured_senses': featured_senses,
        'entity_senses': entity_senses,
        'image': image
    }
    return HttpResponse(template.render(context, request))


def place(request, place_slug):
    index = build_index()
    place = get_object_or_404(Place, slug=place_slug)
    template = loader.get_template('dictionary/place.html')

    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    entity_senses = []
    if len(entity_results) >= 1:
        for entity in entity_results:
            entity_senses += [{'name': entity.name, 'sense': sense, 'examples': [build_example(example) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.order_by('headword')]

    context = {
        'index': index,
        'place': place,
        'artists': [build_artist(artist) for artist in place.artists.order_by('name')],
        'entity_senses': entity_senses
    }
    return HttpResponse(template.render(context, request))


def build_artist(artist_object):
    result = {
        "artist": artist_object,
        "image": check_for_artist_image(artist_object.slug)
    }
    return result


def entity(request, entity_slug):
    index = build_index()
    results = get_list_or_404(NamedEntity, pref_label_slug=entity_slug)
    template = loader.get_template('dictionary/named_entity.html')

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
                'entity': entity,
                'senses': [{'sense': sense, 'examples': [build_example(example) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.order_by('headword')]
            })

        context = {
            'title': title,
            'index': index,
            'entities': entities
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(entity_slug))



def domain(request, domain_slug):
    index = build_index()
    template = loader.get_template('dictionary/domain.html')
    domain = get_object_or_404(Domain, slug=domain_slug)
    sense_objects = domain.senses.order_by('headword')
    senses = [build_sense_preview(sense) for sense in sense_objects]
    published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    context = {
        'index': index,
        'domain': domain,
        'senses': senses,
        'published_entries': published
    }
    return HttpResponse(template.render(context, request))



def stats(request):
    index = build_index()
    published_entries = [entry.senses.all() for entry in Entry.objects.filter(publish=True)]
    template = loader.get_template('dictionary/stats.html')
    context = {
            'index': index,
            'published_entries': published_entries
        }
    return HttpResponse(template.render(context, request))



def check_for_artist_image(slug):
    jpg = 'dictionary/static/dictionary/img/artists/{}.jpg'.format(slug)
    png = 'dictionary/static/dictionary/img/artists/{}.png'.format(slug)
    images = []
    if os.path.isfile(jpg):
        images.append(jpg.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if os.path.isfile(png):
        images.append(png.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if len(images) == 0:
        print('No image found for {}.'.format(slug))
        return ''
    else:
        return random.choice(images)


def search(request):
    index = build_index()
    published_entries = [entry.headword for entry in Entry.objects.filter(publish=True)]
    template = loader.get_template('dictionary/search_results.html')
    context = {
        'index': index,
        'published_entries': published_entries,
        'query': '',
        'senses': []
        }
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        sense_query = build_query(query_string, ['lyric_text'])
        example_results = [build_example(example) for example in Example.objects.filter(sense_query).order_by('release_date')]
        context['query'] = query_string
        context['examples'] = example_results

    return HttpResponse(template.render(context, request))


def handler404(request):
    index = build_index()
    template = loader.get_template('dictionary/404.html')
    context = {
        'index': index,
        }
    return HttpResponse(template.render(context, request), status=404)


def handler500(request):
    index = build_index()
    template = loader.get_template('dictionary/500.html')
    context = {
        'index': index,
        }
    return HttpResponse(template.render(context, request), status=500)
