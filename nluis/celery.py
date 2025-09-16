import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nluis.settings')

# app = Celery('nluis')
app = Celery('nluis', backend='amqp', broker='amqp://guest@localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
