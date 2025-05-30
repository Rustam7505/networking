from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Customer
from .forms import CustomerForm
from orders.models import Order


@login_required
def customer_list(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    customers = Customer.objects.all()

    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if status:
        customers = customers.filter(status=status)

    context = {
        'customers': customers,
        'status_choices': Customer.STATUS_CHOICES
    }

    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Get customer orders
    orders = Order.objects.filter(customer=customer).order_by('-created_at')

    # Get customer stats
    total_orders = orders.count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent
    }

    return render(request, 'customers/customer_detail.html', context)


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()

    # to‘g‘ri variant
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Create Customer'})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/customer_form.html',
                  {'form': form, 'customer': customer, 'title': 'Update Customer'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customers:customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})
