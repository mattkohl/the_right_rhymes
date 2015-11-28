from django.db import models


class Editor(models.Model):
    name = models.CharField('Editor Name', max_length=1000)
    slug = models.SlugField('Editor Slug')


class Image(models.Model):
    title = models.CharField('Image Title', max_length=1000)
    slug = models.SlugField('Image Slug')
    image = models.ImageField()


class Artist(models.Model):
    name = models.CharField('Artist Name', max_length=1000)
    slug = models.SlugField('Artist Slug')
    origin = models.CharField('Origin', max_length=1000)
    image = models.ForeignKey(Image)


class Entry(models.Model):
    headword = models.CharField('Headword', max_length=1000)
    text = models.TextField('Entry Text')
    slug = models.SlugField('Entry Slug')
    pub_date = models.DateTimeField('Date Published')
    pub_by = models.ForeignKey(Editor)
    image = models.ForeignKey(Image)