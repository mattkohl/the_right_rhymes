from django.test import TestCase
import json

from dictionary.ingestion.json_converter import JSONConverter
from dictionary.ingestion.xml_file_reader import XmlFileReader
from dictionary.models import Entry, Form, Artist, Domain, Collocate, Sense, Region, SemanticClass, Song, NamedEntity, \
    LyricLink, Example, Place, Xref, EntryParsed, FormParsed, SenseParsed, ExampleParsed, SongParsed
from dictionary.management.commands.xml_handler import XMLDict


class BaseTest(TestCase):

    def setUp(self):
        self.epmd = Artist(name='EPMD', slug="epmd")
        self.epmd.save()
        self.erick_sermon = Artist(name="Erick Sermon", slug="erick-sermon")
        self.erick_sermon.save()
        self.method_man = Artist(name="Method Man", slug="method-man")
        self.method_man.save()

        self.example_1 = Example(
            lyric_text="For an MC on a trail of a mad comeback",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title="Rap Is Outta Control",
            album='Business As Usual',
            release_date='1990-12-15',
            release_date_string='1990-12-15'
        )
        self.example_1.save()
        self.example_1.artist.add(self.epmd)
        self.example_2 = Example(
            lyric_text="Now, it's time for me, the E, to rock it loco",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title='Brothers From Brentwood L.I.',
            album='Crossover',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.example_2.save()
        self.example_2.artist.add(self.epmd)

        self.example_3 = Example(
            lyric_text="I must go hard, then take charge",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title="Never Defeat 'Em",
            album='We Mean Business',
            release_date='2008-12-09',
            release_date_string='2008-12-09'
        )
        self.example_3.save()
        self.example_3.artist.add(self.epmd)
        self.example_3.feat_artist.add(self.method_man)

        self.example_4 = Example(
            lyric_text="To go platinum and clock mad green",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title='Crossover',
            album='Business Never Personal',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.example_4.save()
        self.example_4.artist.add(self.epmd)
        self.example_5 = Example(
            lyric_text="EPMD in effect, I'm clockin mad green",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title='Chill',
            album='Business Never Personal',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.example_5.save()
        self.example_5.artist.add(self.epmd)
        self.example_6 = Example(
            lyric_text="No static, Uncle Sam, I got mad loot",
            artist_name='EPMD',
            artist_slug='epmd',
            song_title='Boon Dox',
            album='Business Never Personal',
            release_date='1992-07-28',
            release_date_string='1992-07-28'
        )
        self.example_6.save()
        self.example_6.artist.add(self.epmd)

        self.brentwood_place = Place(name="Brentwood", full_name="Brentwood, New York, USA", slug="brentwood-new-york-usa")
        self.brentwood_place.save()
        self.epmd.origin.add(self.brentwood_place)
        self.drugs = Domain(name="drugs", slug="drugs")
        self.drugs.save()
        self.west_coast = Region(slug="west-coast", name="West Coast")
        self.west_coast.save()

        self.lyric_link_1 = LyricLink(
            link_text="E",
            link_type="artist",
            position=27,
            target_lemma="E",
            target_slug="erick-sermon"
        )
        self.lyric_link_2 = LyricLink(
            link_text='loco',
            link_type='xref',
            position=41,
            target_lemma='loco',
            target_slug='loco#e7360_adv_1'
        )
        self.lyric_link_3 = LyricLink(
            link_text='rock',
            link_type='xref',
            position=33,
            target_lemma='rock',
            target_slug='rock#e9060_trV_1'
        )
        self.mad_lyric_link = LyricLink(
            link_text='mad',
            link_type='xref',
            position=33,
            target_lemma='mad',
            target_slug='mad#e9060_trV_1'
        )
        self.lyric_link_1.save()
        self.lyric_link_2.save()
        self.lyric_link_3.save()
        self.mad_lyric_link.save()
        self.example_2.lyric_links.add(self.lyric_link_1)
        self.example_2.lyric_links.add(self.lyric_link_2)
        self.example_2.lyric_links.add(self.lyric_link_3)

        self.published_headwords = ['rock', 'loco', 'mad']
        self.collocate = Collocate(
            collocate_lemma="lemma",
            source_sense_xml_id="x1",
            target_slug="target1",
            target_id="target1",
            frequency=1
        )
        self.collocate.save()
        self.mad_collocate = Collocate(
            collocate_lemma="mad",
            source_sense_xml_id="x1",
            target_slug="mad",
            target_id="target1",
            frequency=1
        )
        self.mad_collocate.save()
        self.xref = Xref(
            xref_word="word",
            xref_type="type",
            target_lemma="target_lemma",
            target_slug="target_slug",
            target_id="target_id",
            frequency=1,
            position=1
        )
        self.mad_xref = Xref(
            xref_word="maddest",
            xref_type="type",
            target_lemma="mad",
            target_slug="mad",
            target_id="target_id",
            frequency=1,
            position=1
        )
        self.mad_xref.save()
        self.oprah = NamedEntity(name="Oprah", slug="oprah", entity_type="person", pref_label="Oprah Winfrey", pref_label_slug="oprah-winfrey")
        self.oprah.save()
        self.mad_entry = Entry(headword="mad", slug="mad", letter="m", publish=True)
        self.mad_entry.save()
        self.mad_form = Form(slug="mad", label="mad")
        self.mad_form.save()
        self.madder_form = Form(slug="madder", label="madder")
        self.madder_form.save()
        self.maddest_form = Form(slug="maddest", label="maddest")
        self.maddest_form.save()
        self.mad_sense = Sense(headword="mad", slug="mad", xml_id="bar", part_of_speech="adj", publish=True)
        self.mad_sense.save()
        self.mad_entry.forms.add(self.mad_form, self.madder_form, self.maddest_form)
        self.mad_entry.senses.add(self.mad_sense)
        self.mad_sense.examples.add(self.example_1)
        self.mad_sense.examples.add(self.example_4)
        self.mad_sense.examples.add(self.example_5)
        self.mad_sense.examples.add(self.example_6)

        self.drugs_semantic_class = SemanticClass(name="drugs", slug="drugs")
        self.drugs_semantic_class.save()
        self.song = Song(release_date="1998-01-01",
                         release_date_string="1998-01-01",
                         title="foo",
                         album="bar",
                         artist_name="Erick Sermon",
                         slug="erick-sermon-foo",
                         artist_slug="erick-sermon")
        self.song.save()
        self.song.artist.add(self.erick_sermon)
        self.example_foo = Example(
            lyric_text="Foo bar baz, boom bap",
            artist_name='Erick Sermon',
            artist_slug='erick-sermon',
            song_title='foo',
            album="bar",
            release_date="1998-01-01",
            release_date_string="1998-01-01",
        )
        self.example_foo.save()
        self.example_foo.artist.add(self.erick_sermon)
        self.example_foo.from_song.add(self.song)
        self.sense = Sense(headword="headword", part_of_speech="noun", xml_id="foo", slug="headword")
        self.sense.save()

        self.domain = Domain(name="domain", slug="domain")
        self.domain.save()
        self.domain.senses.add(self.sense)

        self.semantic_class = SemanticClass(name="semantic class", slug="semantic-class")
        self.semantic_class.save()
        self.semantic_class.senses.add(self.sense)


class BaseXMLTest(TestCase):

    def setUp(self):
        self.source_file = "dictionary/tests/resources/zootie.xml"
        self.x = XMLDict(self.source_file)
        self.x_as_dict = json.loads(json.dumps(self.x.xml_dict))


class BaseXMLParserTest(TestCase):

    def setUp(self):
        self.x = XmlFileReader.read_xml_file("dictionary/tests/resources/zootie.xml")
        self.j = JSONConverter.parse_to_dict(self.x)
        self.xml_dict = json.loads(json.dumps(self.j))

        self.zootie_entry_dict = {
            "@sk": "zootie",
            "@eid": "e11730",
            "@publish": "yes",
            "head": {
                "headword": "zootie"
            },
            "senses": [
                {
                    "@id": "e11730_n",
                    "pos": "noun",
                    "forms": [
                        {
                            "form": [
                                {
                                    "@freq": "5",
                                    "#text": "zootie"
                                }
                            ]
                        }
                    ],
                    "sense": [
                        {
                            "@id": "e11730_n_1",
                            "rhymes": {
                                "rhyme": [
                                    {
                                        "@freq": "2",
                                        "#text": "cutie"
                                    }
                                ]
                            },
                            "collocates": {
                                "collocate": [
                                    {
                                        "@freq": "1",
                                        "@target": "e3170_adj_1",
                                        "#text": "blunted"
                                    },
                                    {
                                        "@freq": "1",
                                        "@target": "e9000_intrV_1",
                                        "#text": "ride"
                                    }
                                ]
                            },
                            "domain": [
                                {
                                    "@type": "drugs"
                                },
                                {
                                    "@type": "marijuana"
                                }
                            ],
                            "sentiment": {
                                "@type": "neutral"
                            },
                            'synSetRef': [{
                                '@target': 'smokes'
                            }],
                            "definition": [
                                {
                                    "text": "a marijuana cigarette laced with cocaine"
                                }
                            ],
                            "xref": [
                                {
                                    "@type": "hasSynonym",
                                    "@target": "e8630_n_1",
                                    "#text": "primo"
                                },
                                {
                                    "@type": "conceptRelatesTo",
                                    "@target": "e8900_n_1",
                                    "#text": "reefer"
                                }
                            ],
                            "examples": {
                                "example": [
                                    {
                                        "@id": "3470",
                                        "date": "1989-07-25",
                                        "artist": "Beastie Boys",
                                        "songTitle": "Hey Ladies",
                                        "album": "Paul's Boutique",
                                        "lyric": {
                                            "text": "I met a little cutie, she was all hopped up on zootie",
                                            "rhyme": [
                                                {
                                                    "@rhymeTarget": "e11730_n_1",
                                                    "@position": "15",
                                                    "@rhymeTargetWord": "zootie",
                                                    "@rhymeTargetPosition": "47",
                                                    "#text": "cutie"
                                                }
                                            ],
                                            "rf": [
                                                {
                                                    "@target": "e11730_n_1",
                                                    "@position": "47",
                                                    "@lemma": "zootie",
                                                    "#text": "zootie"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "@id": "5033",
                                        "date": "1994-12-06",
                                        "artist": "Black Sheep",
                                        "songTitle": "We Boys",
                                        "feat": [
                                            "Legion, The"
                                        ],
                                        "album": "Non-Fiction",
                                        "lyric": {
                                            "text": "One love with the bang, riding with the zootie",
                                            "xref": [
                                                {
                                                    "@target": "e9000_intrV_1",
                                                    "@position": "24",
                                                    "@lemma": "ride",
                                                    "#text": "riding"
                                                }
                                            ],
                                            "rf": [
                                                {
                                                    "@target": "e11730_n_1",
                                                    "@position": "40",
                                                    "@lemma": "zootie",
                                                    "#text": "zootie"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "@id": "11290",
                                        "date": "1996-07-07",
                                        "artist": "De La Soul",
                                        "songTitle": "Intro",
                                        "album": "Stakes Is High",
                                        "lyric": {
                                            "text": "Big four gets the zootie for the self",
                                            "rf": [
                                                {
                                                    "@target": "e11730_n_1",
                                                    "@position": "18",
                                                    "@lemma": "zootie",
                                                    "#text": "zootie"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "@id": "17365",
                                        "date": "1999-07-13",
                                        "artist": "Gang Starr",
                                        "songTitle": "Discipline",
                                        "feat": [
                                            "Total"
                                        ],
                                        "album": "Full Clip",
                                        "lyric": {
                                            "text": "Used to get blunted down in the hallways, I love the cutie pies, never the zootie pies",
                                            "xref": [
                                                {
                                                    "@target": "e3170_adj_1",
                                                    "@position": "12",
                                                    "@lemma": "blunted",
                                                    "#text": "blunted"
                                                }
                                            ],
                                            "rhyme": [
                                                {
                                                    "@rhymeTarget": "e11730_n_1",
                                                    "@position": "53",
                                                    "@rhymeTargetWord": "zootie",
                                                    "@rhymeTargetPosition": "75",
                                                    "#text": "cutie"
                                                }
                                            ],
                                            "rf": [
                                                {
                                                    "@target": "e11730_n_1",
                                                    "@position": "75",
                                                    "@lemma": "zootie",
                                                    "#text": "zootie"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "@id": "38936",
                                        "date": "2003-10-07",
                                        "artist": "RZA",
                                        "songTitle": "A Day To God Is 1,000 Years (Stay With Me)",
                                        "album": "Birth of A Prince",
                                        "lyric": {
                                            "text": "Nigga, pass the zootie",
                                            "rf": [
                                                {
                                                    "@target": "e11730_n_1",
                                                    "@position": "16",
                                                    "@lemma": "zootie",
                                                    "#text": "zootie"
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        self.zootie_entry_nt = EntryParsed(headword='zootie', slug='zootie', sort_key='zootie', letter='z', publish=True, xml_dict={'@sk': 'zootie', '@eid': 'e11730', '@publish': 'yes', 'head': {'headword': 'zootie'}, 'senses': [{'@id': 'e11730_n', 'pos': 'noun', 'forms': [{'form': [{'@freq': '5', '#text': 'zootie'}]}], 'sense': [{'@id': 'e11730_n_1', 'rhymes': {'rhyme': [{'@freq': '2', '#text': 'cutie'}]}, 'collocates': {'collocate': [{'@freq': '1', '@target': 'e3170_adj_1', '#text': 'blunted'}, {'@freq': '1', '@target': 'e9000_intrV_1', '#text': 'ride'}]}, 'domain': [{'@type': 'drugs'}, {'@type': 'marijuana'}], 'sentiment': {'@type': 'neutral'}, 'synSetRef': [{'@target': 'smokes'}], 'definition': [{'text': 'a marijuana cigarette laced with cocaine'}], 'xref': [{'@type': 'hasSynonym', '@target': 'e8630_n_1', '#text': 'primo'}, {'@type': 'conceptRelatesTo', '@target': 'e8900_n_1', '#text': 'reefer'}], 'examples': {'example': [{'@id': '3470', 'date': '1989-07-25', 'artist': 'Beastie Boys', 'songTitle': 'Hey Ladies', 'album': "Paul's Boutique", 'lyric': {'text': 'I met a little cutie, she was all hopped up on zootie', 'rhyme': [{'@rhymeTarget': 'e11730_n_1', '@position': '15', '@rhymeTargetWord': 'zootie', '@rhymeTargetPosition': '47', '#text': 'cutie'}], 'rf': [{'@target': 'e11730_n_1', '@position': '47', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '5033', 'date': '1994-12-06', 'artist': 'Black Sheep', 'songTitle': 'We Boys', 'feat': ['Legion, The'], 'album': 'Non-Fiction', 'lyric': {'text': 'One love with the bang, riding with the zootie', 'xref': [{'@target': 'e9000_intrV_1', '@position': '24', '@lemma': 'ride', '#text': 'riding'}], 'rf': [{'@target': 'e11730_n_1', '@position': '40', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '11290', 'date': '1996-07-07', 'artist': 'De La Soul', 'songTitle': 'Intro', 'album': 'Stakes Is High', 'lyric': {'text': 'Big four gets the zootie for the self', 'rf': [{'@target': 'e11730_n_1', '@position': '18', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '17365', 'date': '1999-07-13', 'artist': 'Gang Starr', 'songTitle': 'Discipline', 'feat': ['Total'], 'album': 'Full Clip', 'lyric': {'text': 'Used to get blunted down in the hallways, I love the cutie pies, never the zootie pies', 'xref': [{'@target': 'e3170_adj_1', '@position': '12', '@lemma': 'blunted', '#text': 'blunted'}], 'rhyme': [{'@rhymeTarget': 'e11730_n_1', '@position': '53', '@rhymeTargetWord': 'zootie', '@rhymeTargetPosition': '75', '#text': 'cutie'}], 'rf': [{'@target': 'e11730_n_1', '@position': '75', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '38936', 'date': '2003-10-07', 'artist': 'RZA', 'songTitle': 'A Day To God Is 1,000 Years (Stay With Me)', 'album': 'Birth of A Prince', 'lyric': {'text': 'Nigga, pass the zootie', 'rf': [{'@target': 'e11730_n_1', '@position': '16', '@lemma': 'zootie', '#text': 'zootie'}]}}]}}]}]})

        self.zootie_entry_dict_forms_updated = {
                'senses': [{
                    'forms': [
                        {'form': [{'@freq': '5', '#text': 'zootie'}]},
                        {'form': [{'@freq': '1', '#text': 'zooties'}]},
                    ],
                    'pos': 'noun',
                    'sense': self.zootie_entry_dict['senses'][0]['sense']
                }],
                'head': {'headword': 'zootie'},
                '@sk': 'zootie',
                '@publish': 'yes',
                '@eid': 'e11730',
            }

        self.zootie_sense_dict = self.zootie_entry_dict['senses'][0]['sense'][0]
        self.zootie_sense_nt = SenseParsed(headword='zootie', slug='zootie#e11730_n_1', publish=True, xml_id='e11730_n_1', part_of_speech='noun', xml_dict={'@id': 'e11730_n_1', 'rhymes': {'rhyme': [{'@freq': '2', '#text': 'cutie'}]}, 'collocates': {'collocate': [{'@freq': '1', '@target': 'e3170_adj_1', '#text': 'blunted'}, {'@freq': '1', '@target': 'e9000_intrV_1', '#text': 'ride'}]}, 'domain': [{'@type': 'drugs'}, {'@type': 'marijuana'}], 'sentiment': {'@type': 'neutral'}, 'synSetRef': [{'@target': 'smokes'}], 'definition': [{'text': 'a marijuana cigarette laced with cocaine'}], 'xref': [{'@type': 'hasSynonym', '@target': 'e8630_n_1', '#text': 'primo'}, {'@type': 'conceptRelatesTo', '@target': 'e8900_n_1', '#text': 'reefer'}], 'examples': {'example': [{'@id': '3470', 'date': '1989-07-25', 'artist': 'Beastie Boys', 'songTitle': 'Hey Ladies', 'album': "Paul's Boutique", 'lyric': {'text': 'I met a little cutie, she was all hopped up on zootie', 'rhyme': [{'@rhymeTarget': 'e11730_n_1', '@position': '15', '@rhymeTargetWord': 'zootie', '@rhymeTargetPosition': '47', '#text': 'cutie'}], 'rf': [{'@target': 'e11730_n_1', '@position': '47', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '5033', 'date': '1994-12-06', 'artist': 'Black Sheep', 'songTitle': 'We Boys', 'feat': ['Legion, The'], 'album': 'Non-Fiction', 'lyric': {'text': 'One love with the bang, riding with the zootie', 'xref': [{'@target': 'e9000_intrV_1', '@position': '24', '@lemma': 'ride', '#text': 'riding'}], 'rf': [{'@target': 'e11730_n_1', '@position': '40', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '11290', 'date': '1996-07-07', 'artist': 'De La Soul', 'songTitle': 'Intro', 'album': 'Stakes Is High', 'lyric': {'text': 'Big four gets the zootie for the self', 'rf': [{'@target': 'e11730_n_1', '@position': '18', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '17365', 'date': '1999-07-13', 'artist': 'Gang Starr', 'songTitle': 'Discipline', 'feat': ['Total'], 'album': 'Full Clip', 'lyric': {'text': 'Used to get blunted down in the hallways, I love the cutie pies, never the zootie pies', 'xref': [{'@target': 'e3170_adj_1', '@position': '12', '@lemma': 'blunted', '#text': 'blunted'}], 'rhyme': [{'@rhymeTarget': 'e11730_n_1', '@position': '53', '@rhymeTargetWord': 'zootie', '@rhymeTargetPosition': '75', '#text': 'cutie'}], 'rf': [{'@target': 'e11730_n_1', '@position': '75', '@lemma': 'zootie', '#text': 'zootie'}]}}, {'@id': '38936', 'date': '2003-10-07', 'artist': 'RZA', 'songTitle': 'A Day To God Is 1,000 Years (Stay With Me)', 'album': 'Birth of A Prince', 'lyric': {'text': 'Nigga, pass the zootie', 'rf': [{'@target': 'e11730_n_1', '@position': '16', '@lemma': 'zootie', '#text': 'zootie'}]}}]}}, definition='a marijuana cigarette laced with cocaine', notes='', etymology='')

        self.zootie_form_dict1 = {'form': [{'@freq': '6', '#text': 'zootie'}]}
        self.zootie_form_dict2 = {'form': [{'@freq': '2', '#text': 'zooties'}]}
        self.zootie_form_dict3 = {'form': [{'@freq': '1', '#text': 'zooty'}]}

        self.zootie_form_nt1 = FormParsed(slug='zootie', label='zootie', frequency=6)
        self.zootie_form_nt2 = FormParsed(slug='zooties', label='zooties', frequency=2)
        self.zootie_form_nt3 = FormParsed(slug='zooty', label='zooty', frequency=1)

        self.zootie_example_dict = self.zootie_sense_dict['examples']['example'][0]
        self.zootie_example_nt = ExampleParsed(primary_artists=['Beastie Boys'], song_title='Hey Ladies', featured_artists=[], release_date='1989-07-25', release_date_string='1989-07-25', album="Paul's Boutique", lyric_text='I met a little cutie, she was all hopped up on zootie', xml_id='3470')

        self.zootie_example_dict1 = self.zootie_sense_dict['examples']['example'][1]
        self.zootie_example_nt1 = ExampleParsed(primary_artists=['Black Sheep'], song_title='We Boys', featured_artists=['Legion, The'], release_date='1994-12-06', release_date_string='1994-12-06', album='Non-Fiction', lyric_text='One love with the bang, riding with the zootie', xml_id='5033')

        self.zootie_song_nt = SongParsed(xml_id='3470', slug='beastie-boys-hey-ladies', title='Hey Ladies', artist_name='Beastie Boys', artist_slug='beastie-boys', release_date='1989-07-25', release_date_string='1989-07-25', album="Paul's Boutique")

