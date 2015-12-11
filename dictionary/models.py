import datetime

from django.db import models
from django.utils import timezone


class Editor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Editor Name', max_length=1000)
    slug = models.SlugField('Editor Slug')

    def __str__(self):
        return self.name


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('Image Title', max_length=1000)
    slug = models.SlugField('Image Slug')
    image = models.ImageField()

    def __str__(self):
        return self.title


class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Artist Name', max_length=1000)
    slug = models.SlugField('Artist Slug')
    origin = models.CharField('Origin', max_length=1000, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="depicts", null=True, blank=True)

    def __str__(self):
        return self.name


class Word(models.Model):
    form = models.CharField('form', max_length=1000)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="image_for_entries", null=True, blank=True)
    senses = models.ManyToManyField('Sense', blank=True, related_name="has_form")
    rhymes_with = models.ManyToManyField('self', blank=True)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.form


class Sense(models.Model):
    id = models.AutoField(primary_key=True)
    pub_date = models.DateTimeField('Date Published')
    pub_by = models.ForeignKey(Editor, on_delete=models.CASCADE, related_name="edited")
    part_of_speech = models.CharField('Part of Speech', max_length=20)
    definition = models.TextField('Definition')
    etymology = models.TextField('Etymology', null=True, blank=True)
    domain = models.ManyToManyField('Domain', related_name="senses", blank=True)
    synset = models.ForeignKey('SynSet', on_delete=models.CASCADE, related_name="senses", null=True, blank=True)
    examples = models.ManyToManyField('Example', related_name="illustrates")
    relates_to = models.ManyToManyField('self', symmetrical=False, related_name="related_to", blank=True)
    descendants = models.ManyToManyField('self', symmetrical=False, related_name="ancestors", blank=True)
    collocates = models.ManyToManyField('self', blank=True)
    synonyms = models.ManyToManyField('self', blank=True)
    antonyms = models.ManyToManyField('self', blank=True)
    note = models.CharField('Usage Note', max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.definition

    def published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)



class Example(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="primary_artist_in_examples")
    song_id = models.CharField('Song ID', max_length=10)
    song_title = models.CharField('Song Title', max_length=200)
    feat_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="featured_artist_in_examples", null=True, blank=True)
    release_date = models.DateField('Release Date')
    album = models.CharField('Album', max_length=200)
    lyric_text = models.CharField('Lyric Text', max_length=1000)
    lyric_tokens = models.CharField('Lyric Tokens', max_length=1000)
    lyric_html = models.CharField('Lyric HTML', max_length=1000)

    def __str__(self):
        return self.lyric_text


class Domain(models.Model):
    name = models.CharField('Domain Name', max_length=1000, primary_key=True)

    def __str__(self):
        return self.name


class SynSet(models.Model):
    name = models.CharField('SynSet Name', max_length=1000, primary_key=True)
    definition = models.TextField('Definition')

    def __str__(self):
        return self.name

