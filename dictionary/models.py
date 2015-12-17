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

    def __str__(self):
        return self.headword + ', ' + self.part_of_speech + ' (' + self.xml_id + ')'


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

