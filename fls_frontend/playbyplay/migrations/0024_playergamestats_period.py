# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0023_auto_20160207_2004'),
    ]

    operations = [
        migrations.AddField(
            model_name='playergamestats',
            name='period',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
