# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 07:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='source',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
