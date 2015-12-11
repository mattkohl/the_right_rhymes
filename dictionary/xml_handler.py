__author__ = 'MBK'

from .models import Word
from lxml import etree
import re
from time import process_time


class tRR_Dictionary:

    def __init__(self, filename):
        self.filename = filename
        self.tree = self.parse_xml()
        self.root = self.get_tree_root()
        self.entries = self.process_entries()

    def parse_xml(self):
        try:
            xml_tree = etree.parse(self.filename)
        except:
            raise Exception('Cannot parse ' + self.filename)
        else:
            return xml_tree

    def get_tree_root(self):
        return self.tree.getroot()

    def process_entries(self):
        for entry in self.root.xpath("//entry"):
            yield tRR_Entry(entry)


class tRR_Entry:

    def __init__(self, entry):
        self.element = entry
        self.id = self.element.attrib['id']
        self.lemma = self.element.xpath('head/headword')[0].text
        self.publish = self.element.attrib['publish'] == 'yes'
        self.slug = slugify(self.lemma)
        self.word_obj = self.persist_lemma_in_db()
        self.senses = [senses for senses in self.process_senses()]

    def persist_lemma_in_db(self):
        word, created = Word.objects.get_or_create(form=self.lemma, slug=self.slug)
        return word

    def process_senses(self):
        for child in self.element.getchildren():
            if child.tag == 'senses':
                yield tRR_Senses(child, self.word_obj, self.publish)


class tRR_Senses:

    def __init__(self, senses, word_obj, publish):
        self.element = senses
        self.word_obj = word_obj
        self.publish = publish
        self.id = self.element.attrib['id']
        self.pos = self.element.xpath('pos')[0].text
        self.senses = [sense for sense in self.process_senses()]

    def process_senses(self):
        for child in self.element.getchildren():
            if child.tag == 'sense':
                yield tRR_Sense(child, self.word_obj, self.publish, self.pos)


class tRR_Sense:

    def __init__(self, sense, word_obj, publish, pos):
        self.element = sense
        self.word_obj = word_obj
        self.publish = publish
        self.pos = pos
        self.id = self.element.attrib['id']
        self.definition = self.get_definitions()
        self.etymology = self.get_etymologies()
        self.domains = self.get_domains()


    def get_definitions(self):
        definitions = self.element.xpath('definition/text')
        return '; '.join([definition.xpath('string()') for definition in definitions])

    def get_etymologies(self):
        etymologies = self.element.xpath('etymology/text')
        return '; '.join([etymology.xpath('string()') for etymology in etymologies])

    def get_domains(self):
        return self.element.xpath('domain/@type')


    xrefs = element.xpath('xref')
    examples = element.xpath('examples/example')
    notes = element.xpath('note')

    # CREATE SENSE NODE
    sense = graph.merge_one('Sense', 'tRR_id', id)
    sense['label'] = definition[:25] + '...'
    sense['lemma'] = lemma
    sense['definition'] = definition
    if etymology:
        sense['etymology'] = etymology

    if sentiment:
        sent_node = graph.merge_one('Sentiment', 'label', sentiment[0].title())
        graph.create_unique(Relationship(sense, 'HAS_SENTIMENT', sent_node))

    # ENTITIES
    for ent in entities:
        if 'prefLabel' in ent.attrib:
            label = ent.attrib['prefLabel']
        else:
            label = ent.text
        ent_type = ent.attrib['type']

        if ent_type == 'artist':
            entity = graph.merge_one('Artist', 'name', label)
        elif ent_type == 'songTitle':
            entity = graph.merge_one('Song', 'title', label)
        elif ent_type == 'album':
            entity = graph.merge_one('Album', 'title', label)
        else:
            entity = graph.merge_one('Entity', 'name', label)
            entity['type'] = ent_type

        entity.push()
        graph.create_unique(Relationship(sense, 'CONCEPT_RELATES_TO', entity,
                                         form=ent.text,
                                         prefLabel=ent.attrib['prefLabel'],
                                         position=ent.attrib['position']))

    # DOMAINS
    for domain in domains:
        d = graph.merge_one('Domain', 'tRR_id', domain)
        d['label'] = tokenize_titleize_camel_case(domain)
        d.push()
        graph.create_unique(Relationship(sense, 'HAS_DOMAIN', d))

    # REGIONS
    for region in regions:
        r = graph.merge_one('Region', 'tRR_id', region)
        r['label'] = tokenize_titleize_camel_case(region)
        r.push()
        graph.create_unique(Relationship(sense, 'HAS_REGION', r))

    # ETYMONS
    for etymon in etymons:
        etymon_node = graph.merge_one('Form', 'label', etymon)
        etymon_node['type'] = 'etymon'
        if etymon.expansion:
            etymon_node['expansion'] = True
        etymon_node.push()
        graph.create_unique(Relationship(sense, 'DERIVES_FROM', etymon_node))

    # NOTES
    for note in notes:
        n = graph.merge_one('Note', 'label', note.text)
        n.push()
        graph.create_unique(Relationship(sense, 'HAS_{}_NOTE'.format(note.attrib['type'].upper()), n))

    # XREFS
    for xref in xrefs:
        target_id = xref.attrib['target']
        xref_type = tokenize_capitalize_camel_case(xref.attrib['type'])
        target_sense = graph.merge_one('Sense', 'tRR_id', target_id)
        target_sense['lemma'] = xref.text
        target_sense.push()

        graph.create_unique(Relationship(sense, xref_type, target_sense))

    sense.push()
    graph.create_unique(Relationship(parent, 'HAS_SENSE', sense))

    for example in examples:
        process_example(example, sense)

    return sense


