import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wtnt.settings")
os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")  # WINDOWS에서 돌리기 위한 설정
app = Celery("wtnt")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "delete-view-history-per-day": {"task": "team.tasks.delete_view_history", "schedule": crontab(minute=0, hour=0)},
    "update-view-count-per-5-minutes": {"task": "team.tasks.update_view_count", "schedule": crontab(minute="*/5")},
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
