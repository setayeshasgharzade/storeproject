from django_filters.rest_framework import FilterSet
from .models import Product,Collection

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields={
            'collection_id':['exact'],
            'price' : ['gt','lt']
        }


