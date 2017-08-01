# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-07-31 13:38
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20170731_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='ssn',
            field=models.CharField(max_length=12, unique=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Personnumret måste vara tolv siffror utan bindesstreck (Ex. 197001010000)', regex='^[0-9]{12}$')], verbose_name='Personnummer'),
        ),
    ]
