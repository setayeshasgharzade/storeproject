from django.contrib import admin
from tag.models import Tags,TaggedItem
from . import models

@admin.register(models.Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display=['label']
    search_fields=['tag']
    

@admin.register(models.TaggedItem)
class TaggedItem(admin.ModelAdmin):
    list_display=['objects']
