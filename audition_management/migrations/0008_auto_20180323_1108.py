# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-23 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audition_management', '0007_auto_20180322_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastwork',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Description of Past Works'),
        ),
    ]
