from .celery import app as celery_app
# now celery can easily find this module
__all__ = ('celery_app',)