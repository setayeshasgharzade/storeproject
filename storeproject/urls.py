from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('', include('store_custom.urls')),
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/jwt/', include('djoser.urls.jwt')),
]