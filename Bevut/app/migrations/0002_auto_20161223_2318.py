# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 22:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Kursnummer')),
                ('year', models.CharField(max_length=32, verbose_name='År')),
                ('weeks', models.CharField(max_length=32, verbose_name='Antal veckor')),
            ],
        ),
        migrations.CreateModel(
            name='CourseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supervisor', models.CharField(max_length=256, verbose_name='Handledare/ansvarig')),
                ('location', models.CharField(max_length=256, verbose_name='Vårdavdelning')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Namn')),
                ('ssn', models.CharField(max_length=18, verbose_name='Personnummer')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Course')),
            ],
        ),
        migrations.AddField(
            model_name='coursegroup',
            name='students',
            field=models.ManyToManyField(to='app.Student'),
        ),
    ]
