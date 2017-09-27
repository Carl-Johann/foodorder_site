# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Product, Item, Order
from datetime import datetime, timedelta
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json

# Create your views here.

def login(request):
    return render(request, 'foodorder/user_login.html')


def product_list(request):
    # We get all active products, since we don't delete products, we set their 'is_active' bool field to false.
    # And reverse them to make them pretty for the user
    products = reversed(Product.objects.filter(is_active=True))    
    date = datetime.now()

    if request.user.is_authenticated():
        # User is authenticated
        return render(request, 'foodorder/product_list.html', { 'products':products, 'is_past_allowed_time': check_if_past_allowed_time(), 'date': date })
    else:
        # User is not authenticated, and we make them
        return render(request, 'foodorder/user_login.html')    
    



def check_if_past_allowed_time():
    date = datetime.now()    
    
    # We check if the request is made within the allowed time. I.e that someone didnt hardcode the url    
    allowed_order_hour = datetime(2017, 1, 1, 14, 0, 0).strftime("%H")    
    
    if int(date.hour) > int(allowed_order_hour):
        # Change to 'True' for prod, set to false for dev        
        return False
    else:        
        return False




def create_items_and_order(request):     
    date = datetime.now()
    if request.user.is_authenticated():
        # Double chekc if the user is allowed to order
        if check_if_past_allowed_time():
            print "past time"
            return redirect('product_list')

        # Gets todays orders, so we can check if we need to make the user one
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
                        create_items(products_id, order, request)
                    else:
                        # User haven't ordered anything today, so we create an Order
                        order = Order.objects.create(user=request.user)
                        print "Laver en ny ordrer for brugeren, fordi der ikke var en"
                        create_items(products_id, order, request)
                
                # Nothing happend, and we return HttpResponse-200
                response = HttpResponse()
                response.status_code = 200
                return response
        except Exception as e:
            # An error occured, and we return HttpResponse-400
            print "ERROR, couldn't create items and order", e
            response = HttpResponse()
            response.status_code = 400
            return response
    else:
        # User is not authenticated, and we make them
        return render(request, 'foodorder/user_login.html')




def create_items(products_id, order, request):
    for product_id in products_id:                       

        # The 'Product' instance with matching primary key, and a is_active status == true
        product = Product.objects.get(pk=product_id, is_active=True)                    
        
        item = Item.objects.create(order=order, product=product)
        
        small_quantity = request.POST.get( 'small_quantity_' + product_id )
        large_quantity = request.POST.get( 'large_quantity_' + product_id )

        # If a quantity is there, we update the item
        if small_quantity:
            item.small_order_quantity = small_quantity                    
        if large_quantity:
            item.large_order_quantity = large_quantity                        
        
        item.save()




