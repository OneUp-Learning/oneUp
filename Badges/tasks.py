from celery import Celery

app = Celery('Badges',broker='amqp://localhost')

@app.task
def register_event_offline(eventID, request, student, objectId):
    from Badges.events import register_event_actual
    register_event_actual(eventID, request, student, objectId)

