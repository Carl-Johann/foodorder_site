# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User)    
    create_date = models.DateTimeField(verbose_name='create date', auto_now=True)    
    
    
    def __unicode__(self):
        return u'%s | %s' % (self.user, self.create_date)

class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Produkt Navn')    
    small_product_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Small price')
    large_product_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Large price ( if none, leave it '0' )", default=0.00)    
    nr = models.PositiveIntegerField(verbose_name='nr', default=1)
    is_active = models.BooleanField(verbose_name="Produktets aktiv status", default=True)
    
    def __unicode__(self):
        return u'%s | %s' % (self.nr, self.title)

class Item(models.Model):
    order = models.ForeignKey(Order, verbose_name='order', related_name='order', default=1)
    small_order_quantity = models.PositiveIntegerField(verbose_name='Small order quantity', default=0)
    large_order_quantity = models.PositiveIntegerField(verbose_name='Large order quantity', default=0)
    product = models.ForeignKey(Product, verbose_name='product', related_name='product')
    

    def __unicode__(self):
        return u'%d store, %d små af %s' % (self.large_order_quantity, self.small_order_quantity, self.product.title )