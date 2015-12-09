# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_auto_20151206_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='feat_artist',
            field=models.ForeignKey(related_name='featured_artist_in_examples', to='dictionary.Artist', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='artist',
            name='image',
            field=models.ForeignKey(related_name='depicts', to='dictionary.Image', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='artist',
            name='origin',
            field=models.CharField(null=True, max_length=1000, blank=True, verbose_name='Origin'),
        ),
        migrations.AlterField(
            model_name='example',
            name='artist',
            field=models.ForeignKey(to='dictionary.Artist', related_name='primary_artist_in_examples'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='antonyms',
            field=models.ManyToManyField(null=True, blank=True, related_name='_sense_antonyms_+', to='dictionary.Sense'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='collocates',
            field=models.ManyToManyField(null=True, blank=True, related_name='_sense_collocates_+', to='dictionary.Sense'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='descendants',
            field=models.ManyToManyField(null=True, blank=True, related_name='ancestors', to='dictionary.Sense'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='domain',
            field=models.ManyToManyField(null=True, blank=True, related_name='senses', to='dictionary.Domain'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='etymology',
            field=models.TextField(null=True, blank=True, verbose_name='Etymology'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='note',
            field=models.CharField(null=True, max_length='1000', blank=True, verbose_name='Usage Note'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='relates_to',
            field=models.ManyToManyField(null=True, blank=True, related_name='related_to', to='dictionary.Sense'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='synonyms',
            field=models.ManyToManyField(null=True, blank=True, related_name='_sense_synonyms_+', to='dictionary.Sense'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='synset',
            field=models.ForeignKey(related_name='senses', to='dictionary.SynSet', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='image',
            field=models.ForeignKey(related_name='image_for_entries', to='dictionary.Image', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rhymes_with',
            field=models.ManyToManyField(null=True, blank=True, related_name='_word_rhymes_with_+', to='dictionary.Word'),
        ),
        migrations.AlterField(
            model_name='word',
            name='senses',
            field=models.ManyToManyField(null=True, blank=True, to='dictionary.Sense'),
        ),
    ]
