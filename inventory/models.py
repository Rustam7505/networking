from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel
from products.models import Product


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Inventory(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_records')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_received = models.PositiveIntegerField()
    date_received = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Inventory for {self.product.name} - {self.date_received}"

    def save(self, *args, **kwargs):
        # Check if this is a new record
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Update product stock quantity only for new records
        if is_new:
            self.product.stock_quantity += self.quantity_received
            self.product.save()

    class Meta:
        verbose_name_plural = "Inventories"
class InventoryHistory(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    change    = models.DecimalField(max_digits=10, decimal_places=2)
    note      = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']
