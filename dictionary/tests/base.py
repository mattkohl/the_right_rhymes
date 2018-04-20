from django.test import TestCase
import json
from dictionary.models import Entry, Artist, Domain, Collocate, Sense, Region, SemanticClass, Song, NamedEntity, LyricLink, Example, Place, Xref
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
        self.mad_sense = Sense(headword="mad", slug="mad", xml_id="bar", part_of_speech="adj", publish=True)
        self.mad_sense.save()
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
