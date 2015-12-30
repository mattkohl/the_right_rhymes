from django.shortcuts import render
from django.http import HttpResponse
from .models import Entry, Artist, NamedEntity, Domain


def index(request):
    return HttpResponse("What up, G. You're at the dictionary index.")


def entry(request, headword_slug):
    results = Entry.objects.filter(slug=headword_slug)
    if len(results) == 1:
        result = results[0]
        return HttpResponse("You found the Entry: {}!".format(result.headword))
    else:
        return HttpResponse("Whoa, what is {}?".format(headword_slug))

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

