# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0008_sense_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='sense',
            name='definition',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]