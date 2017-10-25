# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Item, Product, Order, MasterOrder
# Register your models here.

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(MasterOrder)