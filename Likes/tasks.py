# from storeproject.celery import celery
#both get the same job done, the difference is that with storeproject.celery you can can only use the braker in one app but if you use the other you can use it everywhere it is more flexible
from celery import shared_task
from time import sleep

@shared_task
def notify_customer(message):
    print('100 messages are about to be sent...')
    print(message)
    sleep(10)
    print('emails were sent successfuly!')