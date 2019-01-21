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
        migrations.AlterField(
            model_name='productattribute',
            name='option_group',
            field=models.ForeignKey(blank=True, help_text='Select an option group if using type "Option" or "Multi Option"', null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.AttributeOptionGroup', verbose_name='Option Group'),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='type',
            field=models.CharField(choices=[(b'text', 'Text'), (b'integer', 'Integer'), (b'boolean', 'True / False'), (b'float', 'Float'), (b'richtext', 'Rich Text'), (b'date', 'Date'), (b'datetime', b'Datetime'), (b'option', 'Option'), (b'multi_option', 'Multi Option'), (b'entity', 'Entity'), (b'file', 'File'), (b'image', 'Image')], default=b'text', max_length=20, verbose_name='Type'),
        ),
        migrations.AlterUniqueTogether(
            name='productimage',
            unique_together=set([]),
        ),
    ]
