__author__ = 'MBK'

import time
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
import concurrent.futures
import xmltodict
from geopy.geocoders import Nominatim
from dictionary.models import Entry, Sense, Example, Artist, Domain, SynSet, \
    NamedEntity, Xref, Collocate, SenseRhyme, ExampleRhyme, LyricLink, \
    Place, Song, SemanticClass, Region
from dictionary.utils import slugify, make_label_from_camel_case, geocode_place, move_definite_article_to_end


geolocator = Nominatim()
geocache = []


CHECK_FOR_UPDATES = True


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
        force_list = ('entry', 'senses', 'forms', 'sense', 'definition', 'collocate', 'xref', 'feat', 'note', 'etym', 'rhyme', 'entity', 'rf')
        try:
            j = xmltodict.parse(self.xml_string, force_list=force_list)
        except:
            raise Exception("xmltodict can't parse that xml string")
        else:
            return j


class TRRDict:

    def __init__(self, xml_dict):
        self.start = time.time()
        self.xml_dict = xml_dict
        self.dictionary = self.get_dictionary()
        self.entries = self.get_entries()
        self.entry_count = len(self.entries)
        self.end = time.time()
        self.total_time = self.end - self.start
        self.print_stats()

    def __str__(self):
        return "Python dict representation of The Right Rhymes. Entry count: " + str(self.entry_count)

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

    def print_stats(self):
        m, s = divmod(self.total_time, 60)
        h, m = divmod(m, 60)

        print('Processed', self.entry_count, 'entry in %d:%02d:%02d' % (h, m, s))


class TRREntry:

    def __init__(self, entry_dict):
        self.entry_dict = entry_dict
        self.headword = self.entry_dict['head']['headword']
        self.sort_key = move_definite_article_to_end(self.headword).lower()
        self.slug = slugify(self.headword)
        self.letter = self.get_letter()
        self.xml_id = self.entry_dict['@eid']
        self.forms = []
        self.publish = False if self.entry_dict['@publish'] == 'no' else True
        self.entry_object = self.add_to_db()
        self.updated = self.check_if_updated()
        self.extract_forms()
        self.update_entry()
        self.extract_lexemes()
        self.sense_count = 0
        self.example_count = 0

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
        print("------ Processing: '" + self.headword + "' ------")
        entry, created = Entry.objects.get_or_create(headword=self.headword,
                                                     slug=self.slug)
        return entry

    def check_if_updated(self):
        if CHECK_FOR_UPDATES:
            return self.entry_dict != self.entry_object.json
        return False

    def update_entry(self):
        self.entry_object.publish = self.publish
        self.entry_object.json = self.entry_dict
        self.entry_object.letter = self.letter
        self.entry_object.sort_key = self.sort_key
        self.entry_object.save()

    def extract_forms(self):
        if 'forms' in self.entry_dict['senses']:
            for form in self.entry_dict['senses']['forms']['form']:
                label = form['#text']
                frequency = form["freq"]
                self.append(TRRForm(self.entry_object, label, frequency))

    def extract_lexemes(self):
        if CHECK_FOR_UPDATES:
            if self.updated:
                lexemes = self.entry_dict['senses']
                for l in lexemes:
                    self.process_lexeme(l)
            else:
                print("Skipping '" + self.headword + "' -- it hasn't been updated")
        else:
            lexemes = self.entry_dict['senses']
            for l in lexemes:
                self.process_lexeme(l)

    def process_lexeme(self, lexeme):
        pos = lexeme['pos']
        for s in lexeme['sense']:
            self.process_sense(pos, s)

    def process_sense(self, pos, sense):
        TRRSense(self.entry_object, self.headword, pos, sense, self.publish)


class TRRForm:

    def __init__(self, entry_object, label, frequency):
        self.parent_entry = entry_object
        self.label = label
        self.frequency = frequency
        self.slug = slugify(self.label)

    def add_to_db(self):
        print("Adding Form:'" + self.label)
        form_object, created = Form.objects.get_or_create(slug=self.slug)
        return form_object

