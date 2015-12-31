from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Entry, Artist, NamedEntity, Domain


def index(request):
    headword_list = Entry.objects.order_by('headword')
    template = loader.get_template('dictionary/index.html')
    context = {
        'headword_list': headword_list,
    }
    return HttpResponse(template.render(context, request))


def entry(request, headword_slug):
    results = Entry.objects.filter(slug=headword_slug)
    template = loader.get_template('dictionary/entry.html')
    if len(results) == 1:
        entry = results[0]
        sense_objects = entry.senses.all()
        senses = [{'sense': sense, 'examples': sense.examples.order_by('release_date')} for sense in sense_objects]
        context = {
            'entry': entry,
            'senses': senses
        }
        return HttpResponse(template.render(context, request))
    else:
        print('Found {} results for the slug: {}'.format(len(results), headword_slug))


def artist(request, artist_slug):
    results = Artist.objects.filter(slug=artist_slug)
    if len(results) == 1:
        result = results[0]
        return HttpResponse("You found the Artist: {}!".format(result.name))
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
