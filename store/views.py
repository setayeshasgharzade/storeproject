import time
from django.db import connection
from django.http import HttpResponse
from store.models import Product,OrderItem,Customer,Collection,Order
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.db.models import Q,F,Count,Sum,Avg,Min,Max,ExpressionWrapper,DateTimeField
from django.db.models.functions import Concat
from django.db.models import Func,F,Value
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from .models import Product, Collection, ProductImage,Review ,Cart ,CartItem
from .serializer import AddOrderSerializer, ProductSerializer,Collectionserializer,Reviewserializer ,\
CartSerializer,CartItemSerializer,AddItemserializer,UpdateItemSerializer,\
CustomerSerializer,CustomerSerializerGETandCREATE,OrderSerializer,ProductImagesSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.permissions import  IsAdminUser,IsAuthenticated,AllowAny,BasePermission
from rest_framework.mixins import CreateModelMixin ,RetrieveModelMixin,\
DestroyModelMixin,ListModelMixin,UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.filters import SearchFilter,OrderingFilter
from .pagination import PaginaionNumber
ObjectDoesNotExist
from rest_framework.decorators import action
from store.permissions import IsAdminOrReadonly, ViewCustomerHistoryPermission
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model,authenticate
from django.core.mail import send_mail,BadHeaderError,mail_admins,EmailMessage
from django.core.cache import cache
from django.views.decorators.cache import cache_page #for caching a function 
from django.utils.decorators import method_decorator #for caching a class 

class ProductModelView(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('images').all()
    def get_queryset(self):
          key = 'product_list_cache'
         #  one of the parameters that we need setting cache is label. and we save the label under the name of product_name_cache
          cached_queryset = cache.get(key)
          if cached_queryset is None: 
            # now you're checkingif you have such a label from before and if you don't have it you make it.
            time.sleep(2)  # شبیه سازی تاخیر
            queryset = Product.objects.prefetch_related('images').all() #you determine the data you wanna set in cache
            ids = list(queryset.values_list('id', flat=True)) # now we have too much data here so we are gonna save the IDs only.
            cache.set(key, ids, timeout=60* 5) # to set sthh in cache we need three parameters: 1.label 2.data(here we set the IDs only) 3.the amount of time you wanna keep data in cache
            return queryset
          else:
            # if we have the label in cache already then we need to set a filter just to read it from the memory
            return Product.objects.filter(id__in=cached_queryset).prefetch_related('images')
   #  try:
   #     send_mail('Products','Products were shown','set@gmail.com',['stranger@gmail.com'])
   #    # message= EmailMessage('Products','Products were shown','set@gmail.com',['stranger@gmail.com'])
   #    # message.attach('store/static/')
   #  except BadHeaderError:
   #     pass  #this is a fake SMTP and you can use the real one if you pay. so far we have the procedure of excecuting SMTP4dev to see the complete part check out the setting as well
    filter_backends=[DjangoFilterBackend , SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class=PaginaionNumber
    search_fields=['title','description']
    ordering_fields = ['last_update','price']
    permission_classes=[IsAdminOrReadonly]


    def get_serializer_context(self):
        return {'request': self.request}
        
    # def get_queryset(self):
    #    queryset = Product.objects.all()
    #    collection_id = self.request.query_params.get('collection_id')
    #    if collection_id is not None:
    #       queryset = queryset.filter(collection_id=collection_id)
    #    return queryset

    
    def destroy(self, request, *args, **kwargs):
      if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
      return super().destroy(request, *args, **kwargs)



#   def get(self,request):
#      queryset = Product.objects.select_related('collection').all()
#      serializer = ProductSerializer(queryset , many= True , context={'request': request}) 
#      return Response(serializer.data)
#   def post(self,request):
#        serializer= ProductSerializer(data= request.data)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#     #   print(serializer.validated_data)
#        return Response('ok', status.HTTP_201_CREATED)

#   def get(self,request,id):
#       product = get_object_or_404(Product , pk = id)
#       serializer = ProductSerializer(product)
#       return Response(serializer.data)
#   def put(self,request,id):
#         product = get_object_or_404(Product , pk = id)
#         serializer= ProductSerializer(product,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

class CollectionModelView(ModelViewSet):
   queryset = Collection.objects.annotate(products_count=Count('products'))
   serializer_class=  Collectionserializer

   def destroy(self, request, *args, **kwargs):
      if Product.objects.filter(kwargs=['pk']).count() > 0:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)  
      return super().destroy(request, *args, **kwargs)
   
#      queryset = Collection.objects.annotate(products_count=Count('products'))
#      serializer= Collectionserializer(queryset , many = True)
#      return Response(serializer.data) 
#    def post(self,request):
#       serializer = Collectionserializer(data=request.data)
#       serializer.is_valid(raise_exception=True)
#       serializer.save()
#       return Response(status=status.HTTP_201_CREATED)
#    def get(self,request,id):
#      collection= get_object_or_404(Collection ,pk=id)
#      serializer= Collectionserializer(collection)
#      return Response(serializer.data)
#    def put(self,request,id):
#      collection= get_object_or_404(Collection ,pk=id)
#      serializers = Collectionserializer(collection, data=request.data)
#      serializers.is_valid(raise_exception=True)
#      serializers.save()
#      return Response(serializers.data)
  
# @method_decorator(cache_page(5*60)) => here we set this whole class in cache
class ReviewModelViewSet(ModelViewSet):
   queryset = Review.objects.none()
   serializer_class = Reviewserializer
   @cache_page(5*60) #here we set this function into a cache 
   def get_queryset(self):
      return Review.objects.filter(product_id = self.kwargs['product_pk'])
  
   def get_serializer_context(self):
      return {'product_pk':self.kwargs['product_pk']}

# @api_view()
# def collection_Details(request, pk):
#     try:
#         collection = Collection.objects.get(pk=pk)
#     except Collection.DoesNotExist:
#         return Response(status=404)

#     return Response({
#         'id': collection.id,
#         'title': collection.title
#     })

class CartModelViewSet(RetrieveModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       GenericViewSet,
                       ListModelMixin):
   queryset = Cart.objects.prefetch_related('items__product').all()
   serializer_class= CartSerializer

class CartItemModelViewSet(ModelViewSet):
   http_method_names=['delete','patch','get','post']
   permission_classes = [AllowAny]

   def get_serializer_class(self):
      if self.request.method=='POST':
         return AddItemserializer
      elif self.request.method=='PATCH':
         return UpdateItemSerializer
      return CartItemSerializer
      
    
   def get_serializer_context(self):
      return {'cart_id': self.kwargs['cart_pk']}
   def get_queryset(self):
       return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])
   
