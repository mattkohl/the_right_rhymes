# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-22 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0023_auto_20151222_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='pref_label',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
