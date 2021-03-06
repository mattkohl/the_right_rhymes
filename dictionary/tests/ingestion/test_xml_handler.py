from unittest import mock
from collections import OrderedDict
from dictionary.tests.base import BaseXMLTest, BaseTest
from dictionary.management.commands.xml_handler import XMLDict, TRRDict, TRREntry, TRRSense, TRRExample, TRRLyricLink, TRRPlace, TRRSong
from dictionary.models import Place, Form, Entry


class TestXMLDict(BaseXMLTest):

    def test_cannot_read_file(self):
        with self.assertRaises(Exception):
            XMLDict("foo.xml")

    def test_malformed_file(self):
        with self.assertRaises(Exception):
            x = XMLDict("dictionary/tests/resources/malformed.xml")
            x.get_json()

    def test_xml_dict(self):
        self.assertIn('<?xml version="1.0"', str(self.x.xml_string))

    def test_get_json(self):
        self.assertIsInstance(self.x.xml_dict, OrderedDict)
        self.assertTrue('dictionary' in self.x.xml_dict)


class TestTRRDict(BaseTest):

    def test_no_dictionary_key(self):
        with self.assertRaises(Exception):
            TRRDict({})

    def test_no_entry_key(self):
        with self.assertRaises(Exception):
            TRRDict({"dictionary": {"entries": []}})

    @mock.patch("dictionary.management.commands.xml_handler.TRRDict.print_stats")
    def test_construct_2(self, mock_print_stats):
        mock_print_stats.return_value = ""
        result = TRRDict({"dictionary": {"entry": []}})
        self.assertEqual(result.entry_count, 0)
        self.assertEqual(str(result), "Python dict representation of The Right Rhymes. Entry count: 0")

    def test_print_stats(self):
        result = TRRDict({"dictionary": {"entry": []}})
        self.assertEqual(str(result), "Python dict representation of The Right Rhymes. Entry count: 0")


class TestTRREntry(BaseTest):

    entry_dict = {
            'senses': [{
                'forms': [
                    {'form': [{'@freq': '6', '#text': 'zootie'}]},
                    {'form': [{'@freq': '2', '#text': 'zooties'}]},
                    {'form': [{'@freq': '1', '#text': 'zooty'}]},
                ],
                'pos': 'noun',
                'sense': [{}]
            }],
            'head': {'headword': 'zootie'},
            '@sk': 'zootie',
            '@publish': 'yes',
            '@eid': 'e11730',
        }

    entry_dict_updated = {
            'senses': [{
                'forms': [
                    {'form': [{'@freq': '5', '#text': 'zootie'}]},
                    {'form': [{'@freq': '1', '#text': 'zooties'}]},
                ],
                'pos': 'noun',
                'sense': [{}]
            }],
            'head': {'headword': 'zootie'},
            '@sk': 'zootie',
            '@publish': 'yes',
            '@eid': 'e11730',
        }

    @mock.patch("dictionary.management.commands.xml_handler.TRREntry.process_sense")
    def test_construct(self, mock_process_sense):
        mock_process_sense.return_value = None
        TRREntry(self.entry_dict)

        z_form = Form.objects.get(slug="zootie")
        self.assertEquals(z_form.frequency, 6)
        zs_form = Form.objects.get(slug="zooties")
        self.assertEquals(zs_form.frequency, 2)
        zy_form = Form.objects.get(slug="zooty")
        self.assertEquals(zy_form.frequency, 1)
        response = self.client.get("/search/?q=zooties")
        self.assertRedirects(response, "/zootie/")
        zootie = Entry.objects.get(slug="zootie")
        self.assertEqual(zootie.forms.count(), 3)

    @mock.patch("dictionary.management.commands.xml_handler.TRREntry.process_sense")
    def test_update_forms(self, mock_process_sense):
        mock_process_sense.return_value = None

        TRREntry(self.entry_dict)

        z_form = Form.objects.get(slug="zootie")
        self.assertEquals(z_form.frequency, 6)
        zs_form = Form.objects.get(slug="zooties")
        self.assertEquals(zs_form.frequency, 2)

        TRREntry(self.entry_dict_updated)

        z_form = Form.objects.get(slug="zootie")
        self.assertEquals(z_form.frequency, 5)
        zs_form = Form.objects.get(slug="zooties")
        self.assertEquals(zs_form.frequency, 1)
        self.assertIn(('madder',), Form.objects.values_list("slug"))
        # self.assertNotIn(('zooty',), Form.objects.values_list("slug"))


