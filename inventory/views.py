from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Supplier, Inventory
from .forms import SupplierForm, InventoryForm
from products.models import Product


@login_required
def inventory_list(request):
    search = request.GET.get('search', '')
    low_stock = request.GET.get('low_stock', '')

    products = Product.objects.all()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search)
        )

    if low_stock:
        products = products.filter(stock_quantity__lt=10)

    context = {
        'products': products
    }

    return render(request, 'inventory/inventory_list.html', context)


@login_required
def inventory_history(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        inventory_records = Inventory.objects.filter(product=product).order_by('-date_received')
        context = {
            'product': product,
            'inventory_records': inventory_records
        }
        return render(request, 'inventory/inventory_history.html', context)
    else:
        inventory_records = Inventory.objects.all().order_by('-date_received')
        context = {
            'inventory_records': inventory_records
        }
        return render(request, 'inventory/inventory_history_all.html', context)


@login_required
def inventory_add(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save()
            messages.success(request, 'Inventory record added successfully.')
            return redirect('inventory:history', product_id=inventory.product.id)
    else:
        form = InventoryForm()

    context = {
        'form': form,
        'title': 'Add Inventory'
    }

    return render(request, 'inventory/inventory_form.html', context)


@login_required
def supplier_list(request):
    search = request.GET.get('search', '')

    suppliers = Supplier.objects.all()

    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search)
        )

    context = {
        'suppliers': suppliers
    }

    return render(request, 'inventory/supplier_list.html', context)


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    inventory_records = Inventory.objects.filter(supplier=supplier).order_by('-date_received')

    context = {
        'supplier': supplier,
        'inventory_records': inventory_records
    }

    return render(request, 'inventory/supplier_detail.html', context)


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('inventory:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()

    context = {
        'form': form,
        'title': 'Create Supplier'
    }

    return render(request, 'inventory/supplier_form.html', context)


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('inventory:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)

    context = {
        'form': form,
        'supplier': supplier,
        'title': 'Update Supplier'
    }

    return render(request, 'inventory/supplier_form.html', context)


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('inventory:supplier_list')

    return render(request, 'inventory/supplier_confirm_delete.html', {'supplier': supplier})
