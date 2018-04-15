from collections import Counter, OrderedDict
import operator
import math
import logging
from django.db import models
from django.db.models import Count
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from dictionary.utils import slugify, extract_short_name

logger = logging.getLogger(__name__)


class Artist(models.Model):
    name = models.CharField('Artist Name', max_length=1000, null=True, blank=True)
    slug = models.SlugField(primary_key=True, db_index=True)
    origin = models.ManyToManyField('Place', related_name="+")
    primary_examples = models.ManyToManyField('Example', related_name="+", blank=True)
    primary_senses = models.ManyToManyField('Sense', related_name="+", blank=True)
    featured_examples = models.ManyToManyField('Example', related_name="+", blank=True)
    featured_senses = models.ManyToManyField('Sense', related_name="+", blank=True)
    primary_songs = models.ManyToManyField('Song', related_name="+", blank=True)
    featured_songs = models.ManyToManyField('Song', related_name="+", blank=True)
    also_known_as = models.ManyToManyField("self", blank=True, symmetrical=True)
    member_of = models.ManyToManyField("self", related_name="members", blank=True, symmetrical=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('artist', args=[str(self.slug)])

    def add_aka(self, aka_name):
        aka_slug = slugify(aka_name)
        aka = Artist.objects.filter(slug=aka_slug).first()
        if aka:
            logger.info(self.name + ' now also known as ' + aka.name)
            self.also_known_as.add(aka)

    def add_origin(self, place_name):
        place_slug = slugify(place_name)
        place = Place.objects.filter(slug=place_slug).first()
        if place:
            logger.info('Adding origin ' + place.name + ' to ' + self.name)
            self.origin.add(place)

    def get_primary_sense_example_counts(self):
        return Counter([sense for sense in self.primary_senses.filter(publish=True) for _ in sense.examples.filter(artist_name=self.name)])

    def tf(self, sense):
        a_count = sense.examples.filter(artist_name=self.name).count()
        e_count = self.primary_examples.count()
        return a_count / e_count

    def tfidf(self, sense):
        return self.tf(sense) * sense.idf()

    def get_tfidfs(self, senses=list()):
        if senses:
            results = {sense: self.tfidf(sense) for sense in senses}
        else:
            results = {sense: self.tfidf(sense) for sense in self.primary_senses.filter(publish=True)}

        return OrderedDict(sorted(results.items(), key=operator.itemgetter(1), reverse=True))

    def get_salient_senses(self):
        return Salience.objects.filter(artist=self).order_by("-score")


class Editor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Editor Name', max_length=1000)
    slug = models.SlugField('Slug')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Entry(models.Model):
    headword = models.CharField(primary_key=True, max_length=200)
    sort_key = models.CharField(max_length=200, null=True, blank=True)
    letter = models.CharField(max_length=1, null=True, blank=True)
    slug = models.SlugField('Headword Slug', db_index=True)
    publish = models.BooleanField(default=False, db_index=True)
    forms = models.ManyToManyField('Form', related_name='+', blank=True)
    pub_date = models.DateTimeField('Date Published', auto_now_add=True, blank=True)
    last_updated = models.DateField('Last Updated', auto_now=True, null=True, blank=True)
    json = JSONField(null=True, blank=True)
    senses = models.ManyToManyField('Sense', related_name='+', blank=True)

    class Meta:
        ordering = ["headword"]
        verbose_name_plural = "Entries"

    def __str__(self):
        return self.headword

    def get_senses_ordered_by_example_count(self):
        return [sense for sense in self.senses.annotate(num_examples=Count('examples')).order_by('-num_examples')]

    def get_absolute_url(self):
        return reverse('entry', args=[str(self.slug)])


class Form(models.Model):
    slug = models.SlugField('Form Slug', primary_key=True, db_index=True)
    label = models.CharField(max_length=1000)
    parent_entry = models.ManyToManyField(Entry, through=Entry.forms.through, related_name="+")
    frequency = models.IntegerField(blank=True, null=True)


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    slug = models.CharField('Place Slug', max_length=1000, db_index=True, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    comment = models.CharField(max_length=10000, null=True, blank=True)
    artists = models.ManyToManyField(Artist, through=Artist.origin.through, related_name="+")
    contains = models.ManyToManyField("self", blank=True, symmetrical=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('place', args=[str(self.slug)])

    @classmethod
    def create(cls, full_name):
        slug = slugify(full_name)
        name = extract_short_name(full_name)
        place = cls(slug=slug, full_name=full_name, name=name)
        return place


class Sense(models.Model):
    id = models.AutoField(primary_key=True)
    headword = models.CharField('Headword', db_index=True, max_length=200, null=True, blank=True)
    slug = models.SlugField('Sense Slug', null=True, blank=True)
    publish = models.BooleanField(default=False, db_index=True)
    xml_id = models.CharField('XML id', db_index=True, max_length=50, null=True, blank=True)
    part_of_speech = models.CharField('Part of Speech', max_length=100)
    json = JSONField(null=True, blank=True)
    parent_entry = models.ManyToManyField(Entry, through=Entry.senses.through, related_name="+")
    definition = models.CharField(max_length=2000, null=True, blank=True)
    etymology = models.CharField(max_length=2000, null=True, blank=True)
    notes = models.CharField(max_length=2000, null=True, blank=True)
    examples = models.ManyToManyField('Example', db_index=True, related_name="+")
    domains = models.ManyToManyField('Domain', related_name="+", blank=True)
    regions = models.ManyToManyField('Region', related_name="+", blank=True)
    semantic_classes = models.ManyToManyField('SemanticClass', related_name="+", blank=True)
    synset = models.ManyToManyField('SynSet', related_name="+", blank=True)
    xrefs = models.ManyToManyField('Xref', related_name="+", blank=True)
    sense_rhymes = models.ManyToManyField('SenseRhyme', related_name="+", blank=True)
    collocates = models.ManyToManyField('Collocate', related_name="+", blank=True)
    features_entities = models.ManyToManyField('NamedEntity', related_name="+", blank=True)
    cites_artists = models.ManyToManyField(Artist, through=Artist.primary_senses.through, related_name="+")

    class Meta:
        ordering = ["xml_id"]

    def __str__(self):
        if self.headword and self.part_of_speech:
            return self.headword + ', ' + self.part_of_speech + ' (' + self.xml_id + ')'
        else:
            return self.xml_id

    def get_artist_example_count(self):
        return Counter([a.name for ex in self.examples.all() for a in ex.artist.all()])

    def idf(self):
        sa_count = self.cites_artists.count()
        a_count = Artist.objects.count()
        log_count = math.log10(a_count / sa_count)
        return log_count

    def tf(self, artist):
        a_count = self.examples.filter(artist_name=artist.name).count()
        e_count = self.examples.count()
        return a_count / e_count

    def tfidf(self, artist):
        return self.tf(artist) * self.idf()

    def get_tfidfs(self, artists=list()):
        if artists:
            results = {artist: self.tfidf(artist) for artist in artists}
        else:
            results = {artist: self.tfidf(artist) for artist in self.cites_artists.all()}
        return OrderedDict(sorted(results.items(), key=operator.itemgetter(1), reverse=True))

    def remove_saliences(self):
        old = Salience.objects.filter(sense=self)
        count = old.count()
        for o in old:
            o.delete()
            msg = "Removed {} Saliences from {}".format(count, self)
            logger.info(msg)

    def add_saliences(self):
        scores = self.get_tfidfs()
        for key in scores:
            s = Salience(sense=self, artist=key, score=scores[key])
            logger.info(s)
            s.save()


class Salience(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    sense = models.ForeignKey(Sense, on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        ordering = ["score"]

    def __str__(self):
        return self.artist.name + ' / ' + self.sense.headword + ' (' + self.sense.xml_id + '): ' + str(self.score)

    def to_dict(self):
        return {
            "artist": {
                "name": self.artist.name,
                "slug": self.artist.slug
            },
            "sense": {
                "headword": self.sense.headword,
                "xml_id": self.sense.xml_id
            },
            "score": self.score
        }


class Song(models.Model):
    id = models.AutoField(primary_key=True)
    xml_id = models.CharField('XML id', db_index=True, max_length=50, null=True, blank=True)
    slug = models.CharField('Slug', max_length=1000, db_index=True, null=True, blank=True)
    title = models.CharField('Title', max_length=1000)
    artist = models.ManyToManyField(Artist, through=Artist.primary_songs.through, related_name="+")
    artist_name = models.CharField('Artist Name', max_length=200, null=True, blank=True)
    artist_slug = models.SlugField('Artist Slug', blank=True, null=True)
    feat_artist = models.ManyToManyField(Artist, through=Artist.featured_songs.through, related_name="+", blank=True)
    release_date = models.DateField('Release Date', db_index=True, blank=True, null=True)
    release_date_string = models.CharField('Release Date String', max_length=10, blank=True, null=True)
    album = models.CharField('Album', max_length=200)
    examples = models.ManyToManyField('Example', db_index=True, related_name="+", blank=True)
    lyrics = models.TextField('Lyrics', null=True, blank=True)
    release_date_verified = models.BooleanField('Release Date Verified', default=False)

    class Meta:
        ordering = ["title", "artist_name"]

    def __str__(self):
        return '"' + str(self.title) + '" (' + str(self.artist_name) + ') '

    def get_absolute_url(self):
        return reverse('song', args=[str(self.slug)])


class SynSet(models.Model):
    name = models.CharField(primary_key=True, max_length=1000)
    slug = models.SlugField('SynSet Slug', blank=True, null=True)
    senses = models.ManyToManyField('Sense', through=Sense.synset.through, related_name='+', blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "SynSets"

    def __str__(self):
        return self.name


class SemanticClass(models.Model):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(primary_key=True, max_length=1000)
    senses = models.ManyToManyField('Sense', through=Sense.semantic_classes.through, related_name='+', blank=True)
    broader = models.ManyToManyField("self", blank=True, symmetrical=False)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Semantic Classes"

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"name": self.name, "slug": self.slug}


class Domain(models.Model):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(primary_key=True, max_length=1000)
    senses = models.ManyToManyField('Sense', through=Sense.domains.through, related_name='+', blank=True)
    broader = models.ManyToManyField("self", blank=True, symmetrical=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"name": self.name, "slug": self.slug}


class Region(models.Model):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(primary_key=True, max_length=1000)
    senses = models.ManyToManyField('Sense', through=Sense.regions.through, related_name='+', blank=True)
    broader = models.ManyToManyField("self", blank=True, symmetrical=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"name": self.name, "slug": self.slug}


class Xref(models.Model):
    id = models.AutoField(primary_key=True)
    xref_word = models.CharField(db_index=True, max_length=1000, blank=True, null=True)
    xref_type = models.CharField(db_index=True, max_length=1000, blank=True, null=True)
    target_lemma = models.CharField(max_length=1000, blank=True, null=True)
    target_slug = models.SlugField(blank=True, null=True)
    target_id = models.CharField(max_length=1000, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    frequency = models.IntegerField(blank=True, null=True)
    parent_sense = models.ManyToManyField(Sense, through=Sense.xrefs.through, related_name="+")

    class Meta:
        ordering = ["xref_word"]

    def __str__(self):
        return self.xref_word

    def to_dict(self):
        base = {
            "xref_word": self.xref_word,
            "xref_type": self.xref_type,
            "target_lemma": self.target_lemma,
            "target_slug": self.target_slug,
            "target_id": self.target_id,
        }
        if self.frequency:
            base.update({"frequency": self.frequency})
        if self.position:
            base.update({"position": self.position})
        return base


class Collocate(models.Model):
    id = models.AutoField(primary_key=True)
    collocate_lemma = models.CharField(max_length=1000, blank=True, null=True)
    source_sense_xml_id = models.CharField('Source XML ID', max_length=20, null=True, blank=True)
    target_slug = models.SlugField(blank=True, null=True)
    target_id = models.CharField(max_length=1000, blank=True, null=True)
    frequency = models.IntegerField(db_index=True, blank=True, null=True)
    parent_sense = models.ManyToManyField(Sense, through=Sense.collocates.through, related_name="+")

    class Meta:
        ordering = ["collocate_lemma"]

    def __str__(self):
        return self.collocate_lemma
    
    def to_dict(self):
        base = {
            "collocate_lemma": self.collocate_lemma,
            "source_sense_xml_id": self.source_sense_xml_id,
            "target_slug": self.target_slug,
            "target_id": self.target_id,
            "frequency": self.frequency
        }
        if self.frequency:
            base.update({"frequency": self.frequency})
        return base


class SenseRhyme(models.Model):
    id = models.AutoField(primary_key=True)
    rhyme = models.CharField(max_length=1000, blank=True, null=True)
    rhyme_slug = models.SlugField(db_index=True, blank=True, null=True)
    parent_sense_xml_id = models.CharField('Source XML ID', max_length=20, null=True, blank=True)
    parent_sense = models.ManyToManyField(Sense, through=Sense.sense_rhymes.through, related_name="+")
    frequency = models.IntegerField(db_index=True, blank=True, null=True)

    class Meta:
        ordering = ["rhyme"]

    def __str__(self):
        return self.rhyme + ' - ' + self.parent_sense_xml_id

    def to_dict(self):
        return {
            "rhyme": self.rhyme,
            "rhyme_slug": self.rhyme_slug,
            "parent_sense_xml_id": self.parent_sense_xml_id,
            "frequency": self.frequency,
        }


class Example(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ManyToManyField(Artist, through=Artist.primary_examples.through, related_name="+")
    artist_name = models.CharField('Artist Name', max_length=200, null=True, blank=True)
    artist_slug = models.SlugField('Artist Slug', blank=True, null=True)
    song_title = models.CharField('Song Title', max_length=200)
    from_song = models.ManyToManyField(Song, through=Song.examples.through, related_name="+")
    feat_artist = models.ManyToManyField(Artist, through=Artist.featured_examples.through, related_name="+", blank=True)
    release_date = models.DateField('Release Date', db_index=True, blank=True, null=True)
    release_date_string = models.CharField('Release Date String', max_length=10, blank=True, null=True)
    album = models.CharField('Album', max_length=200)
    lyric_text = models.CharField('Lyric Text', max_length=1000)
    json = JSONField(null=True, blank=True)
    example_rhymes = models.ManyToManyField('ExampleRhyme', related_name="+")
    illustrates_senses = models.ManyToManyField(Sense, through=Sense.examples.through, related_name="+")
    features_entities = models.ManyToManyField('NamedEntity', db_index=True, related_name="+", blank=True)
    lyric_links = models.ManyToManyField('LyricLink', related_name="+")

    class Meta:
        ordering = ["release_date", "artist_name"]

    def __str__(self):
        return '[' + str(self.release_date_string) + '] ' + str(self.artist_name) + ' - ' + str(self.lyric_text)


class ExampleRhyme(models.Model):
    id = models.AutoField(primary_key=True)
    word_one = models.CharField(max_length=1000, blank=True, null=True)
    word_two = models.CharField(max_length=1000, blank=True, null=True)
    word_one_slug = models.SlugField(db_index=True, blank=True, null=True)
    word_two_slug = models.SlugField(db_index=True, blank=True, null=True)
    word_one_target_id = models.CharField(max_length=1000, blank=True, null=True)
    word_two_target_id = models.CharField(max_length=1000, blank=True, null=True)
    word_one_position = models.IntegerField(blank=True, null=True)
    word_two_position = models.IntegerField(blank=True, null=True)
    parent_example = models.ManyToManyField(Example, through=Example.example_rhymes.through, related_name="+")

    class Meta:
        ordering = ["word_one", "word_two"]

    def __str__(self):
        return self.word_one + ' - ' + self.word_two


class LyricLink(models.Model):
    id = models.AutoField(primary_key=True)
    link_type = models.CharField(max_length=1000, blank=True, null=True)
    link_text = models.CharField(max_length=1000, blank=True, null=True)
    target_lemma = models.CharField(max_length=1000, blank=True, null=True)
    target_slug = models.SlugField(max_length=1000, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    parent_example = models.ManyToManyField(Example, through=Example.lyric_links.through, related_name="+")

    class Meta:
        ordering = ["link_text"]

    def __str__(self):
        return self.link_text


class NamedEntity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField('Entity Slug', max_length=1000, blank=True, null=True)
    pref_label = models.CharField(max_length=1000, blank=True, null=True)
    pref_label_slug = models.SlugField('Entity PrefLabel Slug', max_length=1000, db_index=True, blank=True, null=True)
    entity_type = models.CharField(max_length=1000, blank=True, null=True)
    mentioned_at_senses = models.ManyToManyField(Sense, through=Sense.features_entities.through, related_name="+", blank=True)
    examples = models.ManyToManyField(Example, through=Example.features_entities.through, related_name='+', blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Named Entities"

    def __str__(self):
        return self.name


class Stats(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    json = JSONField(null=True, blank=True)

    def __str__(self):
        return self.created.strftime("%a, %d %b %Y %H:%M:%S")
