from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('sales/', views.sales_report, name='sales'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('customer/', views.customer_report, name='customer'),
    path('product/', views.product_report, name='product'),
    path('profit/', views.profit_report, name='profit'),
]