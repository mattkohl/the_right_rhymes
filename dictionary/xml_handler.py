__author__ = 'MBK'

import re
from collections import OrderedDict
import xmltodict
from .models import Entry, Sense, Example, Artist, Domain, SynSet, NamedEntity, Xref, Collocate, Rhyme


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
            j = xmltodict.parse(self.xml_string, force_list=('senses', 'forms', 'sense', 'definition', 'collocate', 'xref', 'note', 'etym', 'rhyme'))
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
        self.letter = self.get_letter()
        self.xml_id = self.entry_dict['@eid']
        self.publish = self.entry_dict['@publish']
        self.entry_object = self.add_to_db()
        self.update_entry()
        self.extract_lexemes()

    def __str__(self):
        return self.headword

    def get_letter(self):
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        if self.slug.startswith('the-'):
            key = self.slug[4]
        else:
            key = self.slug[0]

        if key in ABC:
            return key
        else:
            return '#'

    def add_to_db(self):
        print('Adding Entry:', self.headword)
        entry, created = Entry.objects.get_or_create(headword=self.headword,
                                                     slug=self.slug)
        return entry

    def update_entry(self):
        self.entry_object.publish = self.publish
        self.entry_object.json = self.entry_dict
        self.entry_object.letter = self.letter
        self.entry_object.save()

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
        self.slug = slugify(self.headword) + '#' + self.xml_id
        self.definition = self.extract_definition()
        self.etymology = self.extract_etymology()
        self.notes = self.extract_notes()
        self.sense_object = self.add_to_db()
        self.update_sense()
        self.domains = []
        self.extract_domains()
        self.collocates = []
        self.extract_collocates()
        self.rhymes = []
        self.extract_rhymes()
        self.synset = []
        self.extract_synset()
        self.xrefs = []
        self.extract_xrefs()
        self.examples = [e for e in self.extract_examples()]
        self.add_relations()

    def __str__(self):
        return self.headword + ', ' + self.pos

    def add_to_db(self):
        print('Adding Sense:', self.headword, '-', self.pos, '(' + self.xml_id + ')')
        sense_object, created = Sense.objects.get_or_create(headword=self.headword,
                                                            xml_id=self.xml_id,
                                                            part_of_speech=self.pos)
        return sense_object

    def update_sense(self):
        self.sense_object.json = self.sense_dict
        self.sense_object.definition = self.definition
        self.sense_object.etymology = self.etymology
        self.sense_object.notes = self.notes
        self.sense_object.slug = self.slug
        self.sense_object.save()

    def extract_definition(self):
        return '; '.join([definition['text'] for definition in self.sense_dict['definition']])

    def extract_etymology(self):
        if 'etym' in self.sense_dict:
            return '; '.join([etymology['text'] for etymology in self.sense_dict['etym']])
        else:
            return ''

    def extract_notes(self):
        if 'note' in self.sense_dict:
            return '; '.join([note['#text'].strip() for note in self.sense_dict['note']])
        else:
            return ''

    def extract_domains(self):
        if 'domain' in self.sense_dict:
            domain_list = self.sense_dict['domain']
            if type(domain_list) is list:
                for domain_name in domain_list:
                    self.domains.append(TRRDomain(domain_name['@type']))
            if type(domain_list) is OrderedDict:
                self.domains.append(TRRDomain(domain_list['@type']))

    def extract_synset(self):
        if 'synSetRef' in self.sense_dict:
            synset = self.sense_dict['synSetRef']
            if type(synset) is OrderedDict:
                self.synset.append(TRRSynSet(synset['@target']))

    def extract_collocates(self):
        if 'collocates' in self.sense_dict:
            collocates = self.sense_dict['collocates']['collocate']
            for collocate in collocates:
                self.collocates.append(TRRCollocate(collocate, self.xml_id))

    def extract_rhymes(self):
        if 'rhymes' in self.sense_dict:
            rhymes = self.sense_dict['rhymes']['rhyme']
            for rhyme in rhymes:
                self.rhymes.append(TRRRhyme(rhyme, self.xml_id))

    def extract_xrefs(self):
        if 'xref' in self.sense_dict:
            xrefs = self.sense_dict['xref']
            for xref in xrefs:
                self.xrefs.append(TRRXref(xref))

    def extract_examples(self):
        example_list = self.sense_dict['examples']['example']
        if type(example_list) is list:
            for example in example_list:
                yield(TRRExample(self.sense_object, example))
        if type(example_list) is OrderedDict:
            yield(TRRExample(self.sense_object, example_list))

    def add_relations(self):
        self.sense_object.parent_entry.add(self.parent_entry)
        self.parent_entry.senses.add(self.sense_object)
        for d in self.domains:
            d.domain_object.senses.add(self.sense_object)
        for s in self.synset:
            s.synset_object.senses.add(self.sense_object)
        for x in self.xrefs:
            self.sense_object.xrefs.add(x.xref_object)
        for c in self.collocates:
            self.sense_object.collocates.add(c.collocate_object)
        for r in self.rhymes:
            self.sense_object.rhymes.add(r.rhyme_object)


