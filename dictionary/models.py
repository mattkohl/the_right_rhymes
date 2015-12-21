import datetime

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class Entry(models.Model):
    headword = models.CharField(primary_key=True, max_length=200)
    slug = models.SlugField(max_length=200)
    publish = models.BooleanField(default=False)
    pub_date = models.DateTimeField('Date Published', auto_now_add=True, blank=True)
    json = JSONField(null=True, blank=True)
    image = models.ForeignKey('Image', on_delete=models.CASCADE, related_name="entry_image", null=True, blank=True)
    senses = models.ManyToManyField('Sense', related_name='+', blank=True)

    def __str__(self):
        return self.headword

    def published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Editor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Editor Name', max_length=1000)
    slug = models.SlugField('Slug')

    def __str__(self):
        return self.name


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('Image Title', max_length=1000)
    slug = models.SlugField('Slug')
    image = models.ImageField()

    def __str__(self):
        return self.title


class Artist(models.Model):
    name = models.CharField(primary_key=True, max_length=1000)
    slug = models.SlugField('Artist Slug')
    origin = models.CharField('Origin', max_length=1000, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="depicts", null=True, blank=True)
    primary_examples = models.ManyToManyField('Example', related_name="+")
    featured_examples = models.ManyToManyField('Example', related_name="+")

    def __str__(self):
        if self.origin:
            return self.name + ' (' + self.origin + ')'
        else:
            return self.name


class Sense(models.Model):
    id = models.AutoField(primary_key=True)
    headword = models.CharField('Headword', max_length=200, null=True, blank=True)
    xml_id = models.CharField('Legacy XML id', max_length=20, null=True, blank=True)
    part_of_speech = models.CharField('Part of Speech', max_length=20)
    json = JSONField(null=True, blank=True)
    parent_entry = models.ManyToManyField(Entry, through=Entry.senses.through, related_name="+")
    examples = models.ManyToManyField('Example', related_name="+")
    domains = models.ManyToManyField('Domain', related_name="+")
    synset = models.ManyToManyField('SynSet', related_name="+")

    def __str__(self):
        return self.headword + ', ' + self.part_of_speech + ' (' + self.xml_id + ')'


class Example(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ManyToManyField(Artist, through=Artist.primary_examples.through, related_name="+")
    artist_name = models.CharField('Artist Name', max_length=200, null=True, blank=True)
    song_title = models.CharField('Song Title', max_length=200)
    feat_artist = models.ManyToManyField(Artist, through=Artist.featured_examples.through, related_name="+")
    release_date = models.DateField('Release Date', blank=True, null=True)
    release_date_string = models.CharField('Release Date String', max_length=10, blank=True, null=True)
    album = models.CharField('Album', max_length=200)
    lyric_text = models.CharField('Lyric Text', max_length=1000)
    json = JSONField(null=True, blank=True)
    illustrates_senses = models.ManyToManyField(Sense, through=Sense.examples.through, related_name="+")
    features_entities = models.ManyToManyField('Entity', related_name="+")

    def __str__(self):
        return '[' + str(self.release_date_string) + '] ' + str(self.artist_name) + ' - ' + str(self.lyric_text)


class SynSet(models.Model):
    name = models.CharField(primary_key=True, max_length=1000)
    senses = models.ManyToManyField('Sense', through=Sense.synset.through, related_name='+', blank=True)

    def __str__(self):
        return self.name


class Domain(models.Model):
    name = models.CharField(primary_key=True, max_length=1000)
    senses = models.ManyToManyField('Sense', through=Sense.domains.through, related_name='+', blank=True)

    def __str__(self):
        return self.name


class Entity(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=1000)
    examples = models.ManyToManyField(Example, through=Example.features_entities.through, related_name='+', blank=True)

    def __str__(self):
        return self.name
