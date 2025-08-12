import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from decimal import Decimal
from django.utils import timezone

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

class Query(graphene.ObjectType):
    hello = graphene.String()

    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(graphene.String))

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

# Input types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True
        pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
        return re.match(pattern, phone)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        try:
            validate_email(input.email)
        except DjangoValidationError:
            errors.append("Invalid email format.")
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists.")
        if not cls.validate_phone(input.phone):
            errors.append("Invalid phone format.")
        if errors:
            return CreateCustomer(customer=None, message=None, errors=errors)
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone or None
        )
        return CreateCustomer(customer=customer, message="Customer created successfully!", errors=None)

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        customers = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(input):
                entry_errors = []
                try:
                    validate_email(data.email)
                except DjangoValidationError:
                    entry_errors.append(f"Row {idx+1}: Invalid email format.")
                if Customer.objects.filter(email=data.email).exists():
                    entry_errors.append(f"Row {idx+1}: Email already exists.")
                if not CreateCustomer.validate_phone(data.phone):
                    entry_errors.append(f"Row {idx+1}: Invalid phone format.")
                if entry_errors:
                    errors.extend(entry_errors)
                    continue
                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone or None
                )
                customers.append(customer)
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        if input.price is None or Decimal(input.price) <= 0:
            errors.append("Price must be positive.")
        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative.")
        if errors:
            return CreateProduct(product=None, errors=errors)
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock if input.stock is not None else 0
        )
        return CreateProduct(product=product, errors=None)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)
        if not input.product_ids or len(input.product_ids) == 0:
            errors.append("At least one product must be selected.")
            return CreateOrder(order=None, errors=errors)
        products = []
        for pid in input.product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
            except Product.DoesNotExist:
                errors.append(f"Invalid product ID: {pid}")
        if errors:
            return CreateOrder(order=None, errors=errors)
        total_amount = sum([p.price for p in products])
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)
        return CreateOrder(order=order, errors=None)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
