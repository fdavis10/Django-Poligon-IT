import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poligon_it.settings')

app = Celery('poligon_it')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    worker_pool='solo'
)
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()




@app.task(bind=True)
def debug_task(self):
    print(f'REQUEST: {self.request!r}')

@app.on_after_configure.connect
def show_registered_tasks(sender, **kwargs):
    print('Зарегистрированные задачи:')
    print(app.tasks.keys())