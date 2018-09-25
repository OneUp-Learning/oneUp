from celery import Celery

app = Celery('Badges',broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')
@app.task
def register_event_offline(eventID, request, student, objectId):
    from Badges.events import register_event_actual
    return register_event_actual(eventID, request, student, objectId)

