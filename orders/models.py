from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel
from customers.models import Customer
from products.models import Product


class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, default='cash')
    shipping_address = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
            else:
                last_id = 0
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{last_id + 1:04d}"

        # Calculate total amount
        if not self.pk:  # Only for new orders
            super().save(*args, **kwargs)  # Save first to create the order
            self.calculate_total()
            kwargs['force_update'] = True
            super().save(*args, **kwargs)  # Save again with the calculated total
        else:
            self.calculate_total()
            super().save(*args, **kwargs)

    def calculate_total(self):
        items_total = sum(item.subtotal for item in self.items.all())
        self.total_amount = items_total + self.shipping_cost + self.tax - self.discount
        return self.total_amount


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.order_number}"

    @property
    def subtotal(self):
        return (self.price * self.quantity) - self.discount

    def save(self, *args, **kwargs):
        # Set price from product if not provided
        if not self.price and self.product:
            self.price = self.product.price

        super().save(*args, **kwargs)

        # Update order total
        self.order.calculate_total()
        self.order.save()
