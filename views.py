# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
# from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from .models import Product, Item, Order, MasterOrder
from datetime import datetime, timedelta
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.template.loader import render_to_string
from django.template import RequestContext
import requests

# Create your views here.

def login(request):
    return render(request, 'foodorder/user_login.html')

def product_list(request):
    # We get all active products, since we don't delete products, we set their 'is_active' bool field to false.
    products = Product.objects.filter(is_active=True).order_by('nr')
    date = datetime.now()

    if request.user.is_authenticated():
        # User is authenticated
        # print(123, can_order_or_edit(request))
        todays_master_order = check_for_master_order_and_create(request)
        if can_order_or_edit(request):
            return render(request, 'foodorder/product_list.html', { 'products':products, 'is_past_allowed_time': True, 'date': date })
        else:
            return render(request, 'foodorder/product_list.html', { 'products':products, 'is_past_allowed_time': False, 'date': date })
    else:
        # User is not authenticated, and we make them
        return render(request, 'foodorder/user_login.html')




# def check_if_past_allowed_time():
#     date = datetime.now()

#     # We check if the request is made within the allowed time. I.e that someone didnt hardcode the url, since we also check if it's past time in the view template
#     allowed_order_hour = datetime(2017, 1, 1, 14, 0, 0).strftime("%H")

#     if int(date.hour) > int(allowed_order_hour):
#         # Change to 'True' for prod, set to false for dev
#         return False
#     else:
#         return False



def can_order_or_edit(request):
    date = datetime.now()

    allowed_order_hour = int(datetime(2017, 1, 1, 10, 0, 0).strftime("%H"))
    todays_order = check_for_master_order_and_create(request)

    if date.hour >= allowed_order_hour:
        print "It's past the allowed hour"
        return True
    if date.isoweekday() >= 6:
        print "It's weekend"
        return True
    if todays_order.is_sent == True:
        print "Todays order is already sent"
        return True
    else:
        print "User can order food"
        return False


def check_for_master_order_and_create(request):
    date = datetime.now()
    if request.user.is_authenticated():
        todays_master_order = MasterOrder.objects.filter( create_date__year=date.year, create_date__month=date.month, create_date__day=date.day ).first()

        if not todays_master_order:
            # There is no MasterOrder created today
            print "Creating a MasterOrder"
            created_master_order = MasterOrder.objects.create()
            return created_master_order

        elif todays_master_order:
            # There is a MasterOrder created today, so we use that
            if todays_master_order.is_sent == False:
                # Todays MasterOrder *has not been* sent out be the admin
                print "Reusing a master_order already created today"
                return todays_master_order
            elif todays_master_order.is_sent == True:
                # Todays MasterOrder *has been* sent out by the admin
                print "Todays MasterOrder has already been sent out by the admin"
                return None
    else:
        # User is not authenticated
        return render(request, 'foodorder/user_login.html')



def create_items_and_order(request):
    date = datetime.now()
    if request.user.is_authenticated():
        # Double chekc if the user is allowed to order
        todays_master_order = check_for_master_order_and_create(request)

        if not todays_master_order:
            print "Todays MasterOrder has been sent"
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
                        print "Using an order already created"
                        create_items(products_id, order, request)
                    else:
                        # User haven't ordered anything today, so we create an Order
                        order = Order.objects.create(user=request.user, master_order=todays_master_order)
                        print "Will create order"
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
    if request.user.is_authenticated() and request.user.is_staff:
        return render(request, 'foodorder/admin_orders.html', context_for_admin_orders_view(request, date_year, date_day, date_month))
    else:
        return render(request, 'foodorder/user_login.html')


def send_order(request, date_year, date_day, date_month):
    if request.user.is_authenticated() and request.user.is_staff:

        bootstrap = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">'
        title = '<h4 style="padding-left: 1em;"> Andersen & Martini ' + date_year + ' ' + '-' + ' ' + date_month + ' ' + '-' + ' ' + date_day + '</h4>'

        html_content_as_string = render_to_string('foodorder/admin_orders.html', context_for_admin_orders_view(request, date_year, date_day, date_month), request)

        start_of_table_string = "Start of table"
        end_of_table_string = "End of table"
        start_of_html_to_send = int(html_content_as_string.find(start_of_table_string)) + len(start_of_table_string) + 4
        end_of_html_to_send = html_content_as_string.find(end_of_table_string)


        only_html_table = html_content_as_string[start_of_html_to_send:end_of_html_to_send]
        html_table_with_bootstrap = bootstrap, title, only_html_table


        send_simple_message(html_table_with_bootstrap)
        todays_master_order = check_for_master_order_and_create(request)
        todays_master_order.sender = request.user
        todays_master_order.is_sent = True
        todays_master_order.save()

        print "Did send orders out, and change is_sent value of todays_master_order"

        return redirect('admin_orders', date_year=date_year, date_month=date_month, date_day=date_day)
    else:
        return render(request, 'foodorder/user_login.html')



def send_simple_message(html_table):
    return requests.post(
        "https://api.mailgun.net/v3/m.blinklater.com/messages",

        auth=("api", "key-617028b8971710b5116515f9acb23138"),

        data={ "from": "Andersen & Martini <carljohan.beurling@gmail.com>",
               "to": ["carljohan.beurling@gmail.com"],
               "subject": "SUBJECT GOES HERE",
               "html": html_table,
              },
    )




