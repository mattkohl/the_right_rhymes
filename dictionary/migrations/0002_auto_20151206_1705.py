# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, verbose_name='Domain Name', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('song_id', models.CharField(verbose_name='Song ID', max_length=10)),
                ('song_title', models.CharField(verbose_name='Song Title', max_length=200)),
                ('release_date', models.DateField(verbose_name='Release Date')),
                ('album', models.CharField(verbose_name='Album', max_length=200)),
                ('lyric_text', models.CharField(verbose_name='Lyric Text', max_length=1000)),
                ('lyric_tokens', models.CharField(verbose_name='Lyric Tokens', max_length=1000)),
                ('lyric_html', models.CharField(verbose_name='Lyric HTML', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Sense',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('pub_date', models.DateTimeField(verbose_name='Date Published')),
                ('part_of_speech', models.CharField(verbose_name='Part of Speech', max_length=20)),
                ('definition', models.TextField(verbose_name='Definition')),
                ('etymology', models.TextField(verbose_name='Etymology')),
                ('note', models.CharField(verbose_name='Usage Note', max_length='1000')),
                ('antonyms', models.ManyToManyField(related_name='_sense_antonyms_+', to='dictionary.Sense')),
                ('collocates', models.ManyToManyField(related_name='_sense_collocates_+', to='dictionary.Sense')),
                ('descendants', models.ManyToManyField(related_name='ancestors', to='dictionary.Sense')),
                ('domain', models.ManyToManyField(related_name='senses', to='dictionary.Domain')),
                ('examples', models.ManyToManyField(related_name='illustrates', to='dictionary.Example')),
            ],
        ),
        migrations.CreateModel(
            name='SynSet',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, verbose_name='SynSet Name', max_length=1000)),
                ('definition', models.TextField(verbose_name='Definition')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('form', models.CharField(verbose_name='form', max_length=1000)),
            ],
        ),
        migrations.RemoveField(
            model_name='entry',
            name='image',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='pub_by',
        ),
        migrations.AlterField(
            model_name='artist',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='artist',
            name='image',
            field=models.ForeignKey(to='dictionary.Image', related_name='depicts'),
        ),
        migrations.AlterField(
            model_name='editor',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
        migrations.AddField(
            model_name='word',
            name='image',
            field=models.ForeignKey(to='dictionary.Image', related_name='image_for_entries'),
        ),
        migrations.AddField(
            model_name='word',
            name='rhymes_with',
            field=models.ManyToManyField(related_name='_word_rhymes_with_+', to='dictionary.Word'),
        ),
        migrations.AddField(
            model_name='word',
            name='senses',
            field=models.ManyToManyField(to='dictionary.Sense'),
        ),
        migrations.AddField(
            model_name='sense',
            name='pub_by',
            field=models.ForeignKey(to='dictionary.Editor', related_name='edited'),
        ),
        migrations.AddField(
            model_name='sense',
            name='relates_to',
            field=models.ManyToManyField(related_name='related_to', to='dictionary.Sense'),
        ),
        migrations.AddField(
            model_name='sense',
            name='synonyms',
            field=models.ManyToManyField(related_name='_sense_synonyms_+', to='dictionary.Sense'),
        ),
        migrations.AddField(
            model_name='sense',
            name='synset',
            field=models.ForeignKey(to='dictionary.SynSet', related_name='senses'),
        ),
        migrations.AddField(
            model_name='example',
            name='artist',
            field=models.ForeignKey(to='dictionary.Artist', related_name='in_examples'),
        ),
    ]
