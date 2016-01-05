from django.shortcuts import render
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
        context = {
            'index': index,
            'entry': entry,
            'senses': senses
        }
        return HttpResponse(template.render(context, request))
    else:
        print('Found {} results for the slug: {}'.format(len(results), headword_slug))


def build_sense(sense_object):
    result = {
        "sense": sense_object,
        "domains": sense_object.domains.order_by('name'),
        "synset": sense_object.synset.order_by('name'),
        "examples": sense_object.examples.order_by('release_date')
    }
    return result


def artist(request, artist_slug):
    index = build_index()
    results = Artist.objects.filter(slug=artist_slug)
    template = loader.get_template('dictionary/artist.html')
    if len(results) == 1:
        artist = results[0]
        primary_senses = [{'sense': sense, 'examples': sense.examples.filter(artist=artist).order_by('release_date')} for sense in artist.primary_senses.all()]
        featured_senses = [{'sense': sense, 'examples': sense.examples.filter(feat_artist=artist).order_by('release_date')} for sense in artist.featured_senses.all()]
        context = {
            'index': index,
            'artist': artist,
            'primary_senses': primary_senses,
            'featured_senses': featured_senses,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Whoa, what is {}?".format(artist_slug))


def entity(request, entity_slug):
    results = NamedEntity.objects.filter(slug=entity_slug)
    if len(results) == 1:
        result = results[0]
        if result.name == result.pref_label:
            return HttpResponse("You found the Named Entity: {}!".format(result.name))
        else:
            return HttpResponse("You found the Named Entity: {}, aka {}".format(result.name, result.pref_label))
    else:
        return HttpResponse("Whoa, what is {}?".format(entity_slug))


def domain(request, domain_slug):
    results = Domain.objects.filter(slug=domain_slug)
    if len(results) == 1:
        result = results[0]
        return HttpResponse("You found the Domain: {}".format(result.name))
    else:
        return HttpResponse("Whoa, what is {}?".format(domain_slug))