class CustomerModelViewSet(ModelViewSet):
   queryset= Customer.objects.all()
   serializer_class = CustomerSerializer
   permission_classes = [IsAuthenticated]
      

   @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
   def history(self, request, pk):
      return Response('ok')
      
   @action(detail=False, methods=['GET','PUT'], permission_classes=[IsAuthenticated]) #=> here if you set the argument Detail to Falsee then you can get the info as a query otherwise (True)=> then you have to enter a specific id right after customers in the URL
   def me(self,request):
      (customer,created)=Customer.objects.get_or_create(user_id=request.user.id)
      # sth about get_or_create = it creates a record before it does anythimg with it.
      #  and the things it does with the created record is either creating it which is updating it
      #  with the new data you give according to the request and saving it in db or getting and displying
      #  it from db
      if request.method == 'GET':
         serializer = CustomerSerializerGETandCREATE(customer)
         return Response(serializer.data)
      elif request.method == 'PUT':
         serializer= CustomerSerializerGETandCREATE(customer, request.data)
         serializer.is_valid(raise_exception=True)
         serializer.save()
         return Response(serializer.data)
      
class orderModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    http_method_names=['get','patch','head','delete','post']

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


    def get_queryset(self):
      #   user = self.request.user
      #   if user.is_staff:
            return Order.objects.all()
      #   customer = Customer.objects.only('id').get(user_id=user.id)
      #   return Order.objects.filter(customer_id=customer.id)

    def create(self, request, *args, **kwargs):
        serializer = AddOrderSerializer(data=request.data , context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializer_output= OrderSerializer(order, context=self.get_serializer_context())
        return Response(serializer_output.data)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddOrderSerializer
        return OrderSerializer

class ProductImagesModelViewSet(ModelViewSet):
   serializer_class= ProductImagesSerializer

   def get_serializer_context(self):
      return {'product_pk': self.kwargs['product_pk']}

   def get_queryset(self):
      return ProductImage.objects.filter(pk=self.kwargs['product_pk']).all()
       




#    queryset= Product.objects.annotate(best_selling=Sum(
#       F('orderitem__quantity')* F('orderitem__price')
#    )).order_by('-best_selling')[:2]
#   queryset= Customer.objects.annotate(spent_money=Sum                                   
#    ( F('order__orderitem__price')* F('order__orderitem__quantity'))
#     )
# queryset= TaggedItem.objects.get_tags(Customer,2)
    # collection= Collection(pk=31)
    # collection.title = 'games'
    # collection.product_features= None
    # result = collection.save()
    # discounted_price= ExpressionWrapper(
    #     F('price') * 0.8, output_field= DateTimeField()
    #     )
    # queryset =Product.objects.annotate(
    #     discounted_price=discounted_price
    # )
     
# def Showinfo (request):
#     queryset =Customer.objects.annotate(
#         full_name= Concat(
#             ('first_name'),Value(' '),('last_name')
#         )
#     )
    # queryset =Product.objects.filter(collection__id=3).aggregate(totalprice=Avg('price'),Minprice= Min('price'),Maxprice=Max('price'))
#  queryset = Order.objects.filter(customer__id=1).aggregate(countorders= Count('id'))
    # queryset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
# queryset =Product.objects.prefetch_related('promotions').select_related('collection').all()
#  queryset =Product.objects.select_related('collection').all()
# queryset =Product.objects.filter(id__in=OrderItem.objects.values('product__id')) 
# queryset = Product.objects.values('id','title','collection__title')
    # queryset = Product.objects.all()[5:10]
#  queryset = Product.objects.filter(id=1).order_by('price','-title').reverse()
#  queryset = Product.objects.filter(inventory=F('price'))

    # RETRIEVE AN OBJECT 
      # in this case we are not gonna recieve a record instead we're gonna recieve a boolean value 
    # product = Product.objects.filter(pk=0).exists()
   #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////   
    # it's gonna show you NONE in case there isn't a record like this 
  # product = Product.objects.filter(pk=0).first()
      #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # to see if a spicific record exist you can do this: (but this pieces of codes can be a lot and complecated)
    #  try:
    #     existt = Product.objects.get(pk=0)
    #  except ObjectDoesNotExist:
    #         pass
  #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
      #in this part you're gonna see the record with this id. (to see one spicific record you can use GET) 
     #product = Product.objects.get(pk=0)
  #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  # in this p  art you wanna see all the objects(query set) and then you make a loop and store the result in it 
  # query_set = Product.objects.all()
  # for product in query_set:
  #  print(product)
  #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
     #how to work with database when it's so complecated and you can not use objects from ORM:
    #with connection.cursor() as cursing:
     # cursing.execute("UPDATE store_customers SET first_name ='Nima' WHERE id=1")
     # return HttpResponse('new data has been saved') 
    