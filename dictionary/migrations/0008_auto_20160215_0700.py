# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-15 07:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0007_auto_20160215_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='namedentity',
            name='pref_label_slug',
            field=models.SlugField(blank=True, max_length=1000, null=True, verbose_name='Entity PrefLabel Slug'),
        ),
    ]