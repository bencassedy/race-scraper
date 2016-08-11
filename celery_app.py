from __future__ import absolute_import
from celery import Celery


celery = Celery('celery_app')

# configure celery
celery.conf.update(
    CELERY_RESULT_SERIALIZER='json',
    broker='amqp://',
    backend='amqp://',
    include=['sources.tr_mag']
)

if __name__ == '__main__':
    celery.start()

