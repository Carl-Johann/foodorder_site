# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-10 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodorder', '0008_auto_20170910_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='large_product_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=18, verbose_name="Large price ( if none, leave it '0' )"),
        ),
    ]
