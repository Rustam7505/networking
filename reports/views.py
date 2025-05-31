from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Max
from orders.models import Order
from customers.models import Customer
from products.models import Product
from inventory.models import Inventory
import json
from datetime import datetime, timedelta
from django.utils import timezone


@login_required
def reports_index(request):
    """Reports dashboard"""
    # Quick stats for dashboard
    context = {
        'total_orders': Order.objects.count(),
        'total_revenue': Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_customers': Customer.objects.count(),
        'total_products': Product.objects.count(),
    }
    return render(request, 'reports/index.html', context)


@login_required
def sales_report(request):
    """Sales report with chart data"""
    # Get sales data
    sales = Order.objects.select_related('customer').order_by('-created_at')[:50]

    # Simple approach for chart data
    chart_labels = []
    chart_totals = []

    # Get last 7 days data (simpler approach)
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)

        # Get orders for this date
        daily_total = Order.objects.filter(
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Format date as string
        chart_labels.append(date.strftime('%m/%d'))
        chart_totals.append(float(daily_total))

    # Reverse to show oldest to newest
    chart_labels.reverse()
    chart_totals.reverse()

    context = {
        'sales': sales,
        'chart_labels': json.dumps(chart_labels),
        'chart_totals': json.dumps(chart_totals),
    }
    return render(request, 'reports/sales_report.html', context)


@login_required
def inventory_report(request):
    """Inventory movement report"""
    # Get inventory data with correct field name
    opening = Inventory.objects.select_related('product').all()

    # Create simple inventory data
    inventory_data = []
    total_received = 0

    for item in opening:
        quantity = item.quantity_received or 0
        total_received += quantity

        inventory_data.append({
            'product_name': item.product.name if item.product else 'Unknown Product',
            'quantity_received': quantity,
            'date_received': item.date_received,
            'supplier_name': item.supplier.name if item.supplier else 'No Supplier',
            'invoice_number': item.invoice_number or 'N/A',
        })

    context = {
        'inventory_data': inventory_data,
        'opening': opening,
        'movement': {},  # Empty for now
        'report_date': timezone.now().strftime('%B %d, %Y'),
        'total_opening': total_received,
        'total_added': 0,
        'total_removed': 0,
        'total_closing': total_received,
        'total_received': total_received,
    }
    return render(request, 'reports/inventory_report.html', context)


@login_required
def customer_report(request):
    """Customer analytics report"""
    customers = Customer.objects.annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total_amount'),
        last_order=Max('order__created_at')
    ).order_by('-total_spent')

    context = {
        'customers': customers,
    }
    return render(request, 'reports/customer_report.html', context)


@login_required
def product_report(request):
    """Product performance report"""
    # Simple approach without complex annotations
    products = Product.objects.all()

    # Add calculated fields manually
    product_data = []
    for product in products:
        # You'll need to adjust these based on your actual models
        try:
            units_sold = 0  # Calculate based on your OrderItem model
            revenue = 0  # Calculate based on your OrderItem model
            stock = getattr(product, 'stock', 0)  # Adjust based on your model

            product_data.append({
                'name': product.name,
                'units_sold': units_sold,
                'revenue': revenue,
                'stock': stock,
            })
        except:
            continue

    context = {
        'products': product_data,
    }
    return render(request, 'reports/product_report.html', context)


@login_required
def profit_report(request):
    """Profit and loss report"""
    profits = []

    # Calculate daily profits for last 7 days (simpler)
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)

        # Get revenue for this date
        revenue = Order.objects.filter(
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Mock cost calculation (70% of revenue)
        cost = float(revenue) * 0.7
        profit = float(revenue) - cost

        profits.append({
            'date': date,
            'revenue': float(revenue),
            'cost': cost,
            'profit': profit,
        })

    # Reverse to show oldest to newest
    profits.reverse()

    context = {
        'profits': profits,
        'total_revenue': sum(p['revenue'] for p in profits),
        'total_cost': sum(p['cost'] for p in profits),
        'total_profit': sum(p['profit'] for p in profits),
    }
    return render(request, 'reports/profit_report.html', context)