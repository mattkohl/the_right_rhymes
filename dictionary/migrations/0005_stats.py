# Generated by Django 2.0.1 on 2018-04-13 06:47

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_salience'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('json', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
    ]
