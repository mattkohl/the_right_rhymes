# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 15:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_sense_definition'),
    ]

    operations = [
        migrations.AddField(
            model_name='sense',
            name='etymology',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='sense',
            name='notes',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]