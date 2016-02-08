# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0026_auto_20160207_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameperiod',
            name='startTime',
        ),
        migrations.RemoveField(
            model_name='gameperiod',
            name='endTime',
        ),
        migrations.AddField(
            model_name='gameperiod',
            name='startTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gameperiod',
            name='endTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
