from django.contrib import admin, messages
from . import models
from django.db.models import Count
from django.utils.html import format_html
from urllib.parse import urlencode 
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericTabularInline
from tag.models import TaggedItem
from .models import ProductImage

class inventory_management(admin.SimpleListFilter):
    title='inventory'
    parameter_name='inventory'

    def lookups(self, request, model_admin):
        return[
            ('<20','Low'), ('>20', 'OK') ]
    
    def queryset(self, request, queryset):
        if self.value() == '<20':
            return queryset.filter(inventory__lt=20)
        return queryset.filter(inventory__gt=20)


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    list_per_page = 10
    search_fields=['title']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            })
        )
        return format_html('<a href="{}">{}</a>', url, collection.product_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    readonly_fields=['thumbnails'] # you need to add the inline to the ProductAdmin class as well 

    def thumbnails(self,instane):
        if instane.image.name != "":
            return format_html(f'<img src="{instane.image.url}" class="thumbnail">') # to see how it actually works croll down to   class Media 
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions=['clear_inventory']
    inlines=[ProductImageInline] # to see how we complete it check out store_custom.admin 
    list_display = ['title', 'price', 'inventory_status', 'collection_title']
    list_per_page = 10
    search_fields=['title']
    autocomplete_fields=['collection']
    prepopulated_fields={
        'slug':['title']
    }

    list_editable = ['price']
    list_select_related = ['collection']
    list_filter=['collection','last_update',inventory_management]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory > 20:
            return 'OK'
        return 'Low'
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
     updated_count = queryset.update(inventory=0)
     self.message_user(
        request,
        f'{updated_count} products were updated successfully',
        messages.ERROR
      )
    class Media: #to see how it actually works check out store.static.style.css
        css={
            'all':['style.css']
        }
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id','first_name', 'last_name', 'membership', 'customer_order_count']
    list_per_page = 10
    search_fields=['first_name','user__last_name']
    list_editable = ['membership']
    list_select_related=['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields=['first_name__istartswith','last_name__istartswith']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_count=Count('order')
        )

    def customer_order_count(self, customer):
        url = (
            reverse('admin:store_orderitem_changelist')  
            + '?'
            + urlencode({
                'order__customer__id': str(customer.id)  
            })
        )
        return format_html('<a href="{}">{}</a>', url, customer.order_count)

class Orderitem_inline(admin.TabularInline):
    model= models.OrderItem
    autocomplete_fields=['product']
    extra = 1

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'placed_at', 'payment']
    autocomplete_fields=['customer']
    list_per_page = 10
    inlines=[Orderitem_inline]
    list_editable = ['payment']
    list_select_related = ['customer']


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'order']
    list_per_page = 10



    list_filter = ['order__customer']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        customer_id = request.GET.get('order__customer__id')
        if customer_id:
            queryset = queryset.filter(order__customer__id=customer_id)
        return queryset