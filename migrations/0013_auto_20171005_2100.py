# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-05 21:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodorder', '0012_auto_20171005_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterorder',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='master_order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='foodorder.MasterOrder'),
        ),
    ]
