# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-24 21:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audition_management', '0015_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='denied_applications', to='audition_management.Role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='denied_applications', to='audition_management.AuditionAccount')),
            ],
        ),
        migrations.CreateModel(
            name='RoleViewModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roleview', to='audition_management.AuditionAccount')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roleview', to='audition_management.Role')),
            ],
        ),
        migrations.AddField(
            model_name='castingaccount',
            name='location',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='location'),
        ),
        migrations.AddField(
            model_name='castingaccount',
            name='phone',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='phone'),
        ),
    ]
