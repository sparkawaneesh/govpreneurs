import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "govpreneurs_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["workers.ingestion_tasks"]
)

# Optional configuration
app.conf.update(
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
)

# Periodic Task Schedule
app.conf.beat_schedule = {
    "ingest-opportunities-every-30-minutes": {
        "task": "workers.ingestion_tasks.ingest_opportunities_task",
        "schedule": crontab(minute="*/30"),
    },
}

if __name__ == "__main__":
    app.start()
