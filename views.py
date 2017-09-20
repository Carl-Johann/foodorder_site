# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Product, Item, Order
from datetime import datetime, timedelta
from django.db.models import Sum
import json
# Create your views here.

def login(request):

    return render(request, 'foodorder/login.html')

def product_list(request):
    products = reversed(Product.objects.filter(is_active=True))    
    date = datetime.now()

    if request.user.is_authenticated():
        return render(request, 'foodorder/product_list.html', {'products':products, 'is_past_allowed_time': check_if_past_allowed_time(), 'date': date})
    else:
        return render(request, 'foodorder/login.html')    
    


    
def check_if_past_allowed_time():
    date = datetime.now()
    
    # href="{% url 'post_detail' pk=post.pk %}"
    
    # We check if the request is made within the allowed time. I.e that someone didnt hardcode the url    
    allowed_order_hour = datetime(2017, 1, 1, 14, 0, 0).strftime("%H")    
    
    if int(date.hour) > int(allowed_order_hour):
        # ændrer til True for at virke. Sat til False for dev
        return False
    else:        
        return False




def create_items_and_order(request): 
    
    # date = datetime.now().strftime('%Y-%m-%d')
    date = datetime.now()
    # this_year = datetime.now().strftime('%Y')
    # this_month = datetime.now().strftime('%m')
    # todays_day = datetime.now().strftime('%d')
    

    if check_if_past_allowed_time():
        print "past time"
        return redirect('product_list')

    todays_orders = Order.objects.filter(user=request.user, create_date__year=date.year, create_date__month=date.month, create_date__day=date.day) 

    try:
        if request.method == "POST":
            products_id = request.POST.getlist('id')
            if len(products_id) != 0:                          

                max_daily_orders = 1
                                
                if len(todays_orders) >= max_daily_orders:
                    # User has already created an Order today, so we reuse that one
                    order = todays_orders[0]
                    print "Bruger en ordrer der allerde var lavet til denne bruger"
                    create_or_update_items_and_orders(products_id, order, request)
                else:
                    # User haven't ordered anything today, so we create an Order
                    order = Order.objects.create(user=request.user)
                    print "Laver en ny ordrer for brugeren, fordi der ikke var en"
                    create_or_update_items_and_orders(products_id, order, request)

                # print "123123123", order

                # for product_id in products_id:       

                    

                #     # The 'Product' instance with matching primary key, and a is_active status == true
                #     product = Product.objects.get(pk=product_id, is_active=True)                    
                  
                #     item = Item.objects.create(order=order, product=product)
                    
                #     small_quantity = request.POST.get( 'small_quantity_' + product_id )
                #     large_quantity = request.POST.get( 'large_quantity_' + product_id )
        
                #     if small_quantity:
                #         item.small_order_quantity = small_quantity                    
                #     if large_quantity:
                #         item.large_order_quantity = large_quantity                        
                    
                #     item.save()
                    
            
            response = HttpResponse()
            response.status_code = 200
            return response
    except Exception as e:
        print "ERROR, couldn't create items and order", e
        response = HttpResponse()
        response.status_code = 400
        return response

def create_or_update_items_and_orders(products_id, order, request):

    for product_id in products_id:                       

        # The 'Product' instance with matching primary key, and a is_active status == true
        product = Product.objects.get(pk=product_id, is_active=True)                    
        
        item = Item.objects.create(order=order, product=product)
        
        small_quantity = request.POST.get( 'small_quantity_' + product_id )
        large_quantity = request.POST.get( 'large_quantity_' + product_id )

        if small_quantity:
            item.small_order_quantity = small_quantity                    
        if large_quantity:
            item.large_order_quantity = large_quantity                        
        
        item.save()

    # orders_items = Item.objects.all().filter(order=order)
    
    # for product_id in products_id:        
        
    #     small_quantity = request.POST.get( 'small_quantity_' + product_id )
    #     large_quantity = request.POST.get( 'large_quantity_' + product_id )

    #     if len(orders_items) != 0:
    #         for item in orders_items:                

    #             if item.product.id == int(product_id):                    

    #                 if small_quantity:
    #                     item.small_order_quantity += int(small_quantity)
    #                 if large_quantity:
    #                     item.large_order_quantity += large_quantity  
                    
    #                 item.save()
    #     else:
    #         print "produktet er der ikke"
    #         product = Product.objects.get(pk=product_id, is_active=True)                  
    #         item = Item.objects.create(order=order, product=product)            

    #         if small_quantity:
    #             item.small_order_quantity += int(small_quantity)
    #         if large_quantity:
    #             item.large_order_quantity += large_quantity 
    #         item.save()


def admin_orders(request, date_year, date_day, date_month):
    date = datetime.now()

    orders_for_this_date = Order.objects.all().filter( create_date__year=date.year, create_date__month=date_month, create_date__day=date_day )
    #  
    print orders_for_this_date
    items = Item.objects.filter(order__in=orders_for_this_date).values('product__id', 'product__title', 'product__is_active', 'product__nr', 'order__user__username', 'order__user__first_name', 'order__user__last_name', 'order__user__email', 'product__small_product_price', 'product__large_product_price').annotate(small_order_quantity=Sum('small_order_quantity'),large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')    
    
    past_orders = Order.objects.filter(create_date__year=date.year)

    orders = []
    for order in past_orders:
        string_order_date = order.create_date.strftime('%Y - %d - %m')
        orders.append(string_order_date)

    
    current_order_date_string = datetime(int(date_year), int(date_month), int(date_day), 0, 0).strftime('%Y - %d - %m')    
    
    print "items length:", len(items)
    return render(request, 'foodorder/admin_orders.html', { 'items': items, 'current_order_date': current_order_date_string, 'orders': orders, 'date': date })






def my_orders(request, date_year, date_day, date_month):
    date = datetime.now()    
                                           
    current_order_date_string = datetime(int(date_year), int(date_month), int(date_day), 0, 0).strftime('%Y - %d - %m')    

    requested_order = Order.objects.filter(user=request.user, create_date__year=date_year, create_date__month=date_month, create_date__day=date_day)     
    past_orders = Order.objects.filter(user=request.user)    

    items = Item.objects.filter(order=requested_order).values('product__id', 'product__title', 'order__create_date','order__user__username' ,'order__user__email', 'product__nr', 'product__small_product_price', 'product__large_product_price').annotate(small_order_quantity=Sum('small_order_quantity'),large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')
    
    orders = []
    for order in past_orders:
        string_order_date = order.create_date.strftime('%Y - %d - %m')
        orders.append(string_order_date)
        
    print "items length:", len(items)
    items_sum = 0
    for item in Item.objects.filter(order=requested_order):
        items_sum += (item.small_order_quantity * item.product.small_product_price)
        items_sum += (item.large_order_quantity * item.product.large_product_price)
    
    return render(request, 'foodorder/my_orders.html', { 'items': items, 'order_sum': items_sum, 'current_order_date': current_order_date_string, 'orders': orders, 'date': date })