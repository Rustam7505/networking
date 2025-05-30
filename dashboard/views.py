from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from customers.models import Customer
from orders.models import Order, OrderItem
from inventory.models import Inventory


@login_required
def dashboard(request):
    # Date ranges
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())

    # Total sales
    total_sales = Order.objects.filter(
        status__in=['delivered', 'shipped']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Monthly sales
    monthly_sales = Order.objects.filter(
        created_at__date__gte=start_of_month,
        status__in=['delivered', 'shipped', 'processing']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Weekly sales
    weekly_sales = Order.objects.filter(
        created_at__date__gte=start_of_week,
        status__in=['delivered', 'shipped', 'processing']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Today's sales
    today_sales = Order.objects.filter(
        created_at__date=today
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Top selling products
    top_products = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:5]

    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    # Recent customers
    recent_customers = Customer.objects.all().order_by('-created_at')[:5]

    # Low stock products
    low_stock_products = Product.objects.filter(stock_quantity__lt=10).count()

    # Sales by category
    sales_by_category = OrderItem.objects.values(
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_revenue')

    # Monthly sales data for chart
    months = []
    monthly_data = []

    for i in range(6, 0, -1):
        month = today.month - i
        year = today.year

        if month <= 0:
            month += 12
            year -= 1

        month_start = timezone.datetime(year, month, 1).date()
        if month == 12:
            month_end = timezone.datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = timezone.datetime(year, month + 1, 1).date() - timedelta(days=1)

        month_sales = Order.objects.filter(
            created_at__date__range=[month_start, month_end],
            status__in=['delivered', 'shipped']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        months.append(month_start.strftime('%b'))
        monthly_data.append(float(month_sales))

    context = {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'weekly_sales': weekly_sales,
        'today_sales': today_sales,
        'total_orders': Order.objects.count(),
        'recent_orders': recent_orders,
        'recent_customers': recent_customers,
        'total_customers': Customer.objects.count(),
        'active_orders': Order.objects.exclude(status__in=['delivered', 'cancelled']).count(),
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'total_products': Product.objects.count(),
        'sales_by_category': sales_by_category,
        'months': months,
        'monthly_data': monthly_data,
    }

    return render(request, 'dashboard/index.html', context)
