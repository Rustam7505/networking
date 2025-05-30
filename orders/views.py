# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Order
from .forms  import OrderForm, OrderItemFormSet

# -------- LIST --------
@login_required
def order_list(request):
    search  = request.GET.get('search', '')
    status  = request.GET.get('status', '')

    orders = Order.objects.select_related('customer')

    if search:
        orders = orders.filter(
            Q(customer__name__icontains=search) |
            Q(order_number__icontains=search)
        )
    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders.order_by('-created_at'),
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'orders/order_list.html', context)

# -------- DETAIL --------
@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related('items__product'),
        pk=pk
    )
    return render(request, 'orders/order_detail.html', {'order': order})

# -------- CREATE --------
@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            formset.instance = order
            formset.save()
            messages.success(request, 'Order created.')
            return redirect('orders:detail', order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    return render(request, 'orders/order_form.html',
                  {'form': form, 'formset': formset, 'is_create': True})

# -------- UPDATE --------
@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Order updated.')
            return redirect('orders:detail', order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    return render(request, 'orders/order_form.html',
                  {'form': form, 'formset': formset, 'is_create': False})

# -------- DELETE --------
@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted.')
        return redirect('orders:list')
    return render(request, 'orders/order_confirm_delete.html', {'order': order})

# -------- STATUS CHANGE --------
@login_required

def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        # ❶ instance=order shart!
        form     = OrderForm(request.POST, instance=order)
        formset  = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Buyurtma yangilandi.')
            return redirect('orders:detail', order.pk)
        # Agar xato bo‘lsa, konsolda ko‘rish uchun
        print("FORM ERRORS:", form.errors)
        print("FORMSET ERRORS:", formset.errors, formset.non_form_errors())
    else:
        form     = OrderForm(instance=order)
        formset  = OrderItemFormSet(instance=order)

    return render(request,
                  'orders/order_form.html',
                  {'form': form,
                   'formset': formset,
                   'is_create': False})