class TRRSense:

    def __init__(self, entry_object, headword, pos, sense_dict, publish):
        self.parent_entry = entry_object
        self.headword = headword
        self.pos = pos
        self.sense_dict = sense_dict
        self.publish = publish
        self.xml_id = self.sense_dict['@id']
        self.slug = slugify(self.headword)
        self.definition = self.extract_definition()
        self.etymology = self.extract_etymology()
        self.notes = self.extract_notes()
        self.sense_object = self.add_to_db()
        self.update_sense()
        self.domains = []
        self.extract_domains()
        self.regions = []
        self.extract_regions()
        self.semantic_classes = []
        self.extract_semantic_classes()
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
        self.update_entry()

    def __str__(self):
        return self.headword + ', ' + self.pos

    def add_to_db(self):
        print("Adding Sense:'" + self.headword + "' -", self.pos, '(' + self.xml_id + ')')
        sense_object, created = Sense.objects.get_or_create(xml_id=self.xml_id)
        return sense_object

    def update_sense(self, clear_exx=False):
        if clear_exx:
            self.sense_object.examples.all().delete()
            self.sense_object.cites_artists.all().delete()

        self.sense_object.json = self.sense_dict
        self.sense_object.headword = self.headword
        self.sense_object.part_of_speech = self.pos
        self.sense_object.definition = self.definition
        self.sense_object.etymology = self.etymology
        self.sense_object.notes = self.notes
        self.sense_object.slug = self.slug
        self.sense_object.publish = self.publish
        self.sense_object.save()

    def update_entry(self):
        self.parent_entry.example_count = len(self.examples)
        self.parent_entry.save()

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

    def extract_regions(self):
        if 'region' in self.sense_dict:
            region_list = self.sense_dict['region']
            if type(region_list) is list:
                for region_name in region_list:
                    self.regions.append(TRRRegion(region_name['@type']))
            if type(region_list) is OrderedDict:
                self.regions.append(TRRRegion(region_list['@type']))

    def extract_semantic_classes(self):
        if 'semanticClass' in self.sense_dict:
            semantic_class_list = self.sense_dict['semanticClass']
            if type(semantic_class_list) is list:
                for semantic_class_name in semantic_class_list:
                    self.semantic_classes.append(TRRSemanticClass(semantic_class_name['@type']))
            if type(semantic_class_list) is OrderedDict:
                self.semantic_classes.append(TRRSemanticClass(semantic_class_list['@type']))

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
                self.rhymes.append(TRRSenseRhyme(rhyme, self.xml_id))

    def extract_xrefs(self):
        if 'xref' in self.sense_dict:
            xrefs = self.sense_dict['xref']
            for xref in xrefs:
                self.xrefs.append(TRRXref(xref))

    def extract_examples(self):
        examples = self.sense_dict['examples']
        if examples:
            example_list = examples['example']
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
        for d in self.regions:
            d.region_object.senses.add(self.sense_object)
        for sc in self.semantic_classes:
            sc.semantic_class_object.senses.add(self.sense_object)
        for s in self.synset:
            s.synset_object.senses.add(self.sense_object)
        for x in self.xrefs:
            self.sense_object.xrefs.add(x.xref_object)
        for c in self.collocates:
            self.sense_object.collocates.add(c.collocate_object)
        for r in self.rhymes:
            self.sense_object.sense_rhymes.add(r.rhyme_object)


