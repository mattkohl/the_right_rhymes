import decimal
import os
import random
import re
import logging
from operator import itemgetter
from geopy.geocoders import Nominatim

from django.db.models import Q, Count
import dictionary.models


logger = logging.getLogger(__name__)


NUM_QUOTS_TO_SHOW = 3

geolocator = Nominatim()
geocache = []


def normalize_query(query_string,
                    find_terms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    norm_space=re.compile(r'\s{2,}').sub):
    return [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(query_string)]


def build_query(query_string, search_fields, normalize=False):
    query = None
    if normalize:
        terms = normalize_query(query_string)
    else:
        terms = [query_string]
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
    slug = re.sub("\*", "", slug)
    slug = re.sub("#", "number", slug)
    slug = re.sub("%", "percent", slug)
    slug = re.sub("&amp;", "and", slug)
    slug = re.sub("&", "and", slug)
    slug = re.sub("\+", "and", slug)

    slug = re.sub("é", "e", slug)
    slug = re.sub("ó", "o", slug)
    slug = re.sub("á", "a", slug)
    slug = re.sub("@", "at", slug)
    slug = re.sub("½", "half", slug)
    slug = re.sub("ō", "o", slug)

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


def move_definite_article_to_end(name):
    if name.lower().startswith('the ') and len(name) > 4:
        return name[4:] + ' the'
    return name


def un_camel_case(name):
    n = name
    if n[0].islower():
        n = n[0].upper() + n[1:]
    tokens = re.findall('[A-Z][^A-Z]*', n)
    return ' '.join(tokens)


def build_place(place_object, include_artists=False):
    result = {
        "name": place_object.name,
        "full_name": place_object.full_name,
        "slug": place_object.slug,
    }
    if include_artists:
        artists = collect_place_artists(place_object, [])
        result['artists_with_image'] = [artist for artist in artists if '__none.png' not in artist['image']]
        result['artists_without_image'] = [artist for artist in artists if '__none.png' in artist['image']]

    if place_object.longitude and place_object.latitude:
        result["longitude"] = place_object.longitude
        result["latitude"] = place_object.latitude

    return result


def build_artist(artist_object, require_origin=False, count=1):
    result = {
        "name": reformat_name(artist_object.name),
        "slug": artist_object.slug,
        "image": check_for_image(artist_object.slug, 'artists', 'thumb')
    }
    origin_results = artist_object.origin.all()
    if origin_results:
        origin_object = origin_results[0]
        if origin_object.longitude and origin_object.latitude:
            result['origin'] = {
                "name": origin_object.name,
                 "slug": origin_object.slug,
                 "longitude": origin_object.longitude,
                 "latitude": origin_object.latitude
            }

    result.update({"count": count})
    if require_origin:
        if 'origin' in result:
            return result
        return None
    else:
        return result


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


