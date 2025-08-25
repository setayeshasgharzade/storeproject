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

# products => the address of the parent route and lookup=> id of the parent route 
produt_router = routers.NestedDefaultRouter(router,'products', lookup='product')
produt_router.register('reviews',views.ReviewModelViewSet, basename='produt-reviews')
# images=> the address of the child route and basename= when you wanna use this route somewhere else for example in a template you gotta use the basename which is products-images-... now if you wanna get anything from this router, that specific part uses the basename then after - that part completes it acording to the thing you're lokking for.
produt_router.register('images', views.ProductImagesModelViewSet , basename='products-images')

cart_items= routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_items.register('items', views.CartItemModelViewSet, basename='cart-items')

urlpatterns =router.urls + produt_router.urls + cart_items.urls
# urlpatterns = [
#     path('product/', views.ProductList.as_view()),
#     path('product/<int:pk>/' , views.ProductDetails.as_view()),
#     # path('collection/<int:pk>/' , views.collection_Details , name='collection-details'),
#     path('collection/' , views.CollectionList.as_view()),
#     path('collection/<int:pk>/' , views.CollectionDetails.as_view()),
# ]