def admin_orders(request, date_year, date_day, date_month):
    date = datetime.now()

    if request.user.is_authenticated() and request.user.is_staff:        
        orders_for_this_date = Order.objects.all().filter( create_date__year=date.year, create_date__month=date_month, create_date__day=date_day )
        
        # Aggregates all the items in 'orders_for_this_date' to make i pretty for the user. The user can have multiple of the same order, and it will show them as one
        items = Item.objects.filter(order__in=orders_for_this_date).values('pk', 'product__title', 'product__is_active', 'product__nr', 'order__user__username', 'order__user__first_name', 'order__user__last_name', 'order__user__email', 'product__small_product_price', 'product__large_product_price').annotate(small_order_quantity=Sum('small_order_quantity'),large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')
        
        # Gets orders for this year to parse the datepicker
        past_orders = Order.objects.filter(create_date__year=date.year)

        # Makes strftime's out of the 'past_orders' for the datepicker.
        order_strfs = []
        for order in past_orders:
            string_order_date = order.create_date.strftime('%Y - %m - %d')
            order_strfs.append(string_order_date)
        
        # The current date as a string      
        current_order_date_string = datetime(int(date_year), int(date_month), int(date_day), 0, 0).strftime('%Y - %m - %d')    
    
        return render(request, 'foodorder/admin_orders.html', { 'items': items, 'current_order_date': current_order_date_string, 'orders': order_strfs, 'date': date })        
    else:
        return render(request, 'foodorder/user_login.html')





def update_item_quantity(request):
    date = datetime.now()

    if request.user.is_authenticated() and request.user.is_staff:
        if request.method == 'POST':        
            
            product_pk = request.POST.get('product_pk')
            new_small_quantity = request.POST.get('new_small_quantity')
            new_large_quantity = request.POST.get('new_large_quantity')

            item = Item.objects.get(pk=product_pk)

            # If a quantity is there, we update the item
            if new_small_quantity != "":
                item.small_order_quantity = int(new_small_quantity)
            if new_large_quantity != "":
                item.large_order_quantity = int(new_large_quantity)
            item.save()
        
            return redirect('product_list')
        else:
            return render(request, 'foodorder/product_list.html')        
    else:
        return render(request, 'foodorder/user_login.html')




def my_orders(request, date_year, date_day, date_month):
    date = datetime.now()

    if request.user.is_authenticated():
        # Get the users requested order, and past orders from the dates parsed: 'date_year', 'date_day', 'date_month'
        requested_order = Order.objects.filter(user=request.user, create_date__year=date_year, create_date__month=date_month, create_date__day=date_day)     
        past_orders = Order.objects.filter(user=request.user)
        
        # Aggregates all the items in 'orders_for_this_date' to make it pretty for the user. The user can have multiple of the same order, and it will show them as one
        items = Item.objects.filter(order=requested_order).values('product__id', 'product__title', 'order__create_date','order__user__username' ,'order__user__email', 'product__nr', 'product__small_product_price', 'product__large_product_price').annotate(small_order_quantity=Sum('small_order_quantity'),large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')
        
        # Makes strftime's out of the 'past_orders' for the datepicker.
        orders = []
        for order in past_orders:
            string_order_date = order.create_date.strftime('%Y - %m - %d')
            orders.append(string_order_date)
                    
        
        # Calculates the total sum of all the items to be presented
        items_sum = 0
        for item in Item.objects.filter(order=requested_order):
            items_sum += (item.small_order_quantity * item.product.small_product_price)
            items_sum += (item.large_order_quantity * item.product.large_product_price)
        
        # The current date as a string                            
        current_order_date_string = datetime(int(date_year), int(date_month), int(date_day), 0, 0).strftime('%Y - %m - %d')    
        
        return render(request, 'foodorder/my_orders.html', { 'items': items, 'order_sum': items_sum, 'current_order_date': current_order_date_string, 'orders': orders, 'date': date })
    else:
        return render(request, 'foodorder/user_login.html')




def monthly_statement(request, date_year, date_month):
    date = datetime.now()
    
    if request.user.is_authenticated() and request.user.is_staff:
        selected_month = datetime(2013, int(date_month), 1).strftime('%B')

        orders_for_this_month = (Order.objects.filter(create_date__year=date_year, create_date__month=date_month))
        order_for_this_month_values = orders_for_this_month.values('user__pk', 'user__first_name', 'user__username', 'user__last_name', 'user__email').distinct()


        datepicker_date = date_year + "-" + date_month
        
        items = Item.objects.filter(order__in=orders_for_this_month).values(
                                                                    'product__title',
                                                                    'order__user__pk',
                                                                    'product__small_product_price',
                                                                    'product__large_product_price',
                                                                    ).annotate( small_order_quantity=Sum('small_order_quantity'),
                                                                    large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')            
        orders_this_month_list = list(order_for_this_month_values)    
        
        users_total_sums = {}
        # Calculates the total sum of all items the whole month
        for item in items:            
            total_quantity_sum = 0
            if item["small_order_quantity"] != 0:
                total_quantity_sum += item["product__small_product_price"] * item["small_order_quantity"]
            if item["large_order_quantity"] != 0:
                total_quantity_sum += item["product__large_product_price"] * item["large_order_quantity"]
            
            try:                
                this_users_items_total_sums = int(users_total_sums.get(item["order__user__pk"], 0))
                users_total_sums[item["order__user__pk"]] = this_users_items_total_sums + int(total_quantity_sum)            
            except Exception as e:
                print "couldn't get the small_order_quantity from 'users_total_sums'"


        for order in orders_this_month_list:
            order['total_sum_this_month'] = users_total_sums[order['user__pk']]        

        return render(request, 'foodorder/monthly_statement.html', { 'orders_this_month_list': orders_this_month_list, 'date': date, 'users_total_sums': users_total_sums, 'items': items, 'selected_month': selected_month, 'datepicker_date':datepicker_date })
    else:
        return render(request, 'foodorder/user_login.html')