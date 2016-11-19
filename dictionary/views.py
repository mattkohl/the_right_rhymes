import json
import logging
from operator import itemgetter

from django.core.cache import cache
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control

from dictionary.utils import build_artist, assign_artist_image, build_sense, build_sense_preview, \
    build_example, check_for_image, abbreviate_place_name, \
    collect_place_artists, build_entry_preview, count_place_artists, dedupe_rhymes
from .models import Entry, Sense, Artist, NamedEntity, Domain, Example, Place, ExampleRhyme, Song, SemanticClass
from .utils import build_query, slugify, reformat_name, un_camel_case, move_definite_article_to_end
from dictionary.forms import SongForm


logger = logging.getLogger(__name__)
NUM_QUOTS_TO_SHOW = 3
NUM_ARTISTS_TO_SHOW = 6


@cache_control(max_age=3600)
def about(request):
    template = loader.get_template('dictionary/about.html')
    entry_count = Entry.objects.filter(publish=True).count()
    context = {
        'entry_count': entry_count
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def a_to_z(request):
    template = loader.get_template('dictionary/a_to_z.html')
    published = cache.get('a_to_z')
    if published is None:
        published = [{'headword': e[0], 'slug': e[1], 'letter': e[2]} for e in Entry.objects.values_list('headword', 'slug', 'letter').filter(publish=True).order_by(Lower('headword'))]
        cache.set('a_to_z', published, 86400)

    context = {
        'entries': published
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def artist(request, artist_slug):
    artist_results = get_list_or_404(Artist, slug=artist_slug)
    artist = artist_results[0]
    origin_results = artist.origin.all()
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

    primary_senses = [
        {
            'headword': sense.headword,
            'slug': sense.slug,
            'xml_id': sense.xml_id,
            'example_count': sense.examples.filter(artist=artist).count(),
            'examples': [build_example(example, published) for example in sense.examples.filter(artist=artist).order_by('release_date')]
        } for sense in artist.primary_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('-num_examples')[:5]
    ]

    featured_senses = [
        {
            'headword': sense.headword,
            'slug': sense.slug,
            'xml_id': sense.xml_id,
            'example_count': sense.examples.filter(feat_artist=artist).count(),
            'examples': [build_example(example, published) for example in sense.examples.filter(feat_artist=artist).order_by('release_date')]
        } for sense in artist.featured_senses.filter(publish=True).annotate(num_examples=Count('examples')).order_by('num_examples')[:5]
    ]

    entity_examples = []
    if entity_results:
        entity_examples = [build_example(example, published) for example in entity_results[0].examples.all()]

    image = check_for_image(artist.slug, 'artists', 'full')
    thumb = check_for_image(artist.slug, 'artists', 'thumb')
    name = reformat_name(artist.name)
    primary_sense_count = artist.primary_senses.filter(publish=True).count()
    featured_sense_count = artist.featured_senses.filter(publish=True).count()

    context = {
        'artist': name,
        'slug': artist.slug,
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
        'also_known_as': [{
            'artist': aka.name,
            'slug': aka.slug
        } for aka in artist.also_known_as.all()]
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def domain(request, domain_slug):
    template = loader.get_template('dictionary/domain.html')
    domain = get_object_or_404(Domain, slug=domain_slug)
    sense_objects = domain.senses.filter(publish=True).order_by('headword')
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    senses = [build_sense_preview(sense, published) for sense in sense_objects]
    senses_data = [{"word": sense.headword, "weight": sense.examples.count()} for sense in sense_objects]
    data = [sense.headword for sense in sense_objects]
    context = {
        'domain': un_camel_case(domain.name),
        'slug': domain_slug,
        'senses': senses,
        'senses_data': json.dumps(senses_data),
        'published_entries': published,
        'image': check_for_image(domain.slug, 'domains', 'full'),
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


@cache_control(max_age=3600)
def entry(request, headword_slug):
    if '#' in headword_slug:
        slug = headword_slug.split('#')[0]
    else:
        slug = headword_slug
    template = loader.get_template('dictionary/entry.html')

    entry = get_object_or_404(Entry, slug=slug, publish=True)
    published = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    include_form = request.user.is_authenticated()
    include_all_senses = False
    senses = [build_sense(sense, published, include_all_senses, include_form) for sense in entry.get_senses_ordered_by_example_count()]
    context = {
        'headword': entry.headword,
        'slug': slug,
        'title': entry.headword[0].upper() + entry.headword[1:],
        'image': senses[0]['image'],
        'pub_date': entry.pub_date,
        'last_updated': entry.last_updated,
        'senses': senses,
        'published_entries': published
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def index(request):
    template = loader.get_template('dictionary/index.html')
    entry_count = Entry.objects.filter(publish=True).count()
    sense_count = Sense.objects.filter(publish=True).count()
    example_count = Example.objects.all().count()
    artist_count = Artist.objects.all().count()
    recently_updated = [build_entry_preview(e) for e in Entry.objects.filter(publish=True).order_by('last_updated')[:5]]
    recently_published = [build_entry_preview(e) for e in Entry.objects.filter(publish=True).order_by('-pub_date')[:5]]
    context = {
        "entry_count": entry_count,
        "sense_count": sense_count,
        "example_count": example_count,
        "artist_count": artist_count,
        "recently_updated": recently_updated,
        "recently_published": recently_published
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def place(request, place_slug):
    place = get_object_or_404(Place, slug=place_slug)
    template = loader.get_template('dictionary/place.html')

    published = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    entity_results = NamedEntity.objects.filter(pref_label_slug=place_slug)
    examples = []

    artists = collect_place_artists(place, [])

    artists_with_image = [artist for artist in artists if '__none.png' not in artist['image']]
    artists_without_image = [artist for artist in artists if '__none.png' in artist['image']]

    contains = [{'name': abbreviate_place_name(c.name), 'slug': c.slug} for c in place.contains.order_by('name')]
    within = {}
    if ', ' in place.full_name:
        w_name = ', '.join(place.full_name.split(', ')[1:])
        w_slug = slugify(w_name)
        within = {'name': abbreviate_place_name(w_name), 'slug': w_slug}


    # TODO: reorder examples by release_date in case of multiple entities
    if len(entity_results) >= 1:
        for entity in entity_results:
            examples += [build_example(example, published, rf=True) for example in entity.examples.order_by('release_date')]

    context = {
        'place': place.name,
        'place_name_full': place.full_name,
        'slug': place.slug,
        'contains': contains,
        'within': within,
        'num_artists': len(artists),
        'artists_with_image': artists_with_image,
        'artists_without_image': artists_without_image,
        'image': check_for_image(place.slug, 'places', 'full'),
        'examples': sorted(examples, key=itemgetter('release_date'))[:NUM_QUOTS_TO_SHOW],
        'num_examples': len(examples)
    }
    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
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
    published_entries = Entry.objects.filter(publish=True).values_list('headword', flat=True)
    published_entry_slugs = Entry.objects.filter(publish=True).values_list('slug', flat=True)
    artist_slugs = [artist.slug for artist in Artist.objects.all()]

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

        if query_slug in published_entry_slugs:
            return redirect('entry', headword_slug=query_slug)
        elif query_slug in artist_slugs:
            return redirect('artist', artist_slug=query_slug)
        elif alt_query_slug and alt_query_slug in published_entry_slugs:
            return redirect('entry', headword_slug=alt_query_slug)
        elif alt_query_slug and alt_query_slug in artist_slugs:
            return redirect('artist', artist_slug=alt_query_slug)
        else:
            sense_query = build_query(query_string, ['lyric_text'])
            result_count = Example.objects.filter(sense_query).order_by('-release_date').count()
            example_results = [build_example(example, published=published_entries, rf=True) for example in Example.objects.filter(sense_query).order_by('-release_date')[:100]]
            context['query'] = query_string
            context['examples'] = example_results
            context['result_count'] = result_count
            context['the_rest'] = (result_count - 100) if (result_count > 100) else 0


    other_entries = []
    if 'result_count' in context and context['result_count'] < 1 or 'result_count' not in context:
        for i in range(3):
            r = Entry.objects.filter(publish=True).order_by('?').first()
            other_entries.append(r)
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


# @require_http_methods(['POST'])
# def sense(request, id):
#     form = SenseForm(request.POST)
#     if form.is_valid():
#         sense = Sense.objects.get(id=id)
#         sense.headword = form.cleaned_data['headword']
#         sense.xml_id = form.cleaned_data['xml_id']
#         sense.part_of_speech = form.cleaned_data["part_of_speech"]
#         sense.definition = form.cleaned_data["definition"]
#         sense.etymology = form.cleaned_data["etymology"]
#         sense.notes = form.cleaned_data["notes"]
#         sense.save()


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
    published_entries = Entry.objects.filter(publish=True).values_list('headword', flat=True)
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
        "examples": [build_example(example, published_entries, rf=True) for example in song.examples.all()],
        "same_dates": same_dates,
        "form": None
    }

    if request.user.is_authenticated():
        context['form'] = form

    return HttpResponse(template.render(context, request))


@cache_control(max_age=3600)
def stats(request):

    LIST_LENGTH = 5

    published_headwords = Entry.objects.filter(publish=True).values_list('headword', flat=True)

    entry_count = Entry.objects.filter(publish=True).count()
    sense_count = Sense.objects.filter(publish=True).count()
    example_count = Example.objects.all().count()
    best_attested_senses = [sense for sense in Sense.objects.annotate(num_examples=Count('examples')).order_by('-num_examples')[:LIST_LENGTH]]
    best_attested_sense_count = best_attested_senses[0].num_examples
    best_attested_domains = [domain for domain in Domain.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')[:LIST_LENGTH]]
    best_attested_semantic_classes = [semantic_class for semantic_class in SemanticClass.objects.annotate(num_senses=Count('senses')).order_by('-num_senses')[:LIST_LENGTH]]
    most_cited_songs = [song for song in Song.objects.annotate(num_examples=Count('examples')).order_by('-num_examples')[:LIST_LENGTH]]
    most_cited_song_count = most_cited_songs[0].num_examples
    most_mentioned_places = [e for e in NamedEntity.objects.filter(entity_type='place').annotate(num_examples=Count('examples')).order_by('-num_examples')[:LIST_LENGTH]]
    most_mentioned_artists = [e for e in NamedEntity.objects.filter(entity_type='artist').annotate(num_examples=Count('examples')).order_by('-num_examples')[:LIST_LENGTH]]
    most_cited_artists = [artist for artist in Artist.objects.annotate(num_cites=Count('primary_examples')).order_by('-num_cites')]
    examples_date_ascending = Example.objects.order_by('release_date')
    examples_date_descending = Example.objects.order_by('-release_date')
    seventies = Example.objects.filter(release_date__range=["1970-01-01", "1979-12-31"]).count()
    eighties = Example.objects.filter(release_date__range=["1980-01-01", "1989-12-31"]).count()
    nineties = Example.objects.filter(release_date__range=["1990-01-01", "1999-12-31"]).count()
    noughties = Example.objects.filter(release_date__range=["2000-01-01", "2009-12-31"]).count()
    twenty_tens = Example.objects.filter(release_date__range=["2010-01-01", "2019-12-31"]).count()
    decade_max = max([seventies, eighties, nineties, noughties, twenty_tens])
    places = [place for place in Place.objects.annotate(num_artists=Count('artists')).order_by('-num_artists')[:LIST_LENGTH]]
    domain_count = best_attested_domains[0].num_senses
    semantic_class_count = best_attested_semantic_classes[0].num_senses
    place_count = count_place_artists(places[0], [0])
    place_mention_count = most_mentioned_places[0].num_examples
    artist_mention_count = most_mentioned_artists[0].num_examples
    artist_cite_count = most_cited_artists[0].num_cites

    template = loader.get_template('dictionary/stats.html')

    WIDTH_ADJUSTMENT = 5

    context = {
        'num_entries': entry_count,
        'num_senses': sense_count,
        'num_examples': example_count,
        'best_attested_senses': [
            {
                'headword': sense.headword,
                'slug': sense.slug,
                'anchor': sense.xml_id,
                'definition': sense.definition,
                'num_examples': sense.num_examples,
                'width': (sense.num_examples / best_attested_sense_count) * 100 - WIDTH_ADJUSTMENT

            } for sense in best_attested_senses
            ],
        'best_attested_domains': [
            {
                'name': domain.name,
                'slug': domain.slug,
                'num_senses': domain.num_senses,
                'width': (domain.num_senses / domain_count) * 100 - WIDTH_ADJUSTMENT

            } for domain in best_attested_domains
            ],
        'best_attested_semantic_classes': [
            {
                'name': semantic_class.name,
                'slug': semantic_class.slug,
                'num_senses': semantic_class.num_senses,
                'width': (semantic_class.num_senses / semantic_class_count) * 100 - WIDTH_ADJUSTMENT

            } for semantic_class in best_attested_semantic_classes
            ],
        'most_cited_songs': [
            {
                'title': song.title,
                'slug': song.slug,
                'artist_name': song.artist_name,
                'artist_slug':song.artist_slug,
                'num_examples': song.num_examples,
                'width': (song.num_examples / most_cited_song_count) * 100 - WIDTH_ADJUSTMENT
            } for song in most_cited_songs
            ],
        'most_mentioned_places': [
            {
                'name': e.name,
                'slug': e.pref_label_slug,
                'pref_label': e.pref_label,
                'entity_type': e.entity_type,
                'num_examples': e.num_examples,
                'width': (e.num_examples / place_mention_count) * 100 - WIDTH_ADJUSTMENT
            } for e in most_mentioned_places
            ],
        'most_cited_artists': [
            {
                'name': artist.name,
                'slug': artist.slug,
                'image': check_for_image(artist.slug, 'artists', 'thumb'),
                'count': artist.num_cites,
                'width': (artist.num_cites / artist_cite_count) * 100 - WIDTH_ADJUSTMENT
            } for artist in most_cited_artists[:LIST_LENGTH+1]
            ],
        'most_mentioned_artists': [
            {
                'name': e.pref_label,
                'slug': e.pref_label_slug,
                'image': check_for_image(e.pref_label_slug, 'artists', 'thumb'),
                'pref_label': e.pref_label,
                'entity_type': e.entity_type,
                'num_examples': e.num_examples,
                'width': (e.num_examples / artist_mention_count) * 100 - WIDTH_ADJUSTMENT
            } for e in most_mentioned_artists
            ],
        'num_artists': len(most_cited_artists),
        'num_places': len(places),
        'best_represented_places': [
            {
                'name': p.name.split(', ')[0],
                'slug': p.slug,
                'num_artists': count_place_artists(p, [0]),
                'width': (count_place_artists(p, [0]) / place_count) * 100 - WIDTH_ADJUSTMENT
            } for p in places
            ],
        'earliest_date': {'example': [build_example(date, published_headwords) for date in examples_date_ascending[:LIST_LENGTH]]},
        'latest_date': {'example': [build_example(date, published_headwords) for date in examples_date_descending[:LIST_LENGTH]]},
        'num_seventies': seventies,
        'seventies_width': (seventies / decade_max) * 100,
        'num_eighties': eighties,
        'eighties_width': (eighties / decade_max) * 100 - WIDTH_ADJUSTMENT,
        'num_nineties': nineties,
        'nineties_width': (nineties / decade_max) * 100 - WIDTH_ADJUSTMENT,
        'num_noughties': noughties,
        'noughties_width': (noughties / decade_max) * 100 - WIDTH_ADJUSTMENT,
        'num_twenty_tens': twenty_tens,
        'twenty_tens_width': (twenty_tens / decade_max) * 100 - WIDTH_ADJUSTMENT
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
