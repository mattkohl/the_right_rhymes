# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_auto_20151214_0712'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sense',
            old_name='lemma',
            new_name='headword',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='antonyms',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='collocates',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='definition',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='descendants',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='etymology',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='examples',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='note',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='pub_by',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='pub_date',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='relates_to',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='synonyms',
        ),
        migrations.RemoveField(
            model_name='sense',
            name='synset',
        ),
        migrations.AlterField(
            model_name='sense',
            name='xml_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Legacy XML id'),
        ),
    ]
