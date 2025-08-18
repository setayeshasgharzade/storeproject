from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.conf import settings


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Collection(models.Model):
    title= models.CharField(max_length=255)
    product_features = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
    
  
class Product(models.Model):
    title= models.CharField(max_length=255)
    slug = models.SlugField()  
    description= models.TextField(null=True, blank=True)
    price=models.DecimalField(max_digits=6, decimal_places=2,validators=[MinValueValidator(1)])
    inventory= models.IntegerField()
    last_update= models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT,related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering= ['title']
        # here we define a new permission which we can add throughout the admin pannel: 
        # for the rest of the parts check out store.view.CustomerViewSet.history and 
        # store.permissions.CustomerViewHistoryPermission
        permissions=[
            ('view history' , 'can view history')
        ]

class Customer(models.Model):
    MEMBERSHIP_B = 'B'
    MEMBERSHIP_G = 'G'
    MEMBERSHIP_S = 'S'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_G, 'Gold'),
        (MEMBERSHIP_B, 'Bronze'),
        (MEMBERSHIP_S, 'Silver'),
    ]
    phone = models.CharField(max_length=11, unique=True)
    birth_date = models.DateField(null=True)
    membership = models.CharField(choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_B, max_length=1)
    user= models.OneToOneField(settings.AUTH_USER_MODEL , on_delete=models.CASCADE )

# TODO - staff role & log service = prometheus - grafana(monitoring)
    def first_name(self):
        return self.user.first_name
    def last_name(self):
        return self.user.last_name
       
    def __str__(self):
        return f'{self.user.last_name} {self.user.last_name}'
    
    class Meta:
        db_table = 'store_customers'
        ordering=['user__first_name' , 'user__last_name']
       # indexes = [models.Index(fields=['last_name', 'first_name'])]


class Order(models.Model):
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_FAILED, 'Failed'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_PENDING, 'Pending'), 
    ]
    payment = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT,null=True)

    def __str__(self):
        return self.payment
    
    class Meta:
        ordering=['payment']
    

class Address(models.Model):
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)

class OrderItem(models.Model):
    title= models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orderitems')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])

class Cart(models.Model):
    id = models.UUIDField(primary_key=True , default=uuid4)
    created_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , related_name='items')
    quantity = models.SmallIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productsincart')

    class Meta:
        unique_together = [['cart', 'product']]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE , related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.CharField()
    date = models.DateTimeField(auto_now_add=True)