def process_example(element, sense):
    song_id = element.attrib['id']
    release_date = element.xpath('date')[0].text
    artist_name = element.xpath('artist')[0].text
    artist_origin = 'NONE'
    if element.xpath('artist/@origin'):
        artist_origin = element.xpath('artist/@origin')[0]
    album_name = element.xpath('album')[0].text
    song_title = element.xpath('songTitle')[0].text
    featured_artists = element.xpath('feat')

    lyric_element = element.xpath('lyric/text')[0]
    lyric = lyric_element.xpath('string()')

    form = element.xpath('lyric/rf') if element.xpath('lyric/rf') else None

    xrefs = element.xpath('lyric/xref')
    entities = element.xpath('lyric/entity')
    rhymes = element.xpath('lyric/rhyme')

    example = graph.merge_one('Example', 'tRR_id', song_id + '__' + lyric)
    example['label'] = lyric
    example['date'] = release_date
    example['artist'] = artist_name
    example['album'] = album_name
    example.push()

    song = graph.merge_one('Song', 'tRR_id', song_id)
    song['label'] = '"' + song_title + '"'
    song['title'] = song_title
    song['releaseDate'] = release_date
    song['album'] = album_name
    song.push()

    graph.create_unique(Relationship(example, 'FROM_SONG', song))

    artist = graph.merge_one('Artist', 'name', artist_name)
    if artist_origin and artist_origin.lower() != 'none':
        artist['origin'] = artist_origin
        artist.push()
    graph.create_unique(Relationship(song, 'PRIMARY_ARTIST', artist))

    if featured_artists:
        for featured in featured_artists:
            featured_artist = graph.merge_one('Artist', 'name', featured.text)
            if 'origin' in featured.attrib:
                featured_artist['origin'] = featured.attrib['origin']
            featured_artist.push()
            graph.create_unique(Relationship(song, 'FEATURED_ARTIST', featured_artist))

    if form:
        if form[0].text == form[0].text.upper():
            form_text = form[0].text
        else:
            form_text = form[0].text.lower()
        form_node = graph.merge_one('Form', 'label', form_text)
        graph.create_unique(Relationship(form_node, 'USED_IN', example, position=form[0].attrib['position']))
        graph.create_unique(Relationship(example, 'ILLUSTRATES', sense,
                                         form=form[0].text,
                                         lemma=form[0].attrib['lemma'],
                                         position=form[0].attrib['position']))
    else:
        graph.create_unique(Relationship(example, 'ILLUSTRATES', sense))

    for xref in xrefs:
        target_id = xref.attrib['target']
        target_sense = graph.merge_one('Sense', 'tRR_id', target_id)
        target_sense['lemma'] = xref.attrib['lemma']
        target_sense.push()
        graph.create_unique(Relationship(example, 'ILLUSTRATES', target_sense,
                                         form=xref.text,
                                         lemma=xref.attrib['lemma'],
                                         position=xref.attrib['position']))
        form_node = graph.merge_one('Form', 'label', xref.text)
        graph.create_unique(Relationship(form_node, 'USED_IN', example, position=xref.attrib['position']))

    for ent in entities:
        if 'prefLabel' in ent.attrib:
            label = ent.attrib['prefLabel']
        else:
            label = ent.text
        ent_type = ent.attrib['type']

        if ent_type == 'artist':
            entity = graph.merge_one('Artist', 'name', label)
        elif ent_type == 'songTitle':
            entity = graph.merge_one('Song', 'title', label)
        elif ent_type == 'album':
            entity = graph.merge_one('Album', 'title', label)
        else:
            entity = graph.merge_one('Entity', 'name', label)
            entity['type'] = ent_type

        entity.push()
        graph.create_unique(Relationship(example, 'MENTIONS', entity,
                                         form=ent.text,
                                         prefLabel=ent.attrib['prefLabel'],
                                         position=ent.attrib['position']))
        form = graph.merge_one('Form', 'label', ent.text)
        graph.create_unique(Relationship(form, 'USED_IN', example, position=ent.attrib['position']))
        graph.create_unique(Relationship(entity, 'HAS_FORM', form))

    for rhy in rhymes:
        # print(rhy.text)
        rhyme = graph.merge_one('Form', 'label', rhy.text)
        target_id = rhy.attrib['rhymeTarget']
        if rhy.getparent().find('*[@target="{}"]'.format(target_id)) is not None:
            target_element = rhy.getparent().find('*[@target="{}"]'.format(target_id))
            target_text = target_element.text
            if target_element.tag == 'entity':
                if 'prefLabel' in ent.attrib:
                    label = target_element.attrib['prefLabel']
                else:
                    label = target_element.text
                if target_element.attrib['type'] == 'artist':
                    target_node = graph.merge_one('Artist', 'name', label)
                elif target_element.attrib['type'] == 'songTitle':
                    target_node = graph.merge_one('Song', 'title', label)
                elif target_element.attrib['type'] == 'album':
                    target_node = graph.merge_one('Album', 'title', label)
                else:
                    target_node = graph.merge_one('Entity', 'name', label)
            else:
                target_node = graph.merge_one('Form', 'label', target_text)
            graph.create_unique(Relationship(rhyme, 'RHYMES_WITH', target_node))

        graph.create_unique(Relationship(rhyme, 'USED_IN', example, position=rhy.attrib['position']))

    return example


def tokenize_capitalize_camel_case(label):
    label = label[0].capitalize() + label[1:]
    return '_'.join(re.findall('[A-Z][^A-Z]*', label)).upper()


def tokenize_titleize_camel_case(label):
    label = label[0].capitalize() + label[1:]
    return ' '.join(re.findall('[A-Z][^A-Z]*', label)).title()


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


if __name__ == '__main__':
    start = process_time()
    tree = etree.parse('../static/test/test.xml')
    root = tree.getroot()
    for entry in root.xpath("//entry"):
        process_entry(entry)
    elapsed = process_time() - start
    mins, secs = divmod(elapsed, 60)
    print('Finished uploading data in', str(mins)[:4], 'minutes,', str(secs)[:4], 'seconds')

