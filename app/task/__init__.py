from celery import Celery

celery = Celery('', include=['app.task.tasks'])
celery.config_from_object('app.task.celery_config')

if __name__ == '__main__':
    celery.start()