class TestTRRSense(BaseTest):

    def test_construct(self):
        headword = "mad"
        publish = True
        pos = "noun"
        sense = {
            "@id": "someId",
            "definition": [{"text": "some definition"}],
            "examples": [],
            "domain": [],
            "region": [],
            "semanticClass": [],
            "synSetRef": OrderedDict({"@target": "foo"}),
            "collocates": {"collocate": []},
            "xref": [],

        }
        result = TRRSense(self.mad_entry, headword, pos, sense, publish)
        self.assertIsInstance(result, TRRSense)


class TestTRRExample(BaseTest):

    @mock.patch("dictionary.management.commands.xml_handler.TRRExample.update_example")
    def test_construct(self, mock_update_example):
        mock_update_example.return_value = None
        example_dict = {
            "@id": "someId",
            "date": "2017-05-05",
            "songTitle": "Jammin",
            "album": "Foo",
            "artist": "Bar",
            "lyric": {"text": "Baz"}
        }
        result = TRRExample(self.mad_sense, example_dict)
        self.assertIsInstance(result, TRRExample)


class TestTRRSong(BaseTest):

    def test_construct(self):

        class Artist_(object):
            def __init__(self, artist_object):
                self.artist_object = artist_object

        es_ = Artist_(self.erick_sermon)

        xml_id = "a1234"
        release_date = "1998-01-01"
        title = "foo"
        album = "bar"
        artist_name = "Erick Sermon"
        slug = "erick-sermon-foo"
        artist_slug = "erick-sermon"
        result = TRRSong(xml_id=xml_id,
                         release_date=release_date,
                         release_date_string=release_date,
                         song_title=title,
                         artist_name=artist_name,
                         artist_slug=artist_slug,
                         primary_artists=[es_],
                         feat_artists=[],
                         album=album)
        self.assertIsInstance(result, TRRSong)
        self.assertEqual(result.slug, slug)


class TestTRRPlace(BaseTest):

    def test_construct(self):
        result = TRRPlace("Paris, Texas, USA")
        self.assertIsInstance(result, TRRPlace)
        self.assertEqual(Place.objects.filter(slug="paris-texas-usa").count(), 1)
        self.assertEqual(Place.objects.filter(slug="texas-usa").count(), 1)


class TestTRRLyricLink(BaseTest):

    bad_position_ex = {
        'album': 'By Any Means',
        'songTitle': 'Arm and Hammer',
        'artist': 'Kevin Gates',
        '@id': '51232',
        'date': '2014-03-18',
        'lyric': {
            'text': 'She like, "Bae, I\'m at the store"',
            'rf': [{'@lemma': 'bae', '@position': '12', '#text': 'Bae', '@target': 'e2667_n_1'}]
         }
    }
    good_position_ex = {
        'album': 'King Push',
        'songTitle': 'Drug Dealers Anonymous',
        'artist': 'Pusha T',
        '@id': '66175',
        'feat': ['Jay Z'],
        'date': '2015-12-18',
        'lyric': {
            'text': 'He told 12, "Gimme 12"',
            'rf': [
                {'@lemma': '12', '@position': '8', '#text': '12', '@target': 'e2045_n_1'},
                {'@lemma': '12', '@position': '19', '#text': '12', '@target': 'e2045_n_1'}
            ]
        }
    }

    def test_fix_bad_position(self):
        link_dict = self.bad_position_ex['lyric']['rf'][0]
        link_type = 'rf'
        example_text = self.bad_position_ex['lyric']['text']
        l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
        self.assertEqual(l1.position, 11)

    def test_confirm_good_position(self):
        link_dict = self.good_position_ex['lyric']['rf'][0]
        link_type = 'rf'
        example_text = self.good_position_ex['lyric']['text']
        l1 = TRRLyricLink(link_dict=link_dict, link_type=link_type, example_text=example_text)
        self.assertEqual(l1.position, 8)