class TRRSong:

    def __init__(self, xml_id, release_date, release_date_string, song_title, artist_name, artist_slug, primary_artists, feat_artists, album):
        self.xml_id = xml_id
        self.release_date = release_date
        self.release_date_string = release_date_string
        self.title = song_title
        self.artist_name = artist_name
        self.artist_slug = artist_slug
        self.slug = slugify(self.artist_name + ' ' + self.title)
        self.primary_artists = primary_artists
        self.feat_artists = feat_artists
        self.album = album
        self.song_object = self.add_to_db()
        self.update_song()
        self.add_relations()

    def __str__(self):
        return '"' + self.title + '" '

    def add_to_db(self):
        # print('Adding Song: "' + self.title + '"')
        song_object, created = Song.objects.get_or_create(xml_id=self.xml_id)
        return song_object

    def update_song(self):
        self.song_object.title = self.title
        self.song_object.album = self.album
        self.song_object.slug = self.slug
        self.song_object.release_date = self.release_date
        self.song_object.release_date_string = self.release_date_string
        self.song_object.artist_name = self.artist_name
        self.song_object.artist_slug = self.artist_slug
        self.song_object.save()

    def add_relations(self):
        for artist in self.primary_artists:
            self.song_object.artist.add(artist.artist_object)
            artist.artist_object.primary_songs.add(self.song_object)
            artist.artist_object.save()
        for artist in self.feat_artists:
            self.song_object.feat_artist.add(artist.artist_object)
            artist.artist_object.featured_songs.add(self.song_object)
            artist.artist_object.save()


class TRRExample:

    def __init__(self, sense_object, example_dict):
        self.sense_object = sense_object
        self.example_dict = example_dict
        self.song_title = self.example_dict['songTitle']
        self.xml_id = self.example_dict['@id']
        self.release_date_string = self.example_dict['date']
        self.release_date = clean_up_date(self.release_date_string)
        self.album = self.example_dict['album']
        self.artist_name = self.get_artist_name()
        self.artist_slug = slugify(self.artist_name)
        self.lyric_text = self.example_dict['lyric']['text']
        self.example_object = self.add_to_db()
        # self.remove_previous_lyric_links_and_rhymes()
        self.lyric_links = []
        self.example_rhymes = []
        self.extract_rf()
        self.entities = []
        self.xrefs = []
        self.extract_entities()
        self.extract_rhymes()
        self.update_example()
        self.primary_artists = self.get_primary_artists()
        self.featured_artists = self.get_featured_artists()
        self.extract_xrefs()
        self.song = TRRSong(self.xml_id, self.release_date, self.release_date_string,
                                   self.song_title, self.artist_name, self.artist_slug,
                                   self.primary_artists, self.featured_artists, self.album)
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
            if '@origin' in artist and artist['@origin'].lower() != 'none':
                origin = artist['@origin']
            else:
                origin = None

        if origin:
            a = TRRArtist(name)
        else:
            a = TRRArtist(name)
        return a

    def get_primary_artists(self):
        return [a for a in self.extract_artists('artist')]

    def get_featured_artists(self):
        if 'feat' in self.example_dict:
            return [a for a in self.extract_artists('feat')]
        else:
            return []

    def add_to_db(self):
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

            for entity in entities:
                self.entities.append(TRREntity(entity))
                if '@type' in entity and entity['@type'] == 'artist':
                    self.lyric_links.append(TRRLyricLink(entity, 'artist'))
                    if '@prefLabel' in entity:
                        TRRArtist(entity['@prefLabel'])
                    else:
                        TRRArtist(entity['#text'])
                else:
                    self.lyric_links.append(TRRLyricLink(entity, 'entity'))
                if '@rhymeTarget' in entity:
                    self.example_rhymes.append(TRRExampleRhyme(entity))

    def extract_rhymes(self):
        if 'rhyme' in self.example_dict['lyric']:
            rhymes = self.example_dict['lyric']['rhyme']

            for rhyme in rhymes:
                self.example_rhymes.append(TRRExampleRhyme(rhyme))
                self.lyric_links.append(TRRLyricLink(rhyme, 'rhyme'))

    def extract_rf(self):
        if 'rf' in self.example_dict['lyric']:
            rfs = self.example_dict['lyric']['rf']
            for rf in rfs:
                # self.lyric_links.append(TRRLyricLink(rf, 'rf'))
                self.lyric_links.append(TRRLyricLink(rf, 'xref'))

    def extract_xrefs(self):
        if 'xref' in self.example_dict['lyric']:
            xrefs = self.example_dict['lyric']['xref']
            for xref in xrefs:
                xref_sense_object, created = Sense.objects.get_or_create(xml_id=xref['@target'])
                self.example_object.illustrates_senses.add(xref_sense_object)
                for artist in self.primary_artists:
                    artist.artist_object.primary_senses.add(xref_sense_object)
                self.lyric_links.append(TRRLyricLink(xref, 'xref'))
                if '@rhymeTarget' in xref:
                    self.example_rhymes.append(TRRExampleRhyme(xref))

    def update_example(self):
        self.example_object.json = self.example_dict
        self.example_object.artist_slug = slugify(self.artist_name)
        self.example_object.save()

    def remove_previous_lyric_links_and_rhymes(self):
        # print('Removing any pre-existing lyric links / rhymes to "' + self.lyric_text + '"')
        self.example_object.lyric_links.all().delete()
        self.example_object.example_rhymes.all().delete()
        self.example_object.from_song.all().delete()

    def add_relations(self):
        self.example_object.illustrates_senses.add(self.sense_object)
        for artist in self.primary_artists:
            self.example_object.artist.add(artist.artist_object)
            artist.artist_object.primary_senses.add(self.sense_object)
            artist.artist_object.save()
        for artist in self.featured_artists:
            self.example_object.feat_artist.add(artist.artist_object)
            artist.artist_object.featured_senses.add(self.sense_object)
            artist.artist_object.save()
        for e in self.entities:
            e.entity_object.examples.add(self.example_object)
            e.entity_object.mentioned_at_senses.add(self.sense_object)
            e.entity_object.save()
        for l in self.lyric_links:
            l.link_object.parent_example.add(self.example_object)
            l.link_object.save()
        for r in self.example_rhymes:
            r.rhyme_object.parent_example.add(self.example_object)
            r.rhyme_object.save()
        self.example_object.from_song.add(self.song.song_object)


