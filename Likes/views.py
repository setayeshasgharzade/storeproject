from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .tasks import notify_customer
from django.http import HttpResponse


def NotifyCustomer(request):
    result=notify_customer.delay('Hello')
    return HttpResponse(f'Task ID: {result.id}')