def context_for_admin_orders_view(request, date_year, date_day, date_month):
    date = datetime.now()

    orders_for_this_date = Order.objects.all().filter( create_date__year=date.year, create_date__month=date_month, create_date__day=date_day )

    # Aggregates all the items in 'orders_for_this_date' to make i pretty for the user. The user can have multiple of the same order, and it will show them as one
    items = Item.objects.filter(order__in=orders_for_this_date).values('pk', 'product__title', 'product__is_active', 'product__nr', 'order__user__first_name', 'order__user__last_name', 'order__user__email', 'product__small_product_price', 'product__large_product_price').annotate(small_order_quantity=Sum('small_order_quantity'),large_order_quantity=Sum('large_order_quantity')).order_by('order__user__username')

    # Gets orders for this year to parse the datepicker
    past_orders = Order.objects.filter(create_date__year=date.year)

    # Makes strftime's out of the 'past_orders' for the datepicker.
    order_strfs = []
    for order in past_orders:
        string_order_date = order.create_date.strftime('%Y - %m - %d')
        order_strfs.append(string_order_date)

    # The current date as a string
    current_order_date_string = datetime(int(date_year), int(date_month), int(date_day), 0, 0)

    todays_master_order = check_for_master_order_and_create(request)
    if not todays_master_order:
        return { 'items': items, 'current_order_date': current_order_date_string, 'orders': order_strfs, 'date': date, 'is_todays_order_sent': True }
    else:
        return { 'items': items, 'current_order_date': current_order_date_string, 'orders': order_strfs, 'date': date, 'is_todays_order_sent': False }




def update_item_quantity(request):
    date = datetime.now()
    user = request.user
    if user.is_authenticated() and user.is_staff:
        if request.method == 'POST':
            product_pk = request.POST.get('item_pk')
            item = Item.objects.get(pk=product_pk)

            new_small_quantity = request.POST.get('new_small_quantity')
            new_large_quantity = request.POST.get('new_large_quantity')
            destination = request.POST.get('destination')

            # If the quantity is not empty and it's different from the the items current quantity, we update the item
            if new_small_quantity != "" and new_small_quantity and new_small_quantity != item.small_order_quantity:
                print "new_small_quantity is !="
                item.small_order_quantity = int(new_small_quantity)
            if new_large_quantity != "" and new_large_quantity and new_large_quantity != item.large_order_quantity:
                item.large_order_quantity = int(new_large_quantity)
                print "large_order_quantity is !="
            item.save()


            return redirect(destination, date_year=item.order.create_date.year, date_day=item.order.create_date.day, date_month=item.order.create_date.month)
        else:
            return render(request, 'foodorder/product_list.html')

    elif user.is_authenticated() and not user.is_staff:
        # The only place a 'non-staff' user SHOULD be able to update their items is in my_orders.html.

        if request.method == 'POST':
            product_pk = request.POST.get('item_pk')
            item = Item.objects.get(pk=product_pk)

            new_small_quantity = request.POST.get('new_small_quantity')
            new_large_quantity = request.POST.get('new_large_quantity')
            destination = request.POST.get('destination')

            if item.order.user.pk == user.pk and item.order.create_date.year == date.year and item.order.create_date.month == date.month and item.order.create_date.day == date.day:
                # The item is the users, and he/she is trying to modify an order created today, which is all they are allowed to do.

                # If the quantity is not empty and it's different from the the items current quantity, we update the item
                if new_small_quantity != "" and new_small_quantity and new_small_quantity != item.small_order_quantity:
                    print "new_small_quantity is !="
                    item.small_order_quantity = int(new_small_quantity)
                if new_large_quantity != "" and new_large_quantity and new_large_quantity != item.large_order_quantity:
                    item.large_order_quantity = int(new_large_quantity)
                    print "large_order_quantity is !="
                item.save()


            return redirect(destination, date_year=item.order.create_date.year, date_day=item.order.create_date.day, date_month=item.order.create_date.month)

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
        this_users_items = Item.objects.filter( order=requested_order)
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

        todays_master_order = check_for_master_order_and_create(request)
        if can_order_or_edit(request):
            return render(request, 'foodorder/my_orders.html', { 'items': items, 'this_users_items': this_users_items, 'order_sum': items_sum, 'current_order_date': current_order_date_string, 'orders': orders, 'is_past_allowed_time': True, 'date': date })
        else:
            return render(request, 'foodorder/my_orders.html', { 'items': items, 'this_users_items': this_users_items, 'order_sum': items_sum, 'current_order_date': current_order_date_string, 'orders': orders, 'is_past_allowed_time': False, 'date': date })

    else:
        return render(request, 'foodorder/user_login.html')

def get_danish_selected_month(selected_month):
    danish_month_names = {
        'january': 'januar',
        'february': 'febuar',
        'march': 'marts',
        'april': 'april',
        'may': 'maj',
        'june': 'juni',
        'july': 'juli',
        'august': 'august',
        'september': 'september',
        'october': 'oktober',
        'november': 'november',
        'december': 'december',
    }

    return danish_month_names[selected_month.lower()]


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
                                                                    'order__create_date',
                                                                    'product__small_product_price',
                                                                    'product__large_product_price',
                                                                    ).annotate( small_order_quantity=Sum('small_order_quantity'),
                                                                    large_order_quantity=Sum('large_order_quantity')).order_by('order__create_date')
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

        return render(request, 'foodorder/monthly_statement.html', { 'orders_this_month_list': orders_this_month_list, 'date': date, 'users_total_sums': users_total_sums, 'items': items, 'selected_month': get_danish_selected_month(selected_month), 'datepicker_date':datepicker_date })
    else:
        return render(request, 'foodorder/user_login.html')


