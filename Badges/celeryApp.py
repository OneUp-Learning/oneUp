from celery import Celery
from celery.signals import after_setup_task_logger, after_setup_logger
from django.conf import settings
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import DjangoLogstashFormatter


def initialize_logstash(logger=None, loglevel=logging.DEBUG, **kwargs):
    handler = AsynchronousLogstashHandler(
        host=settings.LOGSTASH_HOST,
        port=settings.LOGSTASH_PORT,
        database_path=None,
    )
    handler.setLevel(loglevel)
    formatter = DjangoLogstashFormatter(
        message_type='Celery',
        extra={
            'application': 'celery',
            'environment': 'dev'
        }
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


after_setup_task_logger.connect(initialize_logstash)
after_setup_logger.connect(initialize_logstash)

app = Celery('Badges',broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')