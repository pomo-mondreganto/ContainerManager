from celery import Celery

import config

app = Celery(
    __name__,
    broker=config.get_celery_config().broker_url,
    backend=config.get_celery_config().backend_url,
    worker_prefetch_multiplier=1,
    include=[
        'celery_manager.tasks',
    ],
)
