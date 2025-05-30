from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product, Category
from customers.models import Customer
from inventory.models import InventoryHistory      # <-- aynan shu nom bo‘lishi kerak
from datetime import date
from django.db.models.functions import TruncDate   # sanani kun bo‘yicha kesish
from django.db.models import Sum
import json   # list → "[...]" ko‘rinishiga o‘girish uchun

from django.db.models import Sum, Q
from inventory.models import InventoryHistory
from django.db.models.functions import TruncDate
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
@login_required
def reports_index(request):
    return render(request, 'reports/index.html')


@login_required
def sales_report(request):
    # 1) Kunlik yig‘indi tayyorlaymiz
    qs = (Order.objects
          .annotate(d=TruncDate('created_at'))     # d = YYYY-MM-DD
          .values('d')
          .annotate(total=Sum('total_amount'))
          .order_by('d'))

    # 2) Grafik uchun listlar
    labels = [row['d'].strftime('%Y-%m-%d') for row in qs]
    totals = [float(row['total']) for row in qs]

    # 3) Jadval uchun barcha buyurtmalar (xohlasangiz filtrlang)
    table_qs = (Order.objects
                .select_related('customer')
                .order_by('-created_at'))

    context = {
        'sales': table_qs,
        'chart_labels': json.dumps(labels),   # "['2025-05-01', …]"
        'chart_totals': json.dumps(totals),   # "[1200.0, 900.5, …]"
    }
    return render(request, 'reports/sales_report.html', context)



@login_required
def product_report(request):
    # Date ranges
    today = timezone.now().date()
    date_range = request.GET.get('date_range', 'month')

    # Set date range
    if date_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        title = f"Weekly Product Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    elif date_range == 'month':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        title = f"Monthly Product Report ({start_date.strftime('%B %Y')})"
    elif date_range == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
        title = f"Yearly Product Report ({start_date.strftime('%Y')})"
    elif date_range == 'custom':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            title = f"Custom Product Report ({start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')})"
        else:
            # Default to last 30 days if custom dates not provided
            start_date = today - timedelta(days=30)
            end_date = today
            title = f"Last 30 Days Product Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
        title = f"Last 30 Days Product Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"

    # Get order items in date range
    order_items = OrderItem.objects.filter(
        order__created_at__date__range=[start_date, end_date]
    )

    # Top selling products
    top_products = order_items.values(
        'product__id', 'product__name', 'product__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_quantity')[:10]

    # Sales by category
    sales_by_category = order_items.values(
        'product__category__id', 'product__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_revenue')

    # Low stock products
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)

    context = {
        'title': title,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'low_stock_products': low_stock_products
    }

    return render(request, 'reports/product_report.html', context)


@login_required
def customer_report(request):
    # Date ranges
    today = timezone.now().date()
    date_range = request.GET.get('date_range', 'month')

    # Set date range
    if date_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        title = f"Weekly Customer Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    elif date_range == 'month':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        title = f"Monthly Customer Report ({start_date.strftime('%B %Y')})"
    elif date_range == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
        title = f"Yearly Customer Report ({start_date.strftime('%Y')})"
    elif date_range == 'custom':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            title = f"Custom Customer Report ({start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')})"
        else:
            # Default to last 30 days if custom dates not provided
            start_date = today - timedelta(days=30)
            end_date = today
            title = f"Last 30 Days Customer Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
        title = f"Last 30 Days Customer Report ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"

    # Get orders in date range
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

    # Top customers
    top_customers = orders.values(
        'customer__id', 'customer__name', 'customer__email'
    ).annotate(
        order_count=Count('id'),
        total_spent=Sum('total_amount')
    ).order_by('-total_spent')[:10]

    # New customers
    new_customers = Customer.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    # Customer status distribution
    customer_status = Customer.objects.values('status').annotate(
        count=Count('id')
    )

    context = {
        'title': title,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'top_customers': top_customers,
        'new_customers': new_customers,
        'customer_status': customer_status
    }

    return render(request, 'reports/customer_report.html', context)
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# <<— o'z modellingizni import qiling —>>
       # change if name differs
            # for profit calculation


@login_required
def inventory_report(request):
    today = date.today()          # kerak bo‘lsa request.GET bilan sanani oling
    qs = InventoryHistory.objects.select_related('product')

    # 1. Ochilish balansi (hozirgi sanadan oldingi jamlama)
    opening = (qs
        .filter(timestamp__lt=today)
        .values('product_id', 'product__name')
        .annotate(
            opening_qty=Sum('change')      # bu yerda filtr yuqori qatorda
        )
    )

    # 2. Bugungi harakatlar    (+ kirim  |  – chiqim)
    movement = (qs
        .filter(timestamp__date=today)
        .values('product_id', 'product__name')
        .annotate(
            added   =Sum('change', filter=Q(change__gt=0)),
            removed =Sum('change', filter=Q(change__lt=0)),
        )
    )

    # 3. Natijani birlashtirish yoki template’ga uzatish
    context = {
        'opening':  opening,
        'movement': movement,
        'report_date': today,
    }
    return render(request, 'reports/inventory_report.html', context)





@login_required
def profit_report(request):
        # har kunlik savdo va tannarx farqini chiqarish misoli
        qs = (OrderItem.objects
              .annotate(order_date=TruncDate('order__created_at'))  # <-- shu yer
              .values('order_date')
              .annotate(
            revenue=Sum(F('price') * F('quantity')),
            cost=Sum(F('product__cost_price') * F('quantity')),
        )
              .annotate(profit=F('revenue') - F('cost'))
              .order_by('order_date'))

        context = {'rows': qs}
        return render(request, 'reports/profit_report.html', context)