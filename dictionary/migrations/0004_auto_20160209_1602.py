# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20160120_0642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sense',
            name='part_of_speech',
            field=models.CharField(max_length=100, verbose_name='Part of Speech'),
        ),
        migrations.AlterField(
            model_name='sense',
            name='xml_id',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True, verbose_name='XML id'),
        ),
    ]