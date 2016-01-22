__author__ = 'MBK'

import re
import decimal
from django.db.models import Q


def normalize_query(query_string,
                    find_terms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    norm_space=re.compile(r'\s{2,}').sub):
    return [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(query_string)]


def build_query(query_string, search_fields):
    query = None
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})

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
    return slug