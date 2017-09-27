from django.conf.urls import url, include
from . import views

# from django.contrib.auth.views import logout, login
# from django.contrib.auth.urls import views as auth_views
from django.conf.urls.static import static

from django.conf import settings

from django.core.urlresolvers import reverse_lazy

from django.contrib.auth.urls import urlpatterns
from django.conf.urls.static import static

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.product_list, name="product_list"),
    url(r'^create_items_and_order/$', views.create_items_and_order, name='create_items_and_order'),
    url(r'^update_item_quantity/$', views.update_item_quantity, name='update_item_quantity'),
    url(r'^login/$', views.login, name='login'),
    url(r'^log_user_in/$', auth_views.login, name='log_user_in'),
    url(r'^log_user_out/$', auth_views.logout, name='log_user_out'),
    url(r'^admin_orders/(?P<date_year>[0-9]+)-(?P<date_month>[0-9]+)-(?P<date_day>[0-9]+)/$', views.admin_orders, name='admin_orders'),
    url(r'^my_orders/(?P<date_year>[0-9]+)-(?P<date_month>[0-9]+)-(?P<date_day>[0-9]+)/$', views.my_orders, name='my_orders'),
    url(r'^monthly_statement/(?P<date_year>[0-9]+)-(?P<date_month>[0-9]+)/$', views.monthly_statement, name='monthly_statement'),
]