# fake_data.py

import os
import django
from faker import Faker
from random import choice, randint, uniform
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

# Django sozlamalarini yuklash
# 'myproject' ni O'Z LOYIHANGIZ NOMI BILAN ALMASHTIRING!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clothing_crm.settings')
django.setup()

# Modellar import qilinadi
# Ilovangiz nomlari va modellar to'g'ri import qilinganligiga ishonch hosil qiling
from customers.models import Customer
from products.models import Category, Product
from inventory.models import Supplier, Inventory, InventoryHistory
from orders.models import Order, OrderItem

# Faker obyektini 'uz_UZ' lokali bilan yaratish
fake = Faker('uz_UZ')


def create_fake_data(num_records=10):
    print(f"{num_records} ta soxta yozuv yaratilmoqda...")

    # --- Categories (Kategoriyalar) ---
    print("Kategoriyalar yaratilmoqda...")
    categories = []
    # O'zbekchaga mos kategoriya nomlari
    uz_categories = [
        "Elektronika", "Kiyim-kechak", "Oyoq kiyimlar", "Maishiy texnika",
        "Kitoblar", "O'yinchoqlar", "Oziq-ovqat", "Salomatlik",
        "Sport anjomlari", "Zargarlik buyumlari"
    ]
    for i in range(min(num_records // 2, len(uz_categories))):  # 5-10 ta kategoriya
        category = Category.objects.create(
            name=uz_categories[i],
            description=fake.text(max_nb_chars=100)
        )
        categories.append(category)
    print(f"{len(categories)} ta kategoriya yaratildi.")

    # --- Products (Mahsulotlar) ---
    print("Mahsulotlar yaratilmoqda...")
    products = []
    SIZE_CHOICES_FLAT = [choice_tuple[0] for choice_tuple in Product.SIZE_CHOICES]
    GENDER_CHOICES_FLAT = [choice_tuple[0] for choice_tuple in Product.GENDER_CHOICES]

    for _ in range(num_records):
        product = Product.objects.create(
            name=fake.ecommerce_name(),  # O'zbekcha mahsulot nomi yo'q, shuning uchun Fakerning mavjudidan foydalanildi
            category=choice(categories),
            description=fake.text(max_nb_chars=200),
            price=Decimal(uniform(10_000.00, 10_000_000.00)).quantize(Decimal('0.01')),  # So'mda narxlar
            cost_price=Decimal(uniform(5_000.00, 8_000_000.00)).quantize(Decimal('0.01')),  # So'mda narxlar
            size=choice(SIZE_CHOICES_FLAT),
            gender=choice(GENDER_CHOICES_FLAT),
            color=fake.color_name(),  # Rang nomlari inglizcha
            stock_quantity=randint(0, 200),
            is_active=fake.boolean(chance_of_getting_true=90)
        )
        products.append(product)
    print(f"{len(products)} ta mahsulot yaratildi.")

    # --- Customers (Mijozlar) ---
    print("Mijozlar yaratilmoqda...")
    customers = []
    STATUS_CHOICES_FLAT = [choice_tuple[0] for choice_tuple in Customer.STATUS_CHOICES]

    for _ in range(num_records):
        customer = Customer.objects.create(
            name=fake.name(),  # O'zbekcha ismlar uchun
            email=fake.unique.email(),
            phone=fake.phone_number()[:20],  # O'zbekcha telefon raqamlari
            address=fake.address(),  # O'zbekcha manzillar
            status=choice(STATUS_CHOICES_FLAT),
            notes=fake.text(max_nb_chars=150)
        )
        customers.append(customer)
    print(f"{len(customers)} ta mijoz yaratildi.")

    # --- Suppliers (Yetkazib beruvchilar) ---
    print("Yetkazib beruvchilar yaratilmoqda...")
    suppliers = []
    for _ in range(num_records // 2):  # 5 ta yetkazib beruvchi
        supplier = Supplier.objects.create(
            name=fake.company(),  # O'zbekcha kompaniya nomlari
            contact_person=fake.name(),
            email=fake.unique.company_email(),
            phone=fake.phone_number()[:20],
            address=fake.address(),
            notes=fake.text(max_nb_chars=150)
        )
        suppliers.append(supplier)
    print(f"{len(suppliers)} ta yetkazib beruvchi yaratildi.")

    # --- Inventory (Inventar) ---
    print("Inventar yozuvlari yaratilmoqda...")
    inventories = []
    for _ in range(num_records):
        inventory_record = Inventory.objects.create(
            product=choice(products),
            supplier=choice(suppliers),
            quantity_received=randint(10, 200),
            date_received=fake.date_time_between(start_date='-6M', end_date='now', tzinfo=timezone.utc),
            invoice_number=f"INV-{fake.bothify(text='######')}",  # Oddiyroq invoice number
            notes=fake.text(max_nb_chars=100)
        )
        inventories.append(inventory_record)
    print(f"{len(inventories)} ta inventar yozuvi yaratildi. Izoh: Mahsulot zaxira miqdorlari avtomatik yangilanadi.")

    # --- Orders (Buyurtmalar) ---
    print("Buyurtmalar va Buyurtma Mahsulotlari yaratilmoqda...")
    orders = []
    PAYMENT_METHOD_CHOICES_FLAT = [choice_tuple[0] for choice_tuple in Order.PAYMENT_METHOD_CHOICES]
    STATUS_CHOICES_ORDER_FLAT = [choice_tuple[0] for choice_tuple in Order.STATUS_CHOICES]

    for _ in range(num_records):
        # Buyurtmani yaratish
        order = Order.objects.create(
            customer=choice(customers),
            status=choice(STATUS_CHOICES_ORDER_FLAT),
            payment_method=choice(PAYMENT_METHOD_CHOICES_FLAT),
            shipping_address=fake.address(),
            discount=Decimal(uniform(0.00, 50000.00)).quantize(Decimal('0.01')),  # So'mda chegirma
            tax=Decimal(uniform(0.00, 20000.00)).quantize(Decimal('0.01')),  # So'mda soliq
            shipping_cost=Decimal(uniform(5000.00, 30000.00)).quantize(Decimal('0.01')),  # So'mda yetkazib berish narxi
            notes=fake.text(max_nb_chars=150)
        )
        orders.append(order)

        # Buyurtma mahsulotlarini qo'shish
        num_items = randint(1, 3)  # Har bir buyurtmada 1 dan 3 tagacha mahsulot
        for _ in range(num_items):
            product_for_item = choice(products)
            quantity = randint(1, 5)

            # Mahsulot narxini OrderItem ga kiritish
            OrderItem.objects.create(
                order=order,
                product=product_for_item,
                quantity=quantity,
                price=product_for_item.price,  # Hozirgi mahsulot narxi
                discount=Decimal(uniform(0.00, 5000.00)).quantize(Decimal('0.01'))  # So'mda chegirma
            )

            # Buyurtma berilganda mahsulot miqdorini kamaytirish va tarixini yozish
            if product_for_item.stock_quantity >= quantity:
                product_for_item.stock_quantity -= quantity
                product_for_item.save()
                InventoryHistory.objects.create(
                    product=product_for_item,
                    change=Decimal(-quantity),  # O'zgarish salbiy bo'ladi
                    note=f"Buyurtma #{order.order_number} {order.customer.name} uchun"
                )
            else:
                print(
                    f"Ogohlantirish: {product_for_item.name} uchun yetarli zaxira yo'q. Zaxira: {product_for_item.stock_quantity}, Buyurtma qilingan: {quantity}")

    print(f"{len(orders)} ta buyurtma va unga bog'liq buyurtma mahsulotlari yaratildi.")

    print("Soxta ma'lumotlarni yaratish yakunlandi!")


if __name__ == '__main__':
    # O'zingiz xohlagan miqdorda yozuvlarni yaratish uchun num_records ni o'zgartiring
    create_fake_data(num_records=10)