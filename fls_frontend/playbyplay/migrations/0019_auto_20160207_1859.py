# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0018_auto_20160207_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='awayFaceoffPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='homeFaceoffPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
