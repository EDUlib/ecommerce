# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-24 11:31
from __future__ import absolute_import, unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0029_auto_20180119_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattributevalue',
            name='value_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='DateTime'),
        ),
        migrations.AddField(
            model_name='productattributevalue',
            name='value_multi_option',
            field=models.ManyToManyField(blank=True, related_name='multi_valued_attribute_values', to='catalogue.AttributeOption', verbose_name='Value multi option'),
        ),
    ]
