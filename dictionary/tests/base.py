from django.test import TestCase

from dictionary.models import Entry, Artist, Domain, Collocate, Sense, Region, SemanticClass, Song, NamedEntity, LyricLink, Example, Place, Xref


class BaseTest(TestCase):

    def setUp(self):
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
        self.epmd = Artist(name='EPMD', slug="epmd")
        self.epmd.save()
        self.erick_sermon = Artist(name="Erick Sermon", slug="erick-sermon")
        self.erick_sermon.save()
        self.example_2.artist.add(self.epmd)
        self.brentwood = Place(name="Brentwood", full_name="Brentwood, New York, USA", slug="brentwood-new-york-usa")
        self.brentwood.save()
        self.epmd.origin.add(self.brentwood)
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
        self.lyric_link_1.save()
        self.lyric_link_2.save()
        self.lyric_link_3.save()
        self.example_2.lyric_links.add(self.lyric_link_1)
        self.example_2.lyric_links.add(self.lyric_link_2)
        self.example_2.lyric_links.add(self.lyric_link_3)
        self.published_headwords = ['rock', 'loco']
        self.collocate = Collocate(
            collocate_lemma="lemma",
            source_sense_xml_id="x1",
            target_slug="target1",
            target_id="target1",
            frequency=1
        )
        self.xref = Xref(
            xref_word="word",
            xref_type="type",
            target_lemma="target_lemma",
            target_slug="target_slug",
            target_id="target_id",
            frequency=1,
            position=1
        )
        self.entry = Entry(headword="headword", slug="headword", pub_date="2017-01-01", last_updated="2017-01-01")

        self.oprah = NamedEntity(name="Oprah", slug="oprah", entity_type="person", pref_label="Oprah Winfrey", pref_label_slug="oprah-winfrey")
        self.oprah.save()
        self.mad = Entry(headword="foo", slug="foo", letter="f", publish=True)
        self.mad.save()
        self.foo_sense = Sense(headword="foo", slug="foo", xml_id="bar", part_of_speech="noun")
        self.foo_sense.save()
        self.mad.senses.add(self.foo_sense)
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
        self.method_man = Artist(name="Method Man", slug="method-man")
        self.method_man.save()
        self.example_3.feat_artist.add(self.method_man)
        self.sense = Sense(headword="headword", part_of_speech="noun", xml_id="foo", slug="headword")
        self.sense.save()