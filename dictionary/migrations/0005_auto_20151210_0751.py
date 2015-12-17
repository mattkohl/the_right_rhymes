# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20151209_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='senses',
            field=models.ManyToManyField(related_name='has_form', to='dictionary.Sense', blank=True),
        ),
    ]
