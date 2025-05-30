from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [

    path('', views.reports_index, name='index'),
    path('sales/', views.sales_report, name='sales'),
    path('inventory/', views.inventory_report, name='inventory'),   # yangi
    path('profit/', views.profit_report, name='profit'),           # yangi
    path('products/', views.product_report, name='products'),
    path('customers/', views.customer_report, name='customers'),
]


