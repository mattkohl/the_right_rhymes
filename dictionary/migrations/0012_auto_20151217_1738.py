# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 17:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0011_auto_20151217_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='sense',
            name='json',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='json',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
