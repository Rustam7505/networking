# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'created_at', 'customer', 'status', 'total_amount')
    list_filter   = ('status', 'created_at')
    search_fields = ('customer__name',)
    inlines       = [OrderItemInline]