class TRRArtist:

    def __init__(self, name, origin=None):
        self.name = name
        self.origin = origin
        self.slug = slugify(self.name)
        self.artist_object = self.add_to_db()
        self.update_artist()

    def __str__(self):
        return self.name

    def add_to_db(self):
        # print('Adding Artist:', self.name, self.slug)
        artist_object, created = Artist.objects.get_or_create(slug=self.slug)
        return artist_object

    def update_artist(self):
        if self.artist_object.name is None:
            self.artist_object.name = self.name
            self.artist_object.save()
        if self.origin:
            o = TRRPlace(self.origin)
            self.artist_object.origin.add(o.place_object)
            self.artist_object.save()


class TRRPlace:

    def __init__(self, name):
        self.full_name = name
        self.name = self.extract_short_name()
        self.slug = slugify(self.full_name)
        self.place_object = self.add_to_db()
        self.update_place_object()
        self.add_lat_long()
        self.check_if_part()

    def extract_short_name(self):
        if ',' in self.full_name:
            return self.full_name.split(', ')[0]
        else:
            return self.full_name

    def add_to_db(self):
        # print('Adding Place:', self.name)
        place_object, created = Place.objects.get_or_create(slug=self.slug)
        return place_object

    def add_lat_long(self):
        if self.full_name and self.place_object and not self.place_object.longitude and self.slug not in geocache:
            latitude, longitude = geocode_place(self.full_name)
            if longitude:
                self.place_object.longitude = longitude
            if latitude:
                self.place_object.latitude = latitude
            self.place_object.save()

    def check_if_part(self):
        if ', ' in self.full_name:
            tokens = self.full_name.split(', ')
            within = ', '.join(tokens[1:])
            container = TRRPlace(within)
            container.place_object.contains.add(self.place_object)
            container.place_object.save()
            self.place_object.save()

    def update_place_object(self):
        self.place_object.name = self.name
        self.place_object.full_name = self.full_name
        self.place_object.save()


class TRRSemanticClass:

    def __init__(self, name):
        self.name = make_label_from_camel_case(name)
        self.slug = slugify(self.name)
        self.semantic_class_object = self.add_to_db()
        self.update_semantic_class_object()

    def __str__(self):
        return self.name

    def add_to_db(self):
        # print('Adding semantic_class:', self.name)
        semantic_class_object, created = SemanticClass.objects.get_or_create(slug=self.slug)
        return semantic_class_object

    def update_semantic_class_object(self):
        self.semantic_class_object.name = self.name
        self.semantic_class_object.save()


