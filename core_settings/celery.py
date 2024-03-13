import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_settings.settings')

app = Celery('core_settings')
app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle'],
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
