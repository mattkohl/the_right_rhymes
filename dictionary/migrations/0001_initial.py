# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=1000, verbose_name='Artist Name')),
                ('slug', models.SlugField(verbose_name='Artist Slug')),
                ('origin', models.CharField(max_length=1000, verbose_name='Origin')),
            ],
        ),
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=1000, verbose_name='Editor Name')),
                ('slug', models.SlugField(verbose_name='Editor Slug')),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('headword', models.CharField(max_length=1000, verbose_name='Headword')),
                ('text', models.TextField(verbose_name='Entry Text')),
                ('slug', models.SlugField(verbose_name='Entry Slug')),
                ('pub_date', models.DateTimeField(verbose_name='Date Published')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(verbose_name='Image Title', max_length=1000)),
                ('slug', models.SlugField(verbose_name='Image Slug')),
                ('image', models.ImageField(upload_to='')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='image',
            field=models.ForeignKey(to='dictionary.Image'),
        ),
        migrations.AddField(
            model_name='entry',
            name='pub_by',
            field=models.ForeignKey(to='dictionary.Editor'),
        ),
        migrations.AddField(
            model_name='artist',
            name='image',
            field=models.ForeignKey(to='dictionary.Image'),
        ),
    ]
