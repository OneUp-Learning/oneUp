from celery import Celery

app = Celery('Badges',broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')