# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-25 09:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20171024_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tagName',
            field=models.CharField(default='General', max_length=50),
        ),
    ]