class TRRDomain:

    def __init__(self, name):
        self.name = make_label_from_camel_case(name)
        self.slug = slugify(self.name)
        self.domain_object = self.add_to_db()
        self.update_domain_object()

    def __str__(self):
        return self.name

    def add_to_db(self):
        # print('Adding Domain:', self.name)
        domain_object, created = Domain.objects.get_or_create(slug=self.slug)
        return domain_object

    def update_domain_object(self):
        self.domain_object.name = self.name
        self.domain_object.save()


class TRRRegion:

    def __init__(self, name):
        self.name = make_label_from_camel_case(name)
        self.slug = slugify(self.name)
        self.region_object = self.add_to_db()
        self.update_region_object()

    def __str__(self):
        return self.name

    def add_to_db(self):
        # print('Adding Region:', self.name)
        region_object, created = Region.objects.get_or_create(slug=self.slug)
        return region_object

    def update_region_object(self):
        self.region_object.name = self.name
        self.region_object.save()


class TRRSynSet:

    def __init__(self, synset_id):
        self.synset_id = synset_id
        self.slug = slugify(self.synset_id)
        self.synset_object = self.add_to_db()
        self.update_synset_object()

    def __str__(self):
        return self.synset_id

    def add_to_db(self):
        # print('Adding SynSet:', self.synset_id)
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
        self.pref_label_slug = slugify(self.pref_label)
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
        # print('Adding Entity:', self.name)
        entity_object, created = NamedEntity.objects.get_or_create(pref_label_slug=self.pref_label_slug,
                                                                   entity_type=self.entity_type)
        # if self.entity_type == 'place':
        #     TRRPlace(self.pref_label)
        return entity_object

    def update_entity_object(self):
        self.entity_object.pref_label = self.pref_label
        self.entity_object.slug = self.slug
        self.entity_object.name = self.name
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
        # print('Adding Collocate:', self.collocate_lemma)
        collocate_object, created = Collocate.objects.get_or_create(collocate_lemma=self.collocate_lemma,
                                                                    source_sense_xml_id=self.source_sense_xml_id,
                                                                    target_id=self.target_id)
        return collocate_object

    def update_collocate_object(self):
        self.collocate_object.frequency = self.frequency
        self.collocate_object.target_slug = self.target_slug
        self.collocate_object.save()


class TRRSenseRhyme:

    def __init__(self, rhyme_dict, sense_id):
        self.rhyme_dict = rhyme_dict
        self.source_sense_xml_id = sense_id
        self.rhyme = self.rhyme_dict['#text']
        self.rhyme_slug = slugify(self.rhyme)
        self.rhyme_object = self.add_to_db()
        self.frequency = self.extract_frequency()
        self.update_rhyme_object()

    def __str__(self):
        return self.rhyme

    def extract_frequency(self):
        if '@freq' in self.rhyme_dict:
            return self.rhyme_dict['@freq']
        else:
            return None

    def add_to_db(self):
        # print('Adding Rhyme:', self.rhyme)
        rhyme_object, created = SenseRhyme.objects.get_or_create(rhyme=self.rhyme,
                                                                 parent_sense_xml_id=self.source_sense_xml_id)
        return rhyme_object

    def update_rhyme_object(self):
        self.rhyme_object.frequency = self.frequency
        self.rhyme_object.rhyme_slug = self.rhyme_slug
        self.rhyme_object.save()


