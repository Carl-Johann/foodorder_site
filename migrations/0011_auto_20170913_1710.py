# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-13 17:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodorder', '0010_product_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='check_out_date',
        ),
        migrations.RemoveField(
            model_name='order',
            name='checked_out',
        ),
    ]