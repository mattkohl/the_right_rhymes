__author__ = 'MBK'

import re
from collections import OrderedDict
import xmltodict
from .models import Entry, Sense, Example


class XMLDict:

    def __init__(self, filename):
        self.filename = filename
        self.xml_string = self.read_xml_string()
        self.xml_dict = self.get_json()

    def read_xml_string(self):
        f = open(self.filename, 'rb')
        try:
            xml_string = f.read()
        except:
            raise Exception("Can't read in source XML")
        else:
            f.close()
            return xml_string

    def get_json(self):
        try:
            j = xmltodict.parse(self.xml_string)
        except:
            raise Exception("xmltodict can't parse that xml string")
        else:
            return j


class TRRDict:

    def __init__(self, xml_dict):
        self.xml_dict = xml_dict
        self.dictionary = self.get_dictionary()
        self.entries = self.get_entries()
        self.entry_count = len(self.entries)

    def __str__(self):
        return "Python dict representation of The Right Rhymes. Entry count: " + self.entry_count

    def get_dictionary(self):
        try:
            return self.xml_dict['dictionary']
        except:
            raise KeyError("No 'dictionary' key in xml_dict")

    def get_entries(self):
        try:
            entry_list = self.dictionary['entry']
        except:
            raise KeyError("No 'entry' key in xml_dict")
        else:
            return[TRREntry(entry_dict) for entry_dict in entry_list]


class TRREntry:

    def __init__(self, entry_dict):
        self.entry_dict = entry_dict
        self.headword = self.entry_dict['head']['headword']
        self.slug = slugify(self.headword)
        self.xml_id = self.entry_dict['@eid']
        self.publish = self.entry_dict['@publish']
        self.entry_object = self.add_to_db()
        self.extract_lexemes()

    def __str__(self):
        return self.headword

    def add_to_db(self):
        entry, created = Entry.objects.get_or_create(headword=self.headword,
                                                     slug=self.slug,
                                                     publish=self.publish,
                                                     json=self.entry_dict)
        return entry

    def extract_lexemes(self):
        lexemes = self.entry_dict['senses']
        if type(lexemes) is OrderedDict:
            self.process_lexeme(lexemes)
        if type(lexemes) is list:
            for l in lexemes:
                self.process_lexeme(l)

    def process_lexeme(self, lexeme):
        pos = lexeme['pos']
        if type(lexeme['sense']) is OrderedDict:
            self.process_sense(pos, lexeme['sense'])
        elif type(lexeme['sense']) is list:
            for s in lexeme['sense']:
                self.process_sense(pos, s)

    def process_sense(self, pos, sense):
        TRRSense(self.entry_object, self.headword, pos, sense)



class TRRSense:

    def __init__(self, entry_object, headword, pos, sense_dict):
        self.parent_entry = entry_object
        self.headword = headword
        self.pos = pos
        self.sense_dict = sense_dict
        self.xml_id = self.sense_dict['@id']
        self.sense_object = self.add_to_db()
        self.add_entry_relations()

    def __str__(self):
        return self.headword + ', ' + self.pos

    def add_to_db(self):
        sense, created = Sense.objects.get_or_create(headword=self.headword,
                                                     xml_id=self.xml_id,
                                                     part_of_speech=self.pos,
                                                     json=self.sense_dict)
        return sense

    def add_entry_relations(self):
        self.sense_object.parent_entry.add(self.parent_entry)
        self.parent_entry.senses.add(self.sense_object)



class TRRArtist:

    def __init__(self, name, origin=None):
        self.name = name
        self.origin = origin
        self.slug = slugify(self.name)

    def __str__(self):
        return self.name

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

