# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-12 02:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0034_auto_20160211_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='dateTime',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
