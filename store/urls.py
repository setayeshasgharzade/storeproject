from. import views
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router= routers.DefaultRouter()
# router = DefaultRouter()
router.register('products', views.ProductModelView , basename='products')
router.register('collections', views.CollectionModelView)
router.register('reviews',views.ReviewModelViewSet)
router.register('carts',views.CartModelViewSet)
router.register('customers',views.CustomerModelViewSet)
router.register('orders',views.orderModelViewSet, basename='orders')


produt_reviews = routers.NestedDefaultRouter(router,'products', lookup='product')
produt_reviews.register('reviews',views.ReviewModelViewSet, basename='produt-reviews')

cart_items= routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_items.register('items', views.CartItemModelViewSet, basename='cart-items')

# order_items = routers.NestedDefaultRouter(router,'orders', lookup='order')
# order_items.register('orders' , views.orderModelViewSet , basename='order_items')

urlpatterns =router.urls + produt_reviews.urls + cart_items.urls
# urlpatterns = [
#     path('product/', views.ProductList.as_view()),
#     path('product/<int:pk>/' , views.ProductDetails.as_view()),
#     # path('collection/<int:pk>/' , views.collection_Details , name='collection-details'),
#     path('collection/' , views.CollectionList.as_view()),
#     path('collection/<int:pk>/' , views.CollectionDetails.as_view()),
# ]
