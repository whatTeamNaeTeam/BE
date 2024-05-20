import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wtnt.settings")
os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")  # WINDOWS에서 돌리기 위한 설정
app = Celery("wtnt")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
