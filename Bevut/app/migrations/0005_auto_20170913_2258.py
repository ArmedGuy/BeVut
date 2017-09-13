# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-13 22:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20170804_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalcourse',
            name='description',
            field=models.TextField(default='', verbose_name='Beskrivning av kursen, generella mål'),
        ),
        migrations.AddField(
            model_name='historicalstudentform',
            name='midterm_action_plan',
            field=models.CharField(choices=[('no', 'Behövs ej'), ('yes', 'Åtgärdsplan behöver upprättas'), ('started', 'Åtgärdsplan har upprättats')], default='no', max_length=6, verbose_name='Status för åtgärdsplan vid halvtidsbedömning'),
        ),
        migrations.AlterField(
            model_name='historicalstudentform',
            name='fullterm_ok_absence',
            field=models.CharField(blank=True, max_length=10, verbose_name='Godkänd frånvaro vid heltidsbedömning'),
        ),
    ]
