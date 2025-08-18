from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection,Review , Cart , CartItem, Customer,Order,OrderItem
from django.db.models import Sum, Avg, Count, Max, Min



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
       model = Product
       fields= ['id','title','slug','inventory','price','price_with_tax','collection']
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
        self.instance=CartItem.objects.create(cart_id = id, **self.validated_data)

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
      fields = ['id','title','quantity','price','product']      


class OrderSerializer(serializers.ModelSerializer):
   items = OrderItemSerializer(many=True)
   class Meta:
      model = Order
      fields= ['id', 'payment','placed_at','items']
   
