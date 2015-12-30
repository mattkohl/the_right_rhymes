# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='namedentity',
            name='slug',
            field=models.SlugField(blank=True, null=True, verbose_name='Entity Slug'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='slug',
            field=models.SlugField(verbose_name='Headword Slug'),
        ),
    ]
