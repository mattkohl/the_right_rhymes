import json
import logging
import os
from operator import itemgetter

from django.core.cache import cache
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from django.template import loader
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control

from dictionary.utils import build_artist, assign_artist_image, build_sense, build_sense_preview, \
    build_example, check_for_image, abbreviate_place_name, \
    collect_place_artists, build_entry_preview, dedupe_rhymes
from .models import Entry, Sense, Artist, NamedEntity, Domain, Region, Example, Place, ExampleRhyme, Song, \
    SemanticClass, Stats, Form
from .utils import build_query, slugify, reformat_name, un_camel_case, move_definite_article_to_end, update_stats
from dictionary.forms import SongForm


logger = logging.getLogger(__name__)
NUM_QUOTS_TO_SHOW = 3
NUM_ARTISTS_TO_SHOW = 6

MAPS_TOKEN = os.getenv("MAPS_TOKEN", None)


@cache_control(max_age=3600)
def about(request):
    template = loader.get_template('dictionary/about.html')
    entry_count = Entry.objects.filter(publish=True).count()
    context = {
        'entry_count': entry_count
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=360)
def a_to_z(request):
    template = loader.get_template('dictionary/a_to_z.html')
    published = cache.get('a_to_z')
    if published is None:
        published = [
            {
                'headword': e[0],
                'slug': e[1],
                'letter': e[2].lower(),
                'sort_key': e[3]
            } for e in Entry.objects.values_list('headword', 'slug', 'letter', 'sort_key').filter(publish=True).order_by(Lower('sort_key'))]
        cache.set('a_to_z', published, 86400)

    context = {
        'entries': published
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def artist(request, artist_slug):
    a = get_object_or_404(Artist, slug=artist_slug)
    origin_results = a.origin.all()
    if origin_results:
        origin = origin_results[0].full_name
        origin_slug = origin_results[0].slug
        long = origin_results[0].longitude
        lat = origin_results[0].latitude
    else:
        origin = ''
        origin_slug = ''
        long = ''
        lat = ''
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    template = loader.get_template('dictionary/artist.html')
    entity_results = NamedEntity.objects.filter(pref_label_slug=artist_slug)

    salient_senses = a.get_salient_senses()
    if not salient_senses.count():
        p_senses = a.primary_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('-num_examples')[:5]
    else:
        p_senses = [s.sense for s in salient_senses][:5]

    primary_senses = [
        {
            'headword': sense.headword,
            'slug': sense.slug,
            'xml_id': sense.xml_id,
            'example_count': sense.examples.filter(artist=a).count(),
            'examples': [build_example(example, published) for example in sense.examples.filter(artist=a).order_by('release_date')]
        } for sense in p_senses
    ]

    featured_senses = [
        {
            'headword': sense.headword,
            'slug': sense.slug,
            'xml_id': sense.xml_id,
            'example_count': sense.examples.filter(feat_artist=a).count(),
            'examples': [build_example(example, published) for example in sense.examples.filter(feat_artist=a).order_by('release_date')]
        } for sense in a.featured_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('num_examples')[:5]
    ]

    entity_examples = []
    if entity_results:
        entity_examples = [build_example(example, published) for example in entity_results[0].examples.all()]

    image = check_for_image(a.slug, 'artists', 'full')
    thumb = check_for_image(a.slug, 'artists', 'thumb')
    name = reformat_name(a.name)
    primary_sense_count = a.primary_senses.filter(publish=True).count()
    featured_sense_count = a.featured_senses.filter(publish=True).count()

    context = {
        'artist': name,
        'slug': a.slug,
        'origin': origin,
        'origin_slug': origin_slug,
        'longitude': long,
        'latitude': lat,
        'primary_sense_count': primary_sense_count,
        'featured_sense_count': featured_sense_count,
        'primary_senses': primary_senses,
        'featured_senses': featured_senses,
        'entity_examples': entity_examples,
        'entity_example_count': len(entity_examples),
        'image': image,
        'thumb': thumb,
        'also_known_as': [build_artist(aka) for aka in a.also_known_as.all()],
        'member_of':  [build_artist(m) for m in a.member_of.all()],
        'members': [build_artist(m) for m in a.members.all()],
        'maps_token': MAPS_TOKEN
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def domain(request, domain_slug):
    template = loader.get_template('dictionary/domain.html')
    d = get_object_or_404(Domain, slug=domain_slug)
    sense_objects = d.senses.filter(publish=True).order_by('headword')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    senses = [build_sense_preview(sense) for sense in sense_objects]
    senses_data = [{"word": sense.headword, "weight": sense.examples.count()} for sense in sense_objects]
    data = [sense.headword for sense in sense_objects]
    context = {
        'domain': un_camel_case(d.name),
        'slug': domain_slug,
        'senses': senses,
        'senses_data': json.dumps(senses_data),
        'published_entries': published,
        'image': check_for_image(d.slug, 'domains', 'full'),
        'data': json.dumps(data)
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def domains(request):
    template = loader.get_template('dictionary/domains.html')
    results = Domain.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    domain_count = results.count()
    context = {
        'domain_count': domain_count,
        'image': check_for_image('domains', 'domains', 'full')
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def region(request, region_slug):
    template = loader.get_template('dictionary/region.html')
    r = get_object_or_404(Region, slug=region_slug)
    sense_objects = r.senses.filter(publish=True).order_by('headword')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    senses = [build_sense_preview(sense) for sense in sense_objects]
    senses_data = [{"word": sense.headword, "weight": sense.examples.count()} for sense in sense_objects]
    data = [sense.headword for sense in sense_objects]
    context = {
        'r': un_camel_case(r.name),
        'slug': region_slug,
        'senses': senses,
        'senses_data': json.dumps(senses_data),
        'published_entries': published,
        'image': check_for_image(r.slug, 'regions', 'full'),
        'data': json.dumps(data),
        'maps_token': MAPS_TOKEN
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def regions(request):
    template = loader.get_template('dictionary/regions.html')
    results = Region.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    region_count = results.count()
    context = {
        'region_count': region_count,
        'image': check_for_image('regions', 'regions', 'full')
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def entity(request, entity_slug):
    results = get_list_or_404(NamedEntity, pref_label_slug=entity_slug)
    template = loader.get_template('dictionary/named_entity.html')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)

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
                'slug': entity.slug,
                'pref_label': entity.pref_label,
                'pref_label_slug': entity.pref_label_slug,
                'senses': [{'sense': sense, 'examples': [build_example(example, published) for example in sense.examples.filter(features_entities=entity).order_by('release_date')]} for sense in entity.mentioned_at_senses.filter(publish=True).order_by('headword')]
            })

        context = {
            'title': title,
            'entities': entities,
            'image': check_for_image(entities[0]['pref_label_slug'], 'entities', 'full'),
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(entity_slug))


@cache_control(max_age=3600)
def entry(request, headword_slug):
    if '#' in headword_slug:
        slug = headword_slug.split('#')[0]
    else:
        slug = headword_slug
    template = loader.get_template('dictionary/entry.html')

    entry = get_object_or_404(Entry, slug=slug, publish=True)
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    slugs = list(published)
    include_form = request.user.is_authenticated
    include_all_senses = False
    senses = [build_sense(sense, published, include_all_senses, include_form) for sense in entry.get_senses_ordered_by_example_count()]
    index = slugs.index(slug)
    preceding = slugs[index-1] if index-1 >= 0 else None
    following = slugs[index+1] if index+1 < len(published) else None
    context = {
        'headword': entry.headword,
        'slug': slug,
        'title': entry.headword[0].upper() + entry.headword[1:],
        'image': senses[0]['image'] if len(senses) > 0 else None,
        'pub_date': entry.pub_date,
        'last_updated': entry.last_updated,
        'senses': senses,
        'published_entries': published,
        'preceding': preceding,
        'following': following,
        'maps_token': MAPS_TOKEN
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def index(request):
    template = loader.get_template('dictionary/index.html')
    entry_count = Entry.objects.filter(publish=True).count()
    sense_count = Sense.objects.filter(publish=True).count()
    example_count = Example.objects.all().count()
    artist_count = Artist.objects.all().count()
    recently_published = [build_entry_preview(e) for e in Entry.objects.filter(publish=True).order_by('-pub_date')[:5]]
    context = {
        "entry_count": entry_count,
        "sense_count": sense_count,
        "example_count": example_count,
        "artist_count": artist_count,
        "recently_published": recently_published
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def place(request, place_slug):
    p = get_object_or_404(Place, slug=place_slug)
    template = loader.get_template('dictionary/place.html')

    published = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    examples = []

    artists = collect_place_artists(p, [])

    artists_with_image = [artist for artist in artists if '__none.png' not in artist['image']]
    artists_without_image = [artist for artist in artists if '__none.png' in artist['image']]

    contains = [{'name': abbreviate_place_name(c.name), 'slug': c.slug} for c in p.contains.order_by('name')]
    within = {}
    if ', ' in p.full_name:
        w_name = ', '.join(p.full_name.split(', ')[1:])
        w_slug = slugify(w_name)
        within = {'name': abbreviate_place_name(w_name), 'slug': w_slug}

    # TODO: reorder examples by release_date in case of multiple entities
    if len(entity_results) >= 1:
        for entity in entity_results:
            examples += [build_example(example, published, rf=True) for example in entity.examples.order_by('release_date')]

    context = {
        'place': p.name,
        'place_name_full': p.full_name,
        'slug': p.slug,
        'contains': contains,
        'within': within,
        'num_artists': len(artists),
        'artists_with_image': artists_with_image,
        'artists_without_image': artists_without_image,
        'image': check_for_image(p.slug, 'places', 'full'),
        'examples': sorted(examples, key=itemgetter('release_date'))[:NUM_QUOTS_TO_SHOW],
        'num_examples': len(examples),
        'maps_token': MAPS_TOKEN
    }
    return HttpResponse(template.render(context, request))


def random_entry(request):
    rand_entry = Entry.objects.filter(publish=True).order_by('?').first()
    return redirect('entry', headword_slug=rand_entry.slug)


@cache_control(max_age=3600)
def rhyme(request, rhyme_slug):
    template = loader.get_template('dictionary/rhyme.html')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
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

        dedupe_rhymes(rhymes_intermediate)

        rhymes_intermediate[slug]['examples'] = sorted(rhymes_intermediate[slug]['examples'], key=itemgetter('release_date'))

    artist_slug, artist_name, image = assign_artist_image(image_exx)

    rhymes = [
        {
            'slug': r,
            'rhyme': rhymes_intermediate[r]['rhyme'],
            'examples': rhymes_intermediate[r]['examples']
        } for r in rhymes_intermediate
    ]

    context = {
        'published_entries': published,
        'rhyme': title,
        'rhymes': rhymes,
        'artist_slug': artist_slug,
        'artist_name': artist_name,
        'image': image
        }

    return HttpResponse(template.render(context, request))


@cache_control(max_age=360)
def search(request):
    published_entry_forms = Form.objects.filter(parent_entry__publish=True).values_list('slug', flat=True)
    published_entry_slugs = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    artist_slugs = [artist.slug for artist in Artist.objects.all()]
    entity_slugs = [entity.pref_label_slug for entity in NamedEntity.objects.filter(entity_type='person')]
    template = loader.get_template('dictionary/search_results.html')
    context = dict()
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        query_slug = slugify(query_string)

        if query_string.lower().startswith("the "):
                alt_query_string = move_definite_article_to_end(query_string)
                alt_query_slug = slugify(alt_query_string)
        else:
            alt_query_slug = ''

        if query_slug in published_entry_forms:
            form = Form.objects.get(slug=query_slug)
            parent_entry = form.parent_entry.first()
            return redirect('entry', headword_slug=parent_entry.slug)
        elif query_slug in published_entry_slugs:
            return redirect('entry', headword_slug=query_slug)
        elif query_slug in artist_slugs:
            return redirect('artist', artist_slug=query_slug)
        elif query_slug in entity_slugs:
            return redirect('entity', entity_slug=query_slug)
        elif alt_query_slug and alt_query_slug in published_entry_slugs:
            return redirect('entry', headword_slug=alt_query_slug)
        elif alt_query_slug and alt_query_slug in artist_slugs:
            return redirect('artist', artist_slug=alt_query_slug)
        else:
            sense_query = build_query(query_string, ['lyric_text'])
            result_count = Example.objects.filter(sense_query).order_by('-release_date').count()
            example_results = [build_example(example, published=published_entry_slugs, rf=True) for example in Example.objects.filter(sense_query).order_by('-release_date')[:100]]
            context['query'] = query_string
            context['examples'] = example_results
            context['result_count'] = result_count
            context['the_rest'] = (result_count - 100) if (result_count > 100) else 0

    other_entries = []
    if 'result_count' in context and context['result_count'] < 1 or 'result_count' not in context:
        for i in range(6):
            r = Sense.objects.filter(publish=True).order_by('?').first()
            if r:
                other_entries.append(build_sense_preview(r))
    context['other_entries'] = other_entries

    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def semantic_class(request, semantic_class_slug):
    template = loader.get_template('dictionary/semantic_class.html')
    semantic_class = get_object_or_404(SemanticClass, slug=semantic_class_slug)
    sense_count = semantic_class.senses.filter(publish=True).order_by('headword').count()
    context = {
        'semantic_class': un_camel_case(semantic_class.name),
        'slug': semantic_class_slug,
        'sense_count': sense_count,
        'image': check_for_image(semantic_class.slug, 'semantic_classes', 'full')
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def semantic_classes(request):
    template = loader.get_template('dictionary/semantic_classes.html')
    results = SemanticClass.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')
    semantic_class_count = results.count()
    context = {
        'semantic_class_count': semantic_class_count,
        'image': check_for_image('semantic-classes', 'semantic_classes', 'full')
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def sense_timeline(request, sense_id):
    sense = get_object_or_404(Sense, xml_id=sense_id)
    template = loader.get_template('dictionary/_timeline.html')
    context = {
        "sense_id": sense_id,
        "headword": sense.headword
    }
    return HttpResponse(template.render(context, request))


@require_http_methods(['GET', 'POST'])
def song(request, song_slug):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            song = Song.objects.get(slug=song_slug)
            song.title = form.cleaned_data['title']
            song.release_date = form.cleaned_data["release_date"]
            song.release_date_string = form.cleaned_data["release_date_string"]
            song.artist_name = form.cleaned_data["artist_name"]
            song.album = form.cleaned_data["album"]
            song.lyrics = form.cleaned_data["lyrics"]
            song.release_date_verified = form.cleaned_data["release_date_verified"]
            song.save()

    song = get_list_or_404(Song, slug=song_slug)[0]
    template = loader.get_template('dictionary/song.html')
    same_dates = [
        {
            'title': s.title,
            'artist_name': reformat_name(s.artist_name),
            'artist_slug': s.artist_slug,
            'slug': s.slug
        } for s in Song.objects.filter(release_date=song.release_date).order_by('artist_name') if s != song]
    image = check_for_image(song.artist_slug, 'artists', 'full')
    thumb = check_for_image(song.artist_slug, 'artists', 'thumb')
    form = SongForm(instance=song)
    sense_results = set([s for e in song.examples.all() for s in e.illustrates_senses.filter(publish=True).order_by('headword')])
    senses = [build_sense_preview(s) for s in sense_results]

    context = {
        "title": song.title,
        "slug": song.slug,
        "image": image,
        "thumb": thumb,
        "artist_name": reformat_name(song.artist_name),
        "artist_slug": song.artist_slug,
        "primary_artist": [build_artist(a) for a in song.artist.all()],
        "featured_artists": [build_artist(a) for a in song.feat_artist.all()],
        "release_date": song.release_date,
        "release_date_string": song.release_date_string,
        "album": song.album,
        "senses": senses,
        "same_dates": same_dates,
        "form": None
    }

    if request.user.is_authenticated:
        context['form'] = form

    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def stats(request):
    most_recent_stats = Stats.objects.all().order_by('-created')
    if most_recent_stats:
        context = json.loads(most_recent_stats.first().json)
    else:
        context = update_stats()
    template = loader.get_template('dictionary/stats.html')
    return HttpResponse(template.render(context, request))


def handler404(request):
    template = loader.get_template('dictionary/404.html')
    context = {}
    return HttpResponse(template.render(context, request), status=404)


def handler500(request):
    template = loader.get_template('dictionary/500.html')
    context = {}
    return HttpResponse(template.render(context, request), status=500)