def build_sense(sense_object, published, full=False, build_form=False):
    example_results = sense_object.examples.order_by('release_date')
    if full:
        examples = [build_example(example, published) for example in example_results]
    else:
        examples = [build_example(example, published) for example in example_results[:NUM_QUOTS_TO_SHOW]]
    sense_slug = slugify(sense_object.headword + '_' + sense_object.xml_id)
    sense_image = check_for_image(sense_slug, 'senses', 'full')
    if "__none" in sense_image:
        sense_image = None
    artist_slug, artist_name, image = assign_artist_image(examples)
    form = None

    synset = sense_object.synset.first()
    if synset:
        synonyms = [sense_to_xref_dict(s) for s in synset.senses.order_by('headword') if s != sense_object]
    else:
        synonyms = [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Synonym").order_by('xref_word')]

    result = {
        "headword": sense_object.headword,
        "part_of_speech": sense_object.part_of_speech,
        "xml_id": sense_object.xml_id,
        "definition": sense_object.definition,
        "notes": sense_object.notes,
        "etymology": sense_object.etymology,
        "domains": [o.to_dict() for o in sense_object.domains.order_by('name')],
        "regions": [o.to_dict() for o in sense_object.regions.order_by('name')],
        "semantic_classes": [o.to_dict() for o in sense_object.semantic_classes.order_by('name')],
        "examples": examples,
        "num_examples": len(example_results),
        "synonyms": synonyms,
        "antonyms": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Antonym").order_by('xref_word')],
        "meronyms": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Meronym").order_by('xref_word')],
        "holonyms": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Holonym").order_by('xref_word')],
        "derivatives": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Derivative").order_by('xref_word')],
        "ancestors": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Derives From").order_by('xref_word')],
        "instance_of": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Instance Of").order_by('xref_word')],
        "instances": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Instance").order_by('xref_word')],
        "related_concepts": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Related Concept").order_by('xref_word')],
        "related_words": [o.to_dict() for o in sense_object.xrefs.filter(xref_type="Related Word").order_by('xref_word')],
        "rhymes": [o.to_dict() for o in sense_object.sense_rhymes.order_by('-frequency')],
        "collocates": [o.to_dict() for o in sense_object.collocates.order_by('-frequency')],
        "artist_slug": artist_slug,
        "artist_name": artist_name,
        "sense_image": sense_image,
        "image": image,
        "form": form
    }
    return result


def sense_to_xref_dict(sense_object):
    return {
        "xref_word": sense_object.headword,
        "xref_type": "synonym",
        "target_lemma": sense_object.headword,
        "target_slug": slugify(sense_object.headword),
        "target_id": sense_object.xml_id,
    }


def build_sense_preview(sense_object, published):
    first_example = sense_object.examples.order_by('release_date').first()
    result = {
        "headword": sense_object.headword,
        "slug": sense_object.slug,
        "part_of_speech": sense_object.part_of_speech,
        "definition": sense_object.definition,
        "xml_id": sense_object.xml_id,
        "example_count": sense_object.examples.count(),
        "first_example": first_example,
        "image": check_for_image(first_example.artist_slug)
    }
    return result


def build_xref(xref_object):

    result = {
        "xref_word": xref_object.xref_word,
        "xref_type": xref_object.xref_type,
        "target_lemma": xref_object.target_lemma,
        "target_slug": xref_object.target_slug,
        "target_id": xref_object.target_id,
        "frequency": xref_object.frequency,
        "position": xref_object.position
    }
    return result


def build_collocate(collocate_object):
    result = {
        "collocate_lemma": collocate_object.collocate_lemma,
        "source_sense_xml_id": collocate_object.source_sense_xml_id,
        "target_slug": collocate_object.target_slug,
        "target_id": collocate_object.target_id,
        "frequency": collocate_object.frequency
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
        "lyric": lyric,
        "linked_lyric": add_links(lyric, lyric_links, published)
    }
    return result


def build_beta_example(example_object):
    lyric = example_object.lyric_text
    lyric_links = example_object.lyric_links.order_by('position')
    result = {
        "primary_artists": [build_artist(a) for a in example_object.artist.order_by('name')],
        "title": example_object.song_title,
        "album": example_object.album,
        "release_date": str(example_object.release_date),
        "release_date_string": example_object.release_date_string,
        "featured_artists": [build_artist(feat) for feat in example_object.feat_artist.order_by('name')],
        "text": lyric,
        "links": [{
            "text": link.link_text,
            "type": link.link_type,
            "offset": link.position,
            "target_lemma": link.target_lemma,
            "target_slug": link.target_slug,
        } for link in lyric_links]
    }
    return result


def build_song(song_object, rf=False):
    result = {
        "primary_artists": [build_artist(a) for a in song_object.artist.order_by('name')],
        "title": song_object.title,
        "slug": slugify(song_object.artist_name + ' ' + song_object.title),
        "album": song_object.album,
        "release_date": str(song_object.release_date),
        "release_date_string": song_object.release_date_string,
        "featured_artists": [build_artist(feat) for feat in song_object.feat_artist.order_by('name')],
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


def add_links(lyric, links, published):
    linked_lyric = lyric
    buffer = 0
    for link in links:
        try:
            lyric.index(link.link_text)
        except Exception as e:
            continue
        else:
            start = link.position + buffer
            end = start + len(link.link_text)
            hw_slug = link.target_slug.split("#")[0]
            if link.link_type == 'rhyme' and hw_slug in published:
                a = '<a href="/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            elif link.link_type == 'rhyme':
                a = '<a href="/rhymes/{}">{}</a>'.format(link.target_slug, link.link_text)
                linked_lyric = inject_link(linked_lyric, start, end, a)
                buffer += (len(a) - len(link.link_text))
            if link.link_type == 'xref' and hw_slug in published:
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


def count_place_artists(place_object, counts=[]):
    counts.extend([place_object.artists.all().count()])
    contains = place_object.contains.all()
    if contains:
        for contained in contains:
            count_place_artists(contained, counts)
    return sum(counts)


def make_label_from_camel_case(text):
    if text[0].lower():
        text = text[0].upper() + text[1:]
    tokens = re.findall('[A-Z][^A-Z]*', text)
    return ' '.join(tokens)


def dedupe_rhymes(rhymes_intermediate):
    for r in rhymes_intermediate:
        example_cache = set()
        rhymes_deduped = []
        for example in rhymes_intermediate[r]['examples']:
            if example['lyric'] not in example_cache:
                example_cache.add(example['lyric'])
                rhymes_deduped.append(example)
        rhymes_intermediate[r]['examples'] = rhymes_deduped


def sameas_places(master_name, dupe_name):
    dupe_slug = slugify(dupe_name)
    master_slug = slugify(move_definite_article_to_end(master_name))
    master = dictionary.models.Place.objects.filter(slug=master_slug).first()
    dupe = dictionary.models.Place.objects.filter(slug=dupe_slug).first()
    ne_dupe = dictionary.models.NamedEntity.objects.filter(slug=dupe_slug).first()
    ne_master = dictionary.models.NamedEntity.objects.filter(slug=master_slug).first()
    ll_dupes = dictionary.models.LyricLink.objects.filter(target_slug=dupe_slug)
    if master and dupe:

        artists = dupe.artists.all()
        for artist in artists:
            msg = 'Reassigning {} origin from {} to {}'.format(artist.name, dupe.full_name, master.full_name)
            logger.info(msg)
            artist.origin.remove(dupe)
            artist.origin.add(master)
            artist.save()

    if ne_dupe and (ne_master or master):
        if not ne_master:
            ne_master = dictionary.models.NamedEntity(name=master.name,
                                                      slug=master.slug,
                                                      pref_label=master.full_name,
                                                      pref_label_slug=master.slug,
                                                      entity_type='place')
            ne_master.save()

        for example in ne_dupe.examples.all():
            msg = 'Reassigning {} featured entity from {} to {}'.format(example, ne_dupe.pref_label, ne_master.pref_label)
            logger.info(msg)
            example.features_entities.remove(ne_dupe)
            example.features_entities.add(ne_master)
            example.save()

        for example in dictionary.models.Example.objects.filter(features_entities__in=[ne_dupe]):
            msg = 'Reassigning {} featured entity from {} to {}'.format(example, ne_dupe.pref_label, ne_master.pref_label)
            logger.info(msg)
            example.features_entities.remove(ne_dupe)
            example.features_entities.add(ne_master)
            example.save()

        for sense in dictionary.models.Sense.objects.filter(features_entities__in=[ne_dupe]):
            msg = 'Reassigning {} featured entity from {} to {}'.format(sense, ne_dupe.pref_label, ne_master.pref_label)
            logger.info(msg)
            sense.features_entities.remove(ne_dupe)
            sense.features_entities.add(ne_master)
            sense.save()

    for ll in ll_dupes:
        msg = 'Reassigning lyric link target {} from {} to {}'.format(ll, dupe_slug, master_slug)
        logger.info(msg)
        ll.target_slug = master_slug
        ll.save()

    return dupe, ne_dupe


def sameas_artists(master_name, dupe_name):
    dupe_slug = slugify(dupe_name)
    master_slug = slugify(move_definite_article_to_end(master_name))
    master = dictionary.models.Artist.objects.filter(slug=master_slug).first()
    dupe = dictionary.models.Artist.objects.filter(slug=dupe_slug).first()
    if master and dupe:

        origin = dupe.origin.first()
        if origin:
            msg = 'Reassigning origin {} from {} to {}'.format(origin, dupe.name, master.name)
            logger.info(msg)
            origin.artists.remove(dupe)
            origin.artists.add(master)
            origin.save()

        primary_examples = dupe.primary_examples.all()
        for example in primary_examples:
            msg = 'Reassigning primary example {} from {} to {}'.format(example, dupe.name, master.name)
            logger.info(msg)
            example.artist.remove(dupe)
            example.artist.add(master)
            example.artist_name = master.name
            example.artist_slug = master.slug
            example.save()

        primary_senses = dupe.primary_senses.all()
        for sense in primary_senses:
            msg = 'Reassigning primary sense {} from {} to {}'.format(sense, dupe.name, master.name)
            logger.info(msg)
            logger.info(msg)
            sense.cites_artists.remove(dupe)
            sense.cites_artists.add(master)
            sense.save()

        featured_examples = dupe.featured_examples.all()
        for example in featured_examples:
            msg = "Reassigning featured example {} from {} to {}".format(example, dupe.name, master.name)
            logger.info(msg)
            example.feat_artist.remove(dupe)
            example.feat_artist.add(master)
            example.save()

        featured_senses = dupe.featured_senses.all()
        for sense in featured_senses:
            msg = "Reassigning primary sense {} from {} to {}".format(sense, dupe.name, master.name)
            logger.info(msg)
            dupe.featured_senses.remove(sense)
            master.featured_senses.add(sense)
            master.save()

        primary_songs = dupe.primary_songs.all()
        for song in primary_songs:
            msg = "Reassigning primary song {} from {} to {}".format(song, dupe.name, master.name)
            logger.info(msg)
            song.artist.remove(dupe)
            song.artist.add(master)
            song.artist_name = master.name
            song.artist_slug = master.slug
            song.save()

        featured_songs = dupe.featured_songs.all()
        for song in featured_songs:
            msg = "Reassigning featured song {} from {} to {}".format(song, dupe.name, master.name)
            logger.info(msg)
            song.feat_artist.remove(dupe)
            song.feat_artist.add(master)
            song.save()

        aka = dupe.also_known_as.all()
        for artist in aka:
            msg = "Reassigning aka {} from {} to {}".format(artist, dupe.name, master.name)
            logger.info(msg)
            artist.also_known_as.remove(dupe)
            artist.also_known_as.add(master)
            artist.save()

        logger.info('Done!')
        return dupe


def sameas_entities(master_name, dupe_name):
    dupe_slug = slugify(dupe_name)
    master_slug = slugify(move_definite_article_to_end(master_name))
    master = dictionary.models.NamedEntity.objects.filter(slug=master_slug).first()
    dupe = dictionary.models.NamedEntity.objects.filter(slug=dupe_slug).first()
    if master and dupe:
        for sense in dupe.mentioned_at_senses.all():
            msg = "Reassigning sense {} from {} to {}".format(sense, dupe.name, master.name)
            logger.info(msg)
            sense.features_entities.remove(dupe)
            sense.features_entities.add(master)
            sense.save()

        for example in dupe.examples.all():
            msg = "Reassigning example {} from {} to {}".format(example, dupe.name, master.name)
            logger.info(msg)
            example.features_entities.remove(dupe)
            example.features_entities.add(master)
            example.save()

        logger.info('Done!')
        return dupe


def sameas_lyric_links(master_name, dupe_name):
    dupe_slug = slugify(dupe_name)
    master_slug = slugify(move_definite_article_to_end(master_name))
    for link in dictionary.models.LyricLink.objects.filter(target_slug=dupe_slug):
        msg = "Reassigning lyric link {} from {} to {}".format(link, dupe_name, master_name)
        logger.info(msg)
        link.target_slug = master_slug
        link.save()


def geocode_place(place_name):

    logger.info('Geocoding: ' + place_name)
    try:
        coded = geolocator.geocode(place_name)
        longitude = coded.longitude
        latitude = coded.latitude
    except Exception as e:
        geocache.append(slugify(place_name))
        msg = 'Unable to geolocate {}: {}'.format(place_name, e)
        logger.warning(msg)
    else:
        return latitude, longitude


def extract_short_name(place_name):
    return place_name.split(', ')[0]


def extract_parent(place_name):
    if ',' in place_name:
        return ", ".join(place_name.split(', ')[1:])
    else:
        return None


def add_artist_origin_with_slugs(artist_slug=None, place_slug=None):
    """
    takes an artist slug and a place slug, drops all the artist's existing origin
    links, then adds that place as origin
    """
    if artist_slug is not None and place_slug is not None:
        try:
            a = dictionary.models.Artist.objects.get(slug=artist_slug)
            p = dictionary.models.Place.objects.get(slug=place_slug)
        except Exception as e:
            return e
        else:
            a.origin.clear()
            a.origin.add(p)
            return str(a) + " updated with origin " + str(p)
    return "Please give slugs for artist and place"


def fix_lyric_link_positions():
    """
    Some of the ingested lyrics with quot marks in them had links with positions off by 1.
    I think this was due to a bug in the XML transform. This function pulls those examples &
    links, then compares the link position against the example.lyric.index(link_text),
    preferring the index where different.

    queryset is limited to examples with " in lyric_text and featuring an entity
    """
    exx = dictionary.models.Example.objects.filter(lyric_text__icontains='"').exclude(features_entities__isnull=True)
    altered = []
    for e in exx:
        lyric = e.lyric_text
        links = e.lyric_links.order_by('position')
        for link in links:
            i = lyric.index(link.link_text)
            o = link.position
            if o != i:
                link.position = i
                link.save()
                altered.append({
                    "example_id": e.id,
                    "lyric": lyric,
                    "link_id": link.id,
                    "link_text": link.link_text,
                    "old_position": o,
                    "new_position": i
                })
    return altered


def get_or_create_place_from_full_name(full_name):
    """
    (Gets or) creates a place, including geocoding & adding regional container, e.g. "Texas contains Houston"

    :param full_name: comma-separated, complete up to country level, as in "Houston, Texas, USA"
    :return: a place object
    """
    slug = slugify(full_name)
    try:
        p = dictionary.models.Place.objects.get(slug=slug)
    except Exception as e:
        name = extract_short_name(full_name)
        try:
            lat, long = geocode_place(full_name)
        except Exception as e:
            p = dictionary.models.Place(full_name=full_name, name=name, slug=slug)
        else:
            p = dictionary.models.Place(full_name=full_name, name=name, slug=slug, latitude=lat, longitude=long)
        p.save()
        within = extract_parent(full_name)
        w = dictionary.models.Place.objects.get(slug=slugify(within))
        w.contains.add(p)
    return p


def gather_suspicious_lat_longs():
    """Finds places with 'usa' in slug that have erroneous lat & long"""
    return dictionary.models.Place.objects.filter(latitude__lt=0).filter(longitude__gt=0).filter(slug__endswith="usa")


def format_suspicious_lat_longs(suspects):
    return ["{} {}\t{}\t{}".format(i, e.latitude, e.longitude, e.slug) for i, e in enumerate(suspects)]


def swap_place_lat_long(place):
    place.latitude, place.longitude = place.longitude, place.latitude
    place.save()
    return place.latitude, place.longitude


def get_duplicate_lyric_texts():
    return dictionary.models.Example.objects.values('lyric_text').annotate(Count('id')).order_by().filter(id__count__gt=1)


def get_all_examples_with_lyric_text(text):
    return dictionary.models.Example.objects.filter(lyric_text=text)


def get_duplicate_lyric_links():
    from itertools import groupby
    exx = dictionary.models.Example.objects.annotate(Count('lyric_links')).filter(lyric_links__count__gt=1)
    for e in exx:
        positions = [link.position for link in e.lyric_links.all()]
        counts = [
            {"position": key, "count": len(list(group))} for key, group in groupby(positions)
        ]
        dupe_positions = [x["position"] for x in counts if x["count"] > 1]
        if dupe_positions:
            for p in dupe_positions:
                links = list(e.lyric_links.filter(position=p))
                msg = "{} {}".format(e, links)
                logger.info(msg)
                yield ([e] + links)


def right_wrong_lyric_link_positions():
    exx = dictionary.models.Example.objects.filter(lyric_text__icontains='"')
    for ex in exx:
        text = ex.lyric_text
        for link in ex.lyric_links.all():
            l_text = link.link_text
            i = text.index(l_text)
            if link.position != i and text.count(l_text) == 1 and link.position - 1 == i:
                logger.info(ex)
                link.position -= 1
                link.save()


def update_release_date(artist_name=None, album=None, new_release_date=None):
    if not artist_name or not album or not new_release_date:
        msg = "One of artist_name: {}, album: {}, or release_date: {} was None".format(artist_name, album, new_release_date)
        logger.error(msg)
        return

    candidates = list(dictionary.models.Song.objects.filter(artist_name=artist_name, album=album)) + list(dictionary.models.Example.objects.filter(artist_name=artist_name, album=album))
    for c in candidates:
        c.release_date = new_release_date
        c.release_date_string = new_release_date
        c.save()

    return candidates