class TRRExampleRhyme:

    def __init__(self, rhyme_dict):
        self.rhyme_dict = rhyme_dict
        self.word_one = self.rhyme_dict['#text']
        self.word_one_slug = slugify(self.word_one)
        self.word_one_position = self.rhyme_dict['@position']
        self.word_two = self.rhyme_dict['@rhymeTargetWord']
        self.word_two_position = self.rhyme_dict['@rhymeTargetPosition']
        self.word_two_slug = slugify(self.word_two)
        self.word_two_target_id = self.extract_target_id()
        self.rhyme_object = self.add_to_db()
        self.update_rhyme_object()

    def __str__(self):
        return self.word_one + ' - ' + self.word_two

    def add_to_db(self):
        if self.word_two_position:
            # print('Adding Example Rhyme:', self.word_one, '-', self.word_two)
            rhyme_object, created = ExampleRhyme.objects.get_or_create(word_one=self.word_one,
                                                                       word_two=self.word_two,
                                                                       word_one_position=self.word_one_position,
                                                                       word_two_position=self.word_two_position)
            return rhyme_object
        else:
            print('Unable to find word position for', self.word_two, 'in rhyme', self.word_one)
            return None

    def extract_target_id(self):
        if '@rhymeTarget' in self.rhyme_dict:
            return self.rhyme_dict['@rhymeTarget']
        else:
            return None

    def update_rhyme_object(self):
        if self.rhyme_object:
            self.rhyme_object.word_one_slug = self.word_one_slug
            self.rhyme_object.word_two_slug = self.word_two_slug
            self.rhyme_object.word_two_target_id = self.word_two_target_id
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
        # print('Adding Xref:', self.xref_word)
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


class TRRLyricLink:

    def __init__(self, link_dict, link_type):
        self.link_dict = link_dict
        self.link_type = link_type
        self.link_text = self.link_dict['#text']
        self.target_slug = self.extract_target_slug()
        self.target_lemma = self.extract_target_lemma()
        self.position = self.link_dict['@position']
        self.link_object = self.add_to_db()

    def __str__(self):
        return self.link_text

    def extract_target_slug(self):
        if '@target' in self.link_dict and '@lemma' in self.link_dict:
            return slugify(self.link_dict['@lemma']) + '#' + self.link_dict['@target']
        elif '@prefLabel' in self.link_dict:
            return slugify(self.link_dict['@prefLabel'])
        else:
            return slugify(self.link_dict['#text'])

    def extract_target_lemma(self):
        if '@lemma' in self.link_dict:
            return self.link_dict['@lemma']
        else:
            return self.link_text

    def add_to_db(self):
        # print('Adding LyricLink:', self.link_text)
        test = LyricLink.objects.filter(link_text=self.link_text,
                                        link_type=self.link_type,
                                        target_lemma=self.target_lemma,
                                        target_slug=self.target_slug,
                                        position=self.position)
        if test:
            return test.first()
        else:
            link_object = LyricLink.objects.create(link_text=self.link_text,
                                                   link_type=self.link_type,
                                                   target_lemma=self.target_lemma,
                                                   target_slug=self.target_slug,
                                                   position=self.position)
            return link_object


def clean_up_date(unformatted_date):
    new_date = unformatted_date
    month = new_date[-2:]
    if len(new_date) == 7 and month == '02':
        return new_date + '-28'
    if len(new_date) == 7 and month in ['04', '06', '11', '09']:
        return new_date + '-30'
    if len(new_date) == 7:
        return new_date + '-31'
    if len(new_date) == 4:
        return new_date + '-12-31'
    return new_date


def collect_xml(directory):
    return [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]


def launch_trr_dict(x):
    return TRRDict(x.xml_dict)


def process_xml(xml_list):
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    #     processed_xml = {executor.submit(launch_trr_dict, XMLDict(xml)): xml for xml in xml_list}
    #     for future in concurrent.futures.as_completed(processed_xml):
    #         done = processed_xml[future]
    #         try:
    #             data = future.result()
    #         except Exception as exc:
    #             print('%r generated an exception: %s' % (done, exc))
    #         else:
    #             print('{} is done, yo'.format(data))

    for xml in xml_list:
        x = XMLDict(xml)
        launch_trr_dict(x)


def main(directory='../tRR/XML/tRR_Django'):
    start = time.time()
    xml_files = sorted(collect_xml(directory), key=lambda f: f.lower())
    process_xml(xml_files)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    print('Processed dictionary in %d:%02d:%02d' % (h, m, s))


#
#
# if __name__ == '__main__':
#     x = XMLDict('static/test/test.xml')
#     t = TRRDict(x.xml_dict)