class TRRExample:

    def __init__(self, sense_object, example_dict):
        self.sense_object = sense_object
        self.example_dict = example_dict
        self.song_title = self.example_dict['songTitle']
        self.release_date_string = self.example_dict['date']
        self.release_date = self.clean_up_date()
        self.album = self.example_dict['album']
        self.artist_name = self.get_artist_name()
        self.lyric_text = self.example_dict['lyric']['text']
        self.example_object = self.add_to_db()
        self.entities = []
        self.extract_entities()
        self.update_example()
        self.primary_artists = self.get_primary_artists()
        self.featured_artists = self.get_featured_artists()
        self.add_relations()

    def get_artist_name(self):
        val = self.example_dict['artist']
        if type(val) is OrderedDict:
            return val['#text']
        elif type(val) is str:
            return val
        else:
            return '__none__'

    def extract_artists(self, artist_type):
        if artist_type in self.example_dict:
            artist = self.example_dict[artist_type]
            if type(artist) is OrderedDict or type(artist) is str:
                yield self.process_artist(artist)
            if type(artist) is list:
                for a in artist:
                    yield self.process_artist(a)
        else:
            yield None

    @staticmethod
    def process_artist(artist):
        if type(artist) is str:
            name = artist
            origin = None
        else:
            name = artist['#text']
            if '@origin' in artist:
                origin = artist['@origin']
            else:
                origin = None

        a = TRRArtist(name)
        if origin:
            a.artist_object.origin = origin
            a.artist_object.save()
        return a

    def get_primary_artists(self):
        return [a for a in self.extract_artists('artist')]

    def get_featured_artists(self):
        if 'feat' in self.example_dict:
            return [a for a in self.extract_artists('feat')]
        else:
            return []

    def add_to_db(self):
        print('Adding Example:', self.lyric_text)
        example, created = Example.objects.get_or_create(song_title=self.song_title,
                                                         artist_name=self.artist_name,
                                                         release_date=self.release_date,
                                                         release_date_string=self.release_date_string,
                                                         album=self.album,
                                                         lyric_text=self.lyric_text)
        return example

    def extract_entities(self):
        if 'entity' in self.example_dict['lyric']:
            entities = self.example_dict['lyric']['entity']
            if type(entities) is list:
                for entity in entities:
                    self.entities.append(TRREntity(entity))
            if type(entities) is OrderedDict:
                self.entities.append(TRREntity(entities))

    def update_example(self):
        self.example_object.json = self.example_dict
        self.example_object.artist_slug = slugify(self.artist_name)
        self.example_object.save()

    def add_relations(self):
        self.example_object.illustrates_senses.add(self.sense_object)
        for artist in self.primary_artists:
            if not self.example_object.artist.exists():
                self.example_object.artist.add(artist)
            artist.artist_object.primary_senses.add(self.sense_object)
            artist.artist_object.save()
        for artist in self.featured_artists:
            if not self.example_object.feat_artist.exists():
                self.example_object.feat_artist.add(artist)
            artist.artist_object.featured_senses.add(self.sense_object)
            artist.artist_object.save()
        for e in self.entities:
            e.entity_object.examples.add(self.example_object)

    def clean_up_date(self):
        new_date = self.release_date_string
        month = new_date[-2:]
        if len(new_date) == 7 and month == '02':
            return new_date + '-29'
        if len(new_date) == 7 and month in ['04', '06', '11', '09']:
            return new_date + '-30'
        if len(new_date) == 7:
            return new_date + '-31'
        if len(new_date) == 4:
            return new_date + '-12-31'
        return new_date


class TRRArtist:

    def __init__(self, name, origin=None):
        self.name = name
        self.origin = origin
        self.slug = slugify(self.name)
        self.artist_object = self.add_to_db()
        self.update_origin()

    def __str__(self):
        return self.name

    def add_to_db(self):
        print('Adding Artist:', self.name)
        artist_object, created = Artist.objects.get_or_create(name=self.name,
                                                              slug=self.slug)
        return artist_object

    def update_origin(self):
        if self.origin:
            self.artist_object.origin = self.origin
            self.artist_object.save()


class TRRDomain:

    def __init__(self, name):
        self.name = name
        self.slug = slugify(self.name)
        self.domain_object = self.add_to_db()
        self.update_domain_object()

    def __str__(self):
        return self.name

    def add_to_db(self):
        print('Adding Domain:', self.name)
        domain_object, created = Domain.objects.get_or_create(name=self.name)
        return domain_object

    def update_domain_object(self):
        self.domain_object.slug = self.slug
        self.domain_object.save()


class TRRSynSet:

    def __init__(self, synset_id):
        self.synset_id = synset_id
        self.slug = slugify(self.synset_id)
        self.synset_object = self.add_to_db()
        self.update_synset_object()

    def __str__(self):
        return self.synset_id

    def add_to_db(self):
        print('Adding SynSet:', self.synset_id)
        synset_object, created = SynSet.objects.get_or_create(name=self.synset_id)
        return synset_object

    def update_synset_object(self):
        self.synset_object.slug = self.slug
        self.synset_object.save()


