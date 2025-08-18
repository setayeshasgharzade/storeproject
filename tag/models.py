from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class TaggedItemManager(models.Manager):
    def get_tags_id(self,object_type,tag_id):
        content_type= ContentType.objects.get_for_model(object_type)
        return TaggedItem.objects.filter(
        content_type=content_type , tag_id = tag_id
    )      

class Tags(models.Model):
    label = models.CharField(max_length=255)
    def __str__(self):
        return self.label

class TaggedItem(models.Model): 
    objects=TaggedItemManager() 
    tag=models.ForeignKey(Tags, on_delete=models.CASCADE)
    content_type=models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type','object_id')

    def __str__(self):
        return self.objects

  