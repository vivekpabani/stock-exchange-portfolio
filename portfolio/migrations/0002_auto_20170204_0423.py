# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 04:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolioentry',
            old_name='user_name',
            new_name='username',
        ),
    ]
