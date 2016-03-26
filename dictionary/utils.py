from operator import itemgetter
import os
import random
from dictionary.models import Entry

__author__ = 'MBK'

import re
import decimal
from django.db.models import Q


NUM_QUOTS_TO_SHOW = 3


def normalize_query(query_string,
                    find_terms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    norm_space=re.compile(r'\s{2,}').sub):
    return [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(query_string)]


def build_query(query_string, search_fields):
    query = None
    terms = normalize_query(query_string)
    for term in terms:
        escaped = re.escape(term)
        term = r'\y{}s?\y'.format(escaped)
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__iregex" % field_name: term})

            if or_query:
                or_query = or_query or q
            else:
                or_query = q
        if query:
            query = query and or_query
        else:
            query = or_query
    return query


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


def slugify(text):
    slug = text.strip().lower()
    if slug[0] == "'" or slug[0] == "-":
        slug = slug[1:]
    slug = re.sub("^[\-']]", "", slug)
    slug = re.sub("[\s\.]", "-", slug)
    slug = re.sub("[:/]", "", slug)
    slug = re.sub("\$", "s", slug)
    slug = re.sub("&amp;", "and", slug)
    slug = re.sub("&", "and", slug)
    slug = re.sub("'", "", slug)
    slug = re.sub(",", "", slug)
    slug = re.sub("-$", "", slug)
    slug = re.sub("\?", "", slug)
    slug = re.sub("[\(\)]", "", slug)
    return slug


def reformat_name(name):
    if name.lower().endswith(', the'):
        return 'The ' + name[:-5]
    return name


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


def build_artist(artist_object, require_origin=False):
    result = {
        "name": reformat_name(artist_object.name),
        "slug": artist_object.slug,
        "image": check_for_image(artist_object.slug, 'artists', 'thumb')
    }
    origin_results = artist_object.origin.all()
    if origin_results:
        origin_object = origin_results[0]
        if origin_object.longitude and origin_object.latitude:
            result["place_name"] = origin_object.name
            result["place_slug"] = origin_object.slug
            result["longitude"] = origin_object.longitude
            result["latitude"] = origin_object.latitude

    if require_origin:
        if 'place_name' in result:
            return result
        return None
    else:
        return result


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


def assign_artist_image(examples):
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
            image = check_for_image(artist_slug, 'artists', 'full')
        if image:
            return artist_slug, artist_name, image
        if count >= THRESHOLD:
            return '', '', ''
    return '', '', ''


def build_sense(sense_object, published, full=False):
    # published = [entry.headword for entry in Entry.objects.filter(publish=True)]
    example_results = sense_object.examples.order_by('release_date')
    if full:
        examples = [build_example(example, published) for example in example_results]
    else:
        examples = [build_example(example, published) for example in example_results[:NUM_QUOTS_TO_SHOW]]
    artist_slug, artist_name, image = assign_artist_image(examples)
    result = {
        "part_of_speech": sense_object.part_of_speech,
        "xml_id": sense_object.xml_id,
        "definition": sense_object.definition,
        "notes": sense_object.notes,
        "etymology": sense_object.etymology,
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
        "artist_slug": artist_slug,
        "artist_name": artist_name,
        "image": image
    }
    return result


def build_sense_preview(sense_object, published):
    result = {
        "sense": sense_object,
        "examples": [build_example(example, published) for example in sense_object.examples.order_by('release_date')][:1]
    }
    return result


def build_entry_preview(entry_object):
    result = {
        "headword": entry_object.headword,
        "slug": entry_object.slug,
        "pub_date": entry_object.pub_date,
        "last_updated": entry_object.last_updated,
    }
    return result


def build_example(example_object, published, rf=False):
    lyric = example_object.lyric_text
    lyric_links = example_object.lyric_links.order_by('position')
    result = {
        "artist_name": reformat_name(example_object.artist_name),
        "artist_slug": example_object.artist_slug,
        "song_title": example_object.song_title,
        "song_slug": slugify(example_object.artist_name + ' ' + example_object.song_title),
        "album": example_object.album,
        "release_date": str(example_object.release_date),
        "release_date_string": example_object.release_date_string,
        "featured_artists": [build_artist(feat) for feat in example_object.feat_artist.order_by('name')],
        "linked_lyric": add_links(lyric, lyric_links, published, rf)
    }
    return result


def build_timeline_example(example_object, published, rf=False):
    example = build_example(example_object, published, rf)
    url = check_for_image(example['artist_slug'], 'artists', 'full')
    thumb = check_for_image(example['artist_slug'], 'artists', 'thumb')
    year, month, day = example['release_date'].split('-')

    result = {
        "background": {
            "url": url
        },
        "media": {
            "thumbnail": thumb
        },
        "start_date": {
            "month": month,
            "day": day,
            "year": year
        },
        "text": {
            "headline": example['linked_lyric'],
            "text": '<a href="/artists/' + example['artist_slug'] + '">' + example['artist_name'] + '</a> - "<a href="/songs/' + example['song_slug'] + '">' + example['song_title'] + '</a>"'

        }
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
            if '#' in link.target_slug:
                lem_slug = link.target_slug.split('#')[0]
            else:
                lem_slug = link.target_slug
            if link.link_type == 'rf' and rf:
                a = '<a href="/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'rhyme':
                a = '<a href="/rhymes/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'xref' and lem_slug in published:
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


def check_for_image(slug, image_type='artists', folder='thumb'):
    jpg = 'dictionary/static/dictionary/img/{}/{}/{}.jpg'.format(image_type, folder, slug)
    png = 'dictionary/static/dictionary/img/{}/{}/{}.png'.format(image_type, folder, slug)
    images = []

    if image_type == 'places':
        print(jpg)
        print(png)

    if os.path.isfile(jpg.encode('utf-8').strip()):
        images.append(jpg.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if os.path.isfile(png.encode('utf-8').strip()):
        images.append(png.replace('dictionary/static/dictionary/', '/static/dictionary/'))
    if len(images) == 0:
        return '/static/dictionary/img/artists/{}/__none.png'.format(folder)
    else:
        return random.choice(images)


def abbreviate_place_name(place_name):
    if place_name.endswith(', USA'):
        tokens = place_name.split(', ')
        return tokens[0]
    else:
        return place_name


def reduce_ordered_list(seq, k):
    if not 0 <= k <= len(seq):
        raise ValueError('Required that 0 <= sample_size <= population_size')

    seq_len = len(seq)
    numbers_picked = 0
    for i, number in enumerate(seq):
        if i == 0 or i == seq_len-1:
            numbers_picked += 1
            yield number
        prob = (k - numbers_picked) / (seq_len - i)
        if random.random() < prob:
            yield number
            numbers_picked += 1


def collect_place_artists(place_object, artists):
    artists.extend([build_artist(artist) for artist in place_object.artists.all()])
    contains = place_object.contains.all()
    if contains:
        for contained in contains:
            collect_place_artists(contained, artists)
    return sorted(artists, key=itemgetter('name'))