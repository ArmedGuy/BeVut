# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-01 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20170731_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentform',
            name='link_uuid',
            field=models.UUIDField(default=uuid.uuid4, verbose_name='Read only länk id'),
        ),
    ]