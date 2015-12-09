# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20151209_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sense',
            name='antonyms',
            field=models.ManyToManyField(to='dictionary.Sense', related_name='_sense_antonyms_+', blank=True),
        ),
        migrations.AlterField(
            model_name='sense',
            name='collocates',
            field=models.ManyToManyField(to='dictionary.Sense', related_name='_sense_collocates_+', blank=True),
        ),
        migrations.AlterField(
            model_name='sense',
            name='descendants',
            field=models.ManyToManyField(to='dictionary.Sense', related_name='ancestors', blank=True),
        ),
        migrations.AlterField(
            model_name='sense',
            name='domain',
            field=models.ManyToManyField(to='dictionary.Domain', related_name='senses', blank=True),
        ),
        migrations.AlterField(
            model_name='sense',
            name='relates_to',
            field=models.ManyToManyField(to='dictionary.Sense', related_name='related_to', blank=True),
        ),
        migrations.AlterField(
            model_name='sense',
            name='synonyms',
            field=models.ManyToManyField(to='dictionary.Sense', related_name='_sense_synonyms_+', blank=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rhymes_with',
            field=models.ManyToManyField(to='dictionary.Word', related_name='_word_rhymes_with_+', blank=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='senses',
            field=models.ManyToManyField(to='dictionary.Sense', blank=True),
        ),
    ]
