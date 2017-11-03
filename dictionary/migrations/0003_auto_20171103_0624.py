# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-03 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_artist_member_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='member_of',
            field=models.ManyToManyField(blank=True, related_name='members', to='dictionary.Artist'),
        ),
    ]
