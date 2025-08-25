from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection, ProductImage,Review , Cart , CartItem, Customer,Order,OrderItem
from django.db.models import Sum, Avg, Count, Max, Min
from django.db import transaction
from .signals import order_created
from .validators import validate_image_size
from rest_framework import validators


class ProductImagesSerializer(serializers.ModelSerializer):
   def create(self, validated_data):
      product_id = self.context['product_pk']
      return ProductImage.objects.create(product_id=product_id,**validated_data)

   class Meta:
      model = ProductImage
      fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True, read_only=True)
    class Meta:
       model = Product
       fields= ['id','title','slug','inventory','price','price_with_tax','collection','images']
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')
    collection=serializers.PrimaryKeyRelatedField(
       queryset=Collection.objects.all()
    )
    # collection = serializers.HyperlinkedRelatedField(
    # queryset= Collection.objects.all(),
    # view_name= 'collection-details'
        # )
    def calculate_tax(self, product: Product):
     return product.price * Decimal(1.1)


class Collectionserializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

class Reviewserializer(serializers.ModelSerializer):
    class Meta:
       model = Review
       fields = ['id','name','date', 'description']

    def create(self, validated_data):
       productid= self.context['product_pk']
       return Review.objects.create(product_id=productid,**validated_data)      
    
class SimpleProductSerializer(serializers.ModelSerializer):
   class Meta:
    model = Product
    fields = ['title','price']

class CartItemSerializer(serializers.ModelSerializer):
   product = SimpleProductSerializer()
   total_price= serializers.SerializerMethodField()
   def get_total_price(self,cartitem:CartItem):
      return cartitem.quantity * cartitem.product.price

   class Meta:
      model = CartItem
      fields = ['id','quantity','product','total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, cart: Cart):
        return sum(item.quantity * item.product.price for item in cart.items.all())
    

class AddItemserializer(serializers.ModelSerializer):
   product_id=serializers.IntegerField()

   def validate_product_id(self, value):
      if not Product.objects.filter(pk=value).exists():
        raise serializers.ValidationError('there is not such an id')
      return value
   def save(self, **kwargs):
      cart_id = self.context['cart_id']
      product_id = self.validated_data['product_id']
      quantity = self.validated_data['quantity']

      try:
        cart_item=CartItem.objects.get( cart_id= cart_id,product_id=product_id)
        cart_item.quantity = cart_item.quantity + quantity
        cart_item.save()
        self.instance=cart_item
      except CartItem.DoesNotExist:
        self.instance=CartItem.objects.create(cart_id = cart_id, **self.validated_data)

      return self.instance
      
   class Meta:
      model = CartItem
      fields = ['id','product_id','quantity']

class UpdateItemSerializer(serializers.ModelSerializer):
   class Meta:
      model = CartItem
      fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
   user_id = serializers.IntegerField()
   class Meta:
      model= Customer
      fields = ['id', 'user_id','membership','birth_date','phone']

class CustomerSerializerGETandCREATE(serializers.ModelSerializer):
   user_id = serializers.IntegerField(read_only=True)
   class Meta:
      model= Customer
      fields = ['id', 'user_id','membership','birth_date','phone']

class OrderItemSerializer(serializers.ModelSerializer):
   product = SimpleProductSerializer()
   class Meta:
      model = OrderItem
      fields = ['id','quantity','price','product']      


class OrderSerializer(serializers.ModelSerializer):
   items = OrderItemSerializer(many=True)
   class Meta:
      model = Order
      fields= ['id', 'payment','placed_at','items']



class AddOrderSerializer(serializers.Serializer):
      cart_id = serializers.UUIDField()

      def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        elif CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('This cart is empty.')
        return cart_id
      
      def save(self, **kwargs):
        with transaction.atomic():
         user_id=self.context['user_id']
         (customer , created) = Customer.objects.get_or_create(user_id = user_id)
         order=Order.objects.create(customer=customer)
         cart_id=self.validated_data['cart_id']
         cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
         order_items= [
            OrderItem(
               order=order,
               quantity = item.quantity,
               price=item.product.price,
               product= item.product,
            ) for item in cart_items
            ]

         OrderItem.objects.bulk_create(order_items)
         cart= Cart.objects.filter(pk=cart_id).delete()
         
         # difference between send and send_robust= if you use send and by any chance you recieve an error from one of the functions, your error will be ignored but if you use send_robust your error will be shown 
         # this was the second step and move to the store_cusom.signals.handler to check out the third step 
         order_created.send_robust(self.__class__,order=order)
         return (order)

