# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 03:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0013_auto_20160207_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playbyplay',
            name='penaltySeverity',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
