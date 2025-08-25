from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer
 
# #  check out store.apps and store_custom.serializers
# @receiver(post_save , sender=settings.AUTH_USER_MODEL)
# def create_customer_for_user(sender,**kwargs):
#     if kwargs['created']:  #=> kwargs['created'] this passes a boolean variable 
#         Customer.objects.create(user=kwargs['instance'])

def create_customer_for_user(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)