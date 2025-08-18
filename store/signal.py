from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

@receiver(post_save, sender=Customer)
def create_user_for_customer(sender, instance, created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(
            username=f'customer_{instance.id}',
            email=f'customer_{instance.id}@example.com',
            password='defaultpassword123'
        )
        instance.user = user
        instance.save()