from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse
from .models import Entry, Artist, NamedEntity, Domain


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
    results = Entry.objects.filter(slug=slug)
    template = loader.get_template('dictionary/entry.html')
    if len(results) == 1:
        entry = results[0]
        sense_objects = entry.senses.all()
        senses = [build_sense(sense) for sense in sense_objects]
        published = [entry.headword for entry in Entry.objects.filter(publish=True)]
        context = {
            'index': index,
            'entry': entry,
            'senses': senses,
            'published_entries': published
        }
        return HttpResponse(template.render(context, request))
    else:
        print('Found {} results for the slug: {}'.format(len(results), headword_slug))


def build_sense(sense_object):
    result = {
        "sense": sense_object,
        "domains": sense_object.domains.order_by('name'),
        "examples": sense_object.examples.order_by('release_date'),
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
    }
    return result


def artist(request, artist_slug):
    index = build_index()
    results = Artist.objects.filter(slug=artist_slug)
    entity_results = NamedEntity.objects.filter(pref_label_slug=artist_slug)
    template = loader.get_template('dictionary/artist.html')
    if len(results) == 1:
        artist = results[0]
        entity_senses = []
        if len(entity_results) >= 1:
            for entity in entity_results:
                entity_senses += [{'name': entity.name, 'sense': sense, 'examples': sense.examples.filter(features_entities=entity).order_by('release_date')} for sense in entity.mentioned_at_senses.all()]

        primary_senses = [{'sense': sense, 'examples': sense.examples.filter(artist=artist).order_by('release_date')} for sense in artist.primary_senses.all()]
        featured_senses = [{'sense': sense, 'examples': sense.examples.filter(feat_artist=artist).order_by('release_date')} for sense in artist.featured_senses.all()]
        context = {
            'index': index,
            'artist': artist,
            'primary_senses': primary_senses,
            'featured_senses': featured_senses,
            'entity_senses': entity_senses,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(artist_slug))


def entity(request, entity_slug):
    index = build_index()
    results = NamedEntity.objects.filter(slug=entity_slug)
    template = loader.get_template('dictionary/named_entity.html')

    if len(results) == 1:
        entity = results[0]
        if entity.entity_type == 'artist':
            return redirect('/artists/' + entity.pref_label_slug)
        else:
            senses = [{'sense': sense, 'examples': sense.examples.filter(features_entities=entity).order_by('release_date')} for sense in entity.mentioned_at_senses.all()]

            context = {
                'index': index,
                'entity': entity,
                'senses': senses,
            }
            return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(entity_slug))



def domain(request, domain_slug):
    index = build_index()
    results = Domain.objects.filter(slug=domain_slug)
    template = loader.get_template('dictionary/domain.html')
    if len(results) == 1:
        domain = results[0]
        senses = domain.senses.order_by('headword')

        context = {
            'index': index,
            'domain': domain,
            'senses': senses,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(domain_slug))


