from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed the database with initial data.'

    def handle(self, *args, **kwargs):
        # Create Customers
        alice = Customer.objects.create(name='Alice', email='alice@example.com', phone='+1234567890')
        bob = Customer.objects.create(name='Bob', email='bob@example.com', phone='123-456-7890')
        carol = Customer.objects.create(name='Carol', email='carol@example.com')

        # Create Products
        laptop = Product.objects.create(name='Laptop', price=999.99, stock=10)
        phone = Product.objects.create(name='Phone', price=499.99, stock=20)

        # Create Orders
        order1 = Order.objects.create(customer=alice, total_amount=laptop.price + phone.price, order_date=timezone.now())
        order1.products.set([laptop, phone])
        self.stdout.write(self.style.SUCCESS('Database seeded!'))
