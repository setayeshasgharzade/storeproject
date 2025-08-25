from store.signals import order_created
from django.dispatch import receiver

@receiver(order_created)
def on_created_order(sender , **kwargs):
     print(kwargs['order'])