class TRREntity:

    def __init__(self, entity):
        self.entity = entity
        self.name = self.entity['#text']
        self.slug = slugify(self.name)
        self.entity_type = self.entity['@type']
        self.pref_label = self.extract_pref_label()
        self.entity_object = self.add_to_db()
        self.update_entity_object()

    def __str__(self):
        return self.name

    def extract_pref_label(self):
        if '@prefLabel' in self.entity:
            return self.entity['@prefLabel']
        else:
            return self.name

    def add_to_db(self):
        print('Adding Entity:', self.name)
        entity_object, created = NamedEntity.objects.get_or_create(name=self.name,
                                                                   entity_type=self.entity_type)
        return entity_object

    def update_entity_object(self):
        self.entity_object.pref_label = self.pref_label
        self.entity_object.slug = self.slug
        self.entity_object.save()


class TRRCollocate:

    def __init__(self, collocate_dict, sense_id):
        self.collocate_dict = collocate_dict
        self.source_sense_xml_id = sense_id
        self.collocate_lemma = self.collocate_dict['#text']
        self.target_id = self.collocate_dict['@target']
        self.target_slug = slugify(self.collocate_lemma)
        self.collocate_object = self.add_to_db()
        self.frequency = self.extract_frequency()
        self.update_collocate_object()

    def __str__(self):
        return self.collocate_lemma

    def extract_frequency(self):
        if '@freq' in self.collocate_dict:
            return self.collocate_dict['@freq']
        else:
            return None

    def add_to_db(self):
        print('Adding Collocate:', self.collocate_lemma)
        collocate_object, created = Collocate.objects.get_or_create(collocate_lemma=self.collocate_lemma,
                                                                    source_sense_xml_id=self.source_sense_xml_id,
                                                                    target_id=self.target_id)
        return collocate_object

    def update_collocate_object(self):
        self.collocate_object.frequency = self.frequency
        self.collocate_object.target_slug = self.target_slug
        self.collocate_object.save()


class TRRRhyme:

    def __init__(self, rhyme_dict, sense_id):
        self.rhyme_dict = rhyme_dict
        self.source_sense_xml_id = sense_id
        self.rhyme_word = self.rhyme_dict['#text']
        self.target_slug = slugify(self.rhyme_word)
        self.rhyme_object = self.add_to_db()
        self.frequency = self.extract_frequency()
        self.update_rhyme_object()

    def __str__(self):
        return self.rhyme_word

    def extract_frequency(self):
        if '@freq' in self.rhyme_dict:
            return self.rhyme_dict['@freq']
        else:
            return None

    def add_to_db(self):
        print('Adding Rhyme:', self.rhyme_dict)
        rhyme_object, created = Rhyme.objects.get_or_create(rhyme_word=self.rhyme_word,
                                                            source_sense_xml_id=self.source_sense_xml_id)
        return rhyme_object

    def update_rhyme_object(self):
        self.rhyme_object.frequency = self.frequency
        self.rhyme_object.target_slug = self.target_slug
        self.rhyme_object.save()


class TRRXref:

    def __init__(self, xref_dict):
        self.xref_dict = xref_dict
        self.xref_word = self.xref_dict['#text']
        self.xref_type = self.extract_xref_type()
        self.target_id = self.xref_dict['@target']
        self.target_lemma = self.extract_target_lemma()
        self.target_slug = slugify(self.target_lemma)
        self.xref_object = self.add_to_db()
        self.position = self.extract_position()
        self.frequency = self.extract_frequency()
        self.update_xref_object()

    def __str__(self):
        return self.xref_word

    def extract_xref_type(self):
        type_map = {
            'conceptRelatesTo': 'Related Concept',
            'derivesFrom': 'Derives From',
            'hasAntonym': 'Antonym',
            'hasInstance': 'Instance',
            'hasPart': 'Meronym',
            'hasSynonym': 'Synonym',
            'hasDerivative': 'Derivative',
            'instanceOf': 'Instance Of',
            'lemmaRelatesTo': 'Related Word',
            'partOf': 'Holonym',
        }

        if '@type' in self.xref_dict:
            key = self.xref_dict['@type']
            return type_map[key]
        else:
            return 'Related Concept'

    def extract_target_lemma(self):
        if '@lemma' in self.xref_dict:
            return self.xref_dict['@lemma']
        else:
            return self.xref_dict['#text']

    def extract_position(self):
        if '@position' in self.xref_dict:
            return self.xref_dict['@position']
        else:
            return None

    def extract_frequency(self):
        if '@freq' in self.xref_dict:
            return self.xref_dict['@freq']
        else:
            return None

    def add_to_db(self):
        print('Adding Xref:', self.xref_word)
        xref_object, created = Xref.objects.get_or_create(xref_word=self.xref_word,
                                                          xref_type=self.xref_type,
                                                          target_id=self.target_id,
                                                          target_lemma=self.target_lemma,
                                                          target_slug=self.target_slug)
        return xref_object

    def update_xref_object(self):
        self.xref_object.position = self.position
        self.xref_object.frequency = self.frequency
        self.xref_object.save()




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

