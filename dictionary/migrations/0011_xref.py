# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0010_auto_20160105_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Xref',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('xref_word', models.CharField(blank=True, max_length=1000, null=True)),
                ('xref_type', models.CharField(blank=True, max_length=1000, null=True)),
                ('target_lemma', models.CharField(blank=True, max_length=1000, null=True)),
                ('target_slug', models.SlugField(blank=True, null=True)),
                ('target_id', models.CharField(blank=True, max_length=1000, null=True)),
                ('position', models.CharField(blank=True, max_length=1000, null=True)),
                ('frequency', